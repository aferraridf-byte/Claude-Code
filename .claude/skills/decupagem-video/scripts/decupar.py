#!/usr/bin/env python3
"""
Decupagem automática: remove trechos sem fala de um vídeo (pensado para HeyGen).

Uso:
    python decupar.py VIDEO.mp4                  # gera VIDEO_decupado.mp4 ao lado
    python decupar.py VIDEO.mp4 SAIDA.mp4        # saída com nome escolhido
    python decupar.py PASTA/                     # todos os vídeos da pasta -> PASTA/decupados/
    python decupar.py VIDEO.mp4 --dry-run        # só analisa, não corta

Como funciona:
  1. ffmpeg silencedetect mapeia os silêncios do áudio.
  2. Cada silêncio maior que --min-silence é encurtado para --keep-pause
     (metade da pausa fica antes, metade depois), para não haver "pulos" secos
     nem sílabas cortadas.
  3. Os limites dos cortes são alinhados à grade de quadros do vídeo, e o áudio
     é fatiado em blocos de exatamente 1 quadro (asetnsamples). Isso evita que o
     áudio dessincronize ao longo de centenas de cortes.
  4. Recodifica em H.264/AAC e confere se a duração de áudio e vídeo bate.
"""
import argparse
import json
import re
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def probe(path):
    r = run(["ffprobe", "-v", "error", "-print_format", "json",
             "-show_streams", "-show_format", str(path)])
    if r.returncode != 0:
        sys.exit(f"ERRO: ffprobe não conseguiu ler o arquivo:\n{r.stderr}")
    info = json.loads(r.stdout)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    if v is None:
        sys.exit("ERRO: o arquivo não tem faixa de vídeo.")
    if a is None:
        sys.exit("ERRO: o arquivo não tem faixa de áudio — não há fala para detectar.")
    fps = Fraction(v.get("avg_frame_rate") or v["r_frame_rate"])
    if fps == 0:
        fps = Fraction(v["r_frame_rate"])
    return {
        "duration": float(info["format"]["duration"]),
        "fps": fps,
        "width": v.get("width"),
        "height": v.get("height"),
        "sample_rate": int(a.get("sample_rate", 48000)),
    }


def detect_silences(path, noise_db, min_silence, duration):
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vn",
             "-af", f"silencedetect=noise={noise_db}dB:d={min_silence}",
             "-f", "null", "-"])
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", r.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    sil = []
    for i, s in enumerate(starts):
        e = ends[i] if i < len(ends) else duration  # silêncio até o fim do arquivo
        sil.append((max(0.0, s), min(e, duration)))
    return sil


def keep_segments(silences, duration, keep_pause, fps):
    """Converte silêncios em trechos a manter, alinhados à grade de quadros."""
    pad = keep_pause / 2
    cuts = []
    for s, e in silences:
        a = 0.0 if s <= 0.05 else s + pad          # silêncio inicial: corta tudo antes da fala
        b = duration if e >= duration - 0.05 else e - pad  # silêncio final: corta tudo depois
        if a == 0.0 and b < duration:
            b = max(0.0, e - pad)                    # deixa um respiro curto antes da 1ª fala
        if b - a > 0.05:
            cuts.append((a, b))

    keep, cur = [], 0.0
    for a, b in cuts:
        if a > cur:
            keep.append((cur, a))
        cur = max(cur, b)
    if cur < duration:
        keep.append((cur, duration))

    # Alinha à grade de quadros (frame k começa em k/fps)
    f = float(fps)
    snapped = []
    for a, b in keep:
        ka, kb = round(a * f), round(b * f)
        if kb - ka >= 1:
            snapped.append((ka, kb))
    # funde trechos que encostaram após o arredondamento
    merged = []
    for ka, kb in snapped:
        if merged and ka <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(kb, merged[-1][1]))
        else:
            merged.append((ka, kb))
    return merged


def build_filter(frames, fps, sample_rate):
    f = float(fps)
    half = 0.5 / f
    terms = [f"gte(t,{ka / f - half:.6f})*lt(t,{kb / f - half:.6f})" for ka, kb in frames]
    expr = "+".join(terms)

    spf = Fraction(sample_rate) / fps  # amostras de áudio por quadro
    if spf.denominator != 1:
        # fps fracionário (ex.: 29,97): reamostra para 48 kHz e aceita erro mínimo
        sample_rate = 48000
        spf = Fraction(48000) / fps
    n = round(float(spf))

    return (
        f"[0:v]select='{expr}',setpts=N/FRAME_RATE/TB[v];\n"
        f"[0:a]aresample={sample_rate},asetnsamples=n={n}:p=0,"
        f"aselect='{expr}',asetpts=N/SR/TB[a]"
    )


VIDEO_EXT = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}


def ffmpeg_major():
    r = run(["ffmpeg", "-version"])
    m = re.search(r"ffmpeg version n?(\d+)", r.stdout)
    return int(m.group(1)) if m else 6


def filter_args(path):
    # ffmpeg 7+ usa "-/filter_complex arquivo"; versões anteriores, -filter_complex_script
    if ffmpeg_major() >= 7:
        return ["-/filter_complex", str(path)]
    return ["-filter_complex_script", str(path)]


def fmt(t):
    m, s = divmod(t, 60)
    return f"{int(m):02d}:{s:05.2f}"


def processar(src, dst, args):
    info = probe(src)
    fps, dur = info["fps"], info["duration"]

    sil = detect_silences(src, args.noise, args.min_silence, dur)
    frames = keep_segments(sil, dur, args.keep_pause, fps)
    f = float(fps)
    kept = sum(kb - ka for ka, kb in frames) / f

    longos = [(s, e) for s, e in sil if e - s >= 3.0 and s > 0.05 and e < dur - 0.05]  # só pausas internas
    rel = {
        "arquivo": src.name,
        "resolucao": f"{info['width']}x{info['height']}",
        "fps": round(f, 3),
        "duracao_original": round(dur, 2),
        "duracao_final_estimada": round(kept, 2),
        "tempo_removido": round(dur - kept, 2),
        "percentual_removido": round(100 * (dur - kept) / dur, 1) if dur else 0,
        "silencios_detectados": len(sil),
        "trechos_mantidos": len(frames),
        "silencios_longos_3s": [{"inicio": fmt(s), "fim": fmt(e), "duracao": round(e - s, 1)}
                                for s, e in longos],
        "parametros": {"noise_db": args.noise, "min_silence": args.min_silence,
                       "keep_pause": args.keep_pause},
    }
    if args.dry_run:
        return rel
    if not frames:
        rel["erro"] = "nenhum trecho com fala encontrado; tente --noise -35"
        return rel

    dst.parent.mkdir(parents=True, exist_ok=True)
    work = dst.with_suffix(".filtro.txt")
    work.write_text(build_filter(frames, fps, info["sample_rate"]), encoding="utf-8")

    t0 = time.time()
    print(f"Processando {src.name} ({fmt(dur)} -> ~{fmt(kept)})...", file=sys.stderr, flush=True)
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src),
           *filter_args(work),
           "-map", "[v]", "-map", "[a]",
           "-c:v", "libx264", "-preset", args.preset, "-crf", str(args.crf),
           "-pix_fmt", "yuv420p", "-r", str(fps),
           "-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart", str(dst)]
    r = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    work.unlink(missing_ok=True)
    if r.returncode != 0:
        rel["erro"] = "ffmpeg falhou: " + r.stderr[-2000:]
        return rel

    out = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", str(dst)])
    st = json.loads(out.stdout)["streams"]
    dv = next(float(s["duration"]) for s in st if s["codec_type"] == "video")
    da = next(float(s["duration"]) for s in st if s["codec_type"] == "audio")
    rel["saida"] = str(dst)
    rel["duracao_final_video"] = round(dv, 2)
    rel["duracao_final_audio"] = round(da, 2)
    rel["diferenca_av_ms"] = round(abs(dv - da) * 1000)
    rel["sincronia_ok"] = abs(dv - da) < 0.15
    rel["tempo_processamento_s"] = round(time.time() - t0, 1)
    rel["tamanho_mb"] = round(dst.stat().st_size / 1e6, 1)
    return rel


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # console do Windows
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada", help="vídeo ou pasta com vídeos")
    ap.add_argument("saida", nargs="?", help="arquivo (ou pasta) de saída")
    ap.add_argument("--noise", type=float, default=-40.0,
                    help="limiar de silêncio em dB (padrão -40; HeyGen é áudio limpo)")
    ap.add_argument("--min-silence", type=float, default=0.6,
                    help="silêncio mínimo, em segundos, para ser cortado (padrão 0,6)")
    ap.add_argument("--keep-pause", type=float, default=0.30,
                    help="pausa que fica no lugar de cada silêncio cortado (padrão 0,30 s)")
    ap.add_argument("--crf", type=int, default=20)
    ap.add_argument("--preset", default="veryfast")
    ap.add_argument("--dry-run", action="store_true", help="só analisa e mostra o relatório")
    ap.add_argument("--report", help="salva o relatório em JSON neste caminho")
    args = ap.parse_args()

    ent = Path(args.entrada).expanduser()
    if not ent.exists():
        sys.exit(f"ERRO: não encontrei {ent}")
    if run(["ffmpeg", "-version"]).returncode != 0:
        sys.exit("ERRO: ffmpeg não está instalado ou não está no PATH.")

    if ent.is_dir():
        destino = Path(args.saida).expanduser() if args.saida else ent / "decupados"
        videos = sorted(p for p in ent.iterdir()
                        if p.suffix.lower() in VIDEO_EXT and not p.stem.endswith("_decupado"))
        if not videos:
            sys.exit(f"ERRO: nenhum vídeo em {ent}")
        rels = [processar(v, destino / f"{v.stem}_decupado.mp4", args) for v in videos]
    else:
        dst = Path(args.saida).expanduser() if args.saida else ent.with_name(f"{ent.stem}_decupado.mp4")
        rels = [processar(ent, dst, args)]

    saida = rels[0] if len(rels) == 1 else rels
    txt = json.dumps(saida, ensure_ascii=False, indent=2)
    if args.report:
        Path(args.report).expanduser().write_text(txt, encoding="utf-8")
    print(txt)
    if any("erro" in r or r.get("sincronia_ok") is False for r in rels):
        sys.exit(1)


if __name__ == "__main__":
    main()
