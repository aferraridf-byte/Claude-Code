#!/usr/bin/env python3
"""
Pipeline HeyGen: roteiro JSON -> vídeo do avatar (API v3) -> download -> decupagem.

Só usa a biblioteca padrão do Python. A chave fica na variável de ambiente
HEYGEN_API_KEY (nunca em arquivo do projeto nem no chat).

Subcomandos:
    verificar                         confere chave, ffmpeg, config e a skill de decupagem
    avatares [--publicos]             lista os looks de avatar (privados por padrão)
    vozes [--idioma Portuguese]       lista vozes (privadas com --privadas)
    configurar --avatar ID ...        grava config.json ao lado deste script
    gerar ROTEIRO.json -p PASTA       envia um vídeo por módulo (não reenvia o que já foi)
    aguardar -p PASTA                 acompanha os vídeos e baixa os prontos
    decupar -p PASTA                  decupa os vídeos baixados (skill decupagem-video)
    status -p PASTA                   mostra o estado do projeto
    produzir ROTEIRO.json -p PASTA    gerar + aguardar + decupar, de uma vez

Formato do roteiro (o mesmo da skill treinamento-heygen):
{
  "curso": "PLD/FTP",
  "modulos": [
    {"n": 1, "titulo": "...",
     "cenas": [{"fala": "...", "tela_titulo": "...", "tela_destaques": ["..."]}]}
  ]
}
Cada módulo vira um vídeo HeyGen do tipo "studio", com uma cena de avatar por cena
do roteiro. Só a "fala" vai para o HeyGen; o texto de tela fica para a edição.

Pastas do projeto:
    PASTA/roteiro.json       cópia do roteiro enviado
    PASTA/estado.json        video_id, status e arquivos de cada módulo
    PASTA/01_heygen/         MP4 baixado do HeyGen
    PASTA/02_decupado/       MP4 sem silêncios, entrada da edição
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

API = os.environ.get("HEYGEN_API_BASE", "https://api.heygen.com").rstrip("/")
AQUI = Path(__file__).resolve().parent
CONFIG = AQUI.parent / "config.json"
MAX_CENAS = 50          # limite do tipo "studio" por requisição
PPM = 140               # palavras por minuto (mesma base do guia de roteiro)

PADRAO = {
    "avatar_id": None,
    "voice_id": None,           # vazio = voz padrão do avatar
    "engine": None,             # "avatar_iii" | "avatar_iv" | "avatar_v"; vazio = padrão do HeyGen
    "velocidade": 1.0,
    "locale": None,             # ex.: "pt-BR", só para vozes com support_locale
    "fundo": None,              # "#RRGGBB" ou URL de imagem; vazio = fundo da gravação do avatar
    "remover_fundo": False,
    "resolucao": "1080p",
    "proporcao": "16:9",
    "brand_glossary_id": None,  # glossário de pronúncia do HeyGen (Coaf, Gafi, PLD...)
    "pasta_projetos": "~/Videos/HeyGen",
}


# ---------------------------------------------------------------- utilidades

def erro(msg, code=1):
    print(f"ERRO: {msg}", file=sys.stderr)
    sys.exit(code)


def log(msg):
    print(f"[{datetime.now():%H:%M:%S}] {msg}", file=sys.stderr, flush=True)


def slug(txt, n=40):
    t = unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode()
    t = re.sub(r"[^A-Za-z0-9]+", "-", t).strip("-")
    return t[:n].rstrip("-") or "video"


def palavras(t):
    return len(re.findall(r"\w+", t))


def mmss(s):
    s = round(s)
    return f"{s // 60}:{s % 60:02d}"


def ler_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def gravar_json(p, dados):
    p = Path(p)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p)


def carregar_config():
    cfg = dict(PADRAO)
    if CONFIG.exists():
        cfg.update({k: v for k, v in ler_json(CONFIG).items() if not k.startswith("_")})
    return cfg


# ---------------------------------------------------------------- API

def chave():
    k = os.environ.get("HEYGEN_API_KEY", "").strip()
    if not k:
        erro("a variável HEYGEN_API_KEY não está definida. Crie a chave em "
             "https://app.heygen.com/developers/api e defina no terminal (veja a skill, seção Configuração).")
    return k


def api(metodo, caminho, corpo=None, consulta=None, tentativas=5):
    url = API + caminho
    if consulta:
        url += "?" + urllib.parse.urlencode({k: v for k, v in consulta.items() if v is not None})
    dados = json.dumps(corpo).encode() if corpo is not None else None
    for i in range(tentativas):
        req = urllib.request.Request(url, data=dados, method=metodo, headers={
            "x-api-key": chave(), "Content-Type": "application/json", "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            txt = e.read().decode("utf-8", "replace")
            if e.code == 429 or e.code >= 500:
                espera = int(e.headers.get("Retry-After") or 0) or min(60, 5 * 2 ** i)
                log(f"HeyGen respondeu {e.code}; nova tentativa em {espera}s")
                time.sleep(espera)
                continue
            try:
                det = json.loads(txt).get("error") or json.loads(txt)
            except ValueError:
                det = txt[:500]
            raise RuntimeError(f"HTTP {e.code} em {metodo} {caminho}: {json.dumps(det, ensure_ascii=False)}")
        except (urllib.error.URLError, TimeoutError) as e:
            if i == tentativas - 1:
                raise RuntimeError(f"falha de rede em {metodo} {caminho}: {e}")
            time.sleep(min(60, 5 * 2 ** i))
    raise RuntimeError(f"HeyGen não respondeu após {tentativas} tentativas ({metodo} {caminho})")


def baixar(url, destino):
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    parte = destino.with_suffix(destino.suffix + ".part")
    for i in range(4):
        try:
            with urllib.request.urlopen(url, timeout=120) as r, open(parte, "wb") as f:
                shutil.copyfileobj(r, f, 1 << 20)
            parte.replace(destino)
            return destino
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            log(f"download falhou ({e}); tentando de novo")
            time.sleep(5 * 2 ** i)
    raise RuntimeError(f"não consegui baixar {destino.name}")


# ---------------------------------------------------------------- roteiro

def validar_roteiro(rot):
    """Devolve (erros, alertas). Erro impede o envio; alerta só é mostrado."""
    erros, alertas = [], []
    mods = rot.get("modulos") or []
    if not mods:
        erros.append("roteiro sem 'modulos'.")
    vistos = set()
    for m in mods:
        n = m.get("n")
        if n is None:
            erros.append(f"módulo sem número 'n': {m.get('titulo', '?')}")
            continue
        if n in vistos:
            erros.append(f"módulo {n} repetido.")
        vistos.add(n)
        cenas = m.get("cenas") or []
        if not cenas:
            erros.append(f"módulo {n} sem cenas.")
        if len(cenas) > MAX_CENAS:
            erros.append(f"módulo {n} tem {len(cenas)} cenas; o HeyGen aceita até {MAX_CENAS} por vídeo.")
        for i, c in enumerate(cenas, 1):
            tag = f"M{n}C{i}"
            fala = (c.get("fala") or "").strip()
            if not fala:
                erros.append(f"{tag}: cena sem fala.")
                continue
            for num in re.findall(r"\d[\d.,/º°%]*", fala):
                alertas.append(f"{tag}: número na fala '{num}' (o avatar lê literalmente; escreva por extenso).")
            if re.search(r"[()\[\]/]", fala):
                alertas.append(f"{tag}: parênteses ou barra na fala (o avatar lê literalmente).")
            for frase in re.split(r"[.!?]", fala):
                if palavras(frase) > 30:
                    alertas.append(f"{tag}: frase com {palavras(frase)} palavras; dividir.")
    return erros, alertas


def duracao_estimada(modulo):
    return sum(palavras(c["fala"]) for c in modulo["cenas"]) / PPM * 60


def payload_modulo(rot, m, cfg):
    entrada = {"type": "avatar", "avatar_id": cfg["avatar_id"]}
    if cfg.get("voice_id"):
        entrada["voice_id"] = cfg["voice_id"]
    vs = {}
    if cfg.get("velocidade") and float(cfg["velocidade"]) != 1.0:
        vs["speed"] = float(cfg["velocidade"])
    if cfg.get("locale"):
        vs["locale"] = cfg["locale"]
    if vs:
        entrada["voice_settings"] = vs
    if cfg.get("engine"):
        entrada["engine"] = {"type": cfg["engine"]}
    fundo = cfg.get("fundo")
    if fundo:
        if str(fundo).startswith("#"):
            entrada["background"] = {"type": "color", "color": fundo}
        else:
            entrada["background"] = {"type": "image", "source": {"type": "url", "url": fundo}}
    if cfg.get("remover_fundo"):
        entrada["remove_background"] = True

    cenas = [{"type": "avatar_video", "input": {**entrada, "script": c["fala"].strip()}}
             for c in m["cenas"]]
    corpo = {
        "type": "studio",
        "title": f"{rot.get('curso', 'Video')} - M{int(m['n']):02d} {m.get('titulo', '')}".strip(),
        "aspect_ratio": cfg.get("proporcao") or "16:9",
        "resolution": cfg.get("resolucao") or "1080p",
        "scenes": cenas,
    }
    if cfg.get("brand_glossary_id"):
        corpo["brand_glossary_id"] = cfg["brand_glossary_id"]
    return corpo


# ---------------------------------------------------------------- estado

def abrir_projeto(pasta):
    pasta = Path(pasta).expanduser().resolve()
    est = pasta / "estado.json"
    if not est.exists():
        erro(f"{pasta} não tem estado.json; rode 'gerar' primeiro.")
    return pasta, ler_json(est)


def salvar_estado(pasta, estado):
    gravar_json(Path(pasta) / "estado.json", estado)


def nome_base(m):
    return f"M{int(m['n']):02d}_{slug(m.get('titulo', ''))}"


# ---------------------------------------------------------------- comandos

def cmd_verificar(a):
    ok = True
    print(f"API: {API}")
    try:
        me = api("GET", "/v3/users/me")
        d = me.get("data", me)
        resumo = {k: d.get(k) for k in ("email", "username", "billing_type") if k in d}
        cobranca = d.get(d.get("billing_type") or "", None)
        if isinstance(cobranca, dict):  # wallet / subscription / usage_based
            resumo["saldo"] = {k: v for k, v in cobranca.items() if k != "auto_reload"}
        print("Chave HeyGen: OK", json.dumps(resumo, ensure_ascii=False) if resumo else "")
    except (RuntimeError, SystemExit) as e:
        ok = False
        print(f"Chave HeyGen: FALHOU - {e}")
    print("ffmpeg:", "OK" if shutil.which("ffmpeg") else "NÃO ENCONTRADO")
    ok &= bool(shutil.which("ffmpeg"))
    dec = achar_decupar()
    print("skill decupagem-video:", dec or "NÃO ENCONTRADA")
    ok &= bool(dec)
    cfg = carregar_config()
    print(f"config: {CONFIG if CONFIG.exists() else 'não existe (rode configurar)'}")
    print("  avatar_id:", cfg.get("avatar_id") or "FALTA")
    print("  voice_id:", cfg.get("voice_id") or "(voz padrão do avatar)")
    print("  engine:", cfg.get("engine") or "(padrão do HeyGen)")
    ok &= bool(cfg.get("avatar_id"))
    if cfg.get("avatar_id") and os.environ.get("HEYGEN_API_KEY"):
        try:
            look = api("GET", f"/v3/avatars/looks/{cfg['avatar_id']}").get("data", {})
            print(f"  avatar: {look.get('name')} ({look.get('avatar_type')}), "
                  f"engines {look.get('supported_api_engines')}")
            if cfg.get("engine") and cfg["engine"] not in (look.get("supported_api_engines") or []):
                ok = False
                print(f"  AVISO: engine {cfg['engine']} não é suportado por este avatar.")
        except RuntimeError as e:
            ok = False
            print(f"  avatar: não encontrado ({e})")
    sys.exit(0 if ok else 1)


def cmd_avatares(a):
    cons = {"ownership": "public" if a.publicos else "private", "limit": 50}
    linhas, token = [], None
    while True:
        r = api("GET", "/v3/avatars/looks", consulta={**cons, "token": token})
        linhas += r.get("data", [])
        token = r.get("next_token")
        if not r.get("has_more") or not token or len(linhas) >= a.max:
            break
    for x in linhas[:a.max]:
        print(f"{x['id']}\t{x.get('name')}\t{x.get('avatar_type')}\t"
              f"engines={','.join(x.get('supported_api_engines') or [])}\t"
              f"voz_padrao={x.get('default_voice_id')}\tstatus={x.get('status')}")
    if not linhas:
        print("Nenhum avatar encontrado.")


def cmd_vozes(a):
    cons = {"type": "private" if a.privadas else "public", "language": a.idioma,
            "gender": a.genero, "limit": 100}
    linhas, token = [], None
    while True:
        r = api("GET", "/v3/voices", consulta={**cons, "token": token})
        linhas += r.get("data", [])
        token = r.get("next_token")
        if not r.get("has_more") or not token or len(linhas) >= a.max:
            break
    for v in linhas[:a.max]:
        print(f"{v['voice_id']}\t{v.get('name')}\t{v.get('language')}\t{v.get('gender')}\t"
              f"locale={v.get('support_locale')}\t{v.get('preview_audio_url') or ''}")
    if not linhas:
        print("Nenhuma voz encontrada.")


def cmd_configurar(a):
    cfg = carregar_config()
    mapa = {"avatar": "avatar_id", "voz": "voice_id", "engine": "engine", "velocidade": "velocidade",
            "locale": "locale", "fundo": "fundo", "resolucao": "resolucao", "proporcao": "proporcao",
            "glossario": "brand_glossary_id", "pasta_projetos": "pasta_projetos"}
    for arg, chave_cfg in mapa.items():
        v = getattr(a, arg)
        if v is not None:
            cfg[chave_cfg] = None if v in ("", "none", "nenhum") else v
    if a.remover_fundo is not None:
        cfg["remover_fundo"] = a.remover_fundo == "sim"
    gravar_json(CONFIG, cfg)
    print(f"Configuração gravada em {CONFIG}")
    print(json.dumps(cfg, ensure_ascii=False, indent=2))


def cmd_gerar(a):
    cfg = carregar_config()
    if not cfg.get("avatar_id"):
        erro("falta avatar_id na configuração; rode 'avatares' e depois 'configurar --avatar ID'.")
    rot = ler_json(a.roteiro)
    erros, alertas = validar_roteiro(rot)
    for x in alertas:
        log(f"alerta: {x}")
    if erros:
        erro("roteiro com problemas:\n  " + "\n  ".join(erros))

    pasta = Path(a.projeto).expanduser().resolve()
    pasta.mkdir(parents=True, exist_ok=True)
    est_path = pasta / "estado.json"
    estado = ler_json(est_path) if est_path.exists() else {
        "criado_em": datetime.now().isoformat(timespec="seconds"), "modulos": {}}
    estado["curso"] = rot.get("curso")
    estado["roteiro"] = str(pasta / "roteiro.json")
    estado["config_usada"] = {k: cfg.get(k) for k in PADRAO if k != "pasta_projetos"}
    if Path(a.roteiro).resolve() != (pasta / "roteiro.json").resolve():
        shutil.copyfile(a.roteiro, pasta / "roteiro.json")

    escolha = {int(x) for x in a.modulos.split(",")} if a.modulos else None
    mods = [m for m in rot["modulos"] if escolha is None or int(m["n"]) in escolha]
    if escolha and len(mods) != len(escolha):
        erro(f"módulos não encontrados no roteiro: {sorted(escolha - {int(m['n']) for m in mods})}")

    enviados = 0
    for m in mods:
        k = str(m["n"])
        atual = estado["modulos"].get(k, {})
        if atual.get("video_id") and atual.get("status") != "failed" and not a.refazer:
            log(f"M{k}: já enviado ({atual['video_id']}, {atual.get('status')}); pulando. "
                f"Use --refazer para gerar de novo (gasta créditos).")
            continue
        corpo = payload_modulo(rot, m, cfg)
        est = duracao_estimada(m)
        if a.dry_run:
            print(json.dumps(corpo, ensure_ascii=False, indent=2))
            log(f"M{k}: {len(m['cenas'])} cenas, ~{mmss(est)} estimados (dry-run, nada enviado)")
            continue
        r = api("POST", "/v3/videos", corpo)
        vid = (r.get("data") or {}).get("video_id")
        if not vid:
            erro(f"resposta sem video_id para M{k}: {r}")
        historico = atual.get("anteriores", [])
        if atual.get("video_id"):
            historico.append(atual["video_id"])
        estado["modulos"][k] = {
            "n": m["n"], "titulo": m.get("titulo", ""), "base": nome_base(m),
            "cenas": len(m["cenas"]), "duracao_estimada": round(est, 1),
            "video_id": vid, "status": (r.get("data") or {}).get("status", "pending"),
            "enviado_em": datetime.now().isoformat(timespec="seconds"),
            "anteriores": historico,
        }
        salvar_estado(pasta, estado)
        enviados += 1
        log(f"M{k}: enviado ao HeyGen (video_id {vid}, ~{mmss(est)} estimados)")
    if not a.dry_run:
        salvar_estado(pasta, estado)
        log(f"{enviados} vídeo(s) enviado(s). Estado em {est_path}")
    return pasta


def cmd_aguardar(a, pasta_fixa=None):
    pasta, estado = abrir_projeto(pasta_fixa or a.projeto)
    destino = pasta / "01_heygen"
    inicio = time.time()
    while True:
        pendentes = 0
        for k, m in sorted(estado["modulos"].items(), key=lambda x: int(x[0])):
            if not m.get("video_id") or m.get("arquivo") and Path(m["arquivo"]).exists():
                continue
            d = api("GET", f"/v3/videos/{m['video_id']}").get("data", {})
            st = d.get("status", "?")
            if st != m.get("status"):
                log(f"M{k}: {m.get('status')} -> {st}")
            m["status"] = st
            if st == "completed":
                url = d.get("video_url")
                if not url:
                    pendentes += 1
                    continue
                arq = baixar(url, destino / f"{m['base']}.mp4")
                m.update(arquivo=str(arq), duracao_heygen=d.get("duration"),
                         pagina=d.get("video_page_url"),
                         baixado_em=datetime.now().isoformat(timespec="seconds"))
                if d.get("subtitle_url"):
                    try:
                        baixar(d["subtitle_url"], destino / f"{m['base']}.srt")
                    except RuntimeError:
                        pass
                log(f"M{k}: baixado em {arq} ({d.get('duration')} s)")
            elif st == "failed":
                m["erro"] = f"{d.get('failure_code')}: {d.get('failure_message')}"
                log(f"M{k}: FALHOU no HeyGen - {m['erro']}")
            else:
                pendentes += 1
            salvar_estado(pasta, estado)
        if not pendentes:
            break
        if time.time() - inicio > a.timeout:
            log(f"tempo limite de {a.timeout}s atingido com {pendentes} vídeo(s) ainda em produção. "
                f"Rode 'aguardar' de novo depois; nada é perdido.")
            sys.exit(2)
        time.sleep(a.intervalo)
    falhos = [k for k, m in estado["modulos"].items() if m.get("status") == "failed"]
    if falhos:
        log(f"módulos com falha: {', '.join(falhos)}. Corrija e rode 'gerar --modulos {','.join(falhos)}'.")
    else:
        log("todos os vídeos do HeyGen estão baixados.")
    if pasta_fixa is None and falhos:
        sys.exit(1)
    return falhos


def achar_decupar():
    candidatos = [
        AQUI.parents[1] / "decupagem-video" / "scripts" / "decupar.py",
        Path.home() / ".claude" / "skills" / "decupagem-video" / "scripts" / "decupar.py",
    ]
    if os.environ.get("DECUPAR_PY"):
        candidatos.insert(0, Path(os.environ["DECUPAR_PY"]).expanduser())
    return next((str(p) for p in candidatos if p.exists()), None)


def cmd_decupar(a, pasta_fixa=None):
    pasta, estado = abrir_projeto(pasta_fixa or a.projeto)
    script = achar_decupar()
    if not script:
        erro("não encontrei decupar.py da skill decupagem-video (defina DECUPAR_PY com o caminho).")
    extra = a.args_decupagem.split() if getattr(a, "args_decupagem", None) else []
    destino = pasta / "02_decupado"
    falhou = False
    for k, m in sorted(estado["modulos"].items(), key=lambda x: int(x[0])):
        arq = m.get("arquivo")
        if not arq or not Path(arq).exists():
            continue
        saida = destino / f"{m['base']}_decupado.mp4"
        if saida.exists() and m.get("decupado") == str(saida) and not getattr(a, "refazer", False):
            continue
        destino.mkdir(parents=True, exist_ok=True)
        log(f"M{k}: decupando...")
        r = subprocess.run([sys.executable, script, arq, str(saida), *extra],
                           capture_output=True, text=True, encoding="utf-8")
        try:
            rel = json.loads(r.stdout)
        except ValueError:
            rel = {"erro": (r.stderr or r.stdout)[-1500:]}
        m["decupagem"] = {k2: rel.get(k2) for k2 in (
            "duracao_original", "duracao_final_video", "tempo_removido", "percentual_removido",
            "silencios_longos_3s", "sincronia_ok", "diferenca_av_ms", "erro") if k2 in rel}
        if r.returncode == 0 and rel.get("sincronia_ok"):
            m["decupado"] = str(saida)
            log(f"M{k}: {rel['duracao_original']}s -> {rel['duracao_final_video']}s "
                f"(-{rel['percentual_removido']}%)")
        else:
            falhou = True
            log(f"M{k}: decupagem com problema: {rel.get('erro') or 'sincronia_ok=false'}")
        salvar_estado(pasta, estado)
    if falhou and pasta_fixa is None:
        sys.exit(1)
    return not falhou


def cmd_status(a):
    pasta, estado = abrir_projeto(a.projeto)
    print(f"Projeto: {pasta}  Curso: {estado.get('curso')}")
    for k, m in sorted(estado["modulos"].items(), key=lambda x: int(x[0])):
        dec = m.get("decupagem") or {}
        print(f"M{int(k):02d} {m.get('titulo', '')[:40]:40} {m.get('status', '?'):10} "
              f"est {mmss(m.get('duracao_estimada') or 0)}  "
              f"heygen {m.get('duracao_heygen') or '-'}s  "
              f"decupado {dec.get('duracao_final_video') or '-'}s  "
              f"{'ERRO ' + m['erro'] if m.get('erro') else ''}")
        for rot, chave_ in (("  heygen:", "arquivo"), ("  decupado:", "decupado")):
            if m.get(chave_):
                print(rot, m[chave_])


def cmd_produzir(a):
    pasta = cmd_gerar(a)
    if a.dry_run:
        return
    falhos = cmd_aguardar(a, pasta)
    ok_decupagem = True
    if not a.sem_decupagem:
        ok_decupagem = cmd_decupar(a, pasta)
    a.projeto = str(pasta)
    cmd_status(a)
    if falhos or not ok_decupagem:
        sys.exit(1)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("verificar").set_defaults(f=cmd_verificar)

    p = sub.add_parser("avatares")
    p.add_argument("--publicos", action="store_true", help="lista os avatares públicos do HeyGen")
    p.add_argument("--max", type=int, default=100)
    p.set_defaults(f=cmd_avatares)

    p = sub.add_parser("vozes")
    p.add_argument("--idioma", default="Portuguese")
    p.add_argument("--genero")
    p.add_argument("--privadas", action="store_true", help="só as vozes clonadas da conta")
    p.add_argument("--max", type=int, default=100)
    p.set_defaults(f=cmd_vozes)

    p = sub.add_parser("configurar")
    for nome in ("avatar", "voz", "engine", "locale", "fundo", "resolucao", "proporcao", "glossario"):
        p.add_argument(f"--{nome}")
    p.add_argument("--velocidade", type=float)
    p.add_argument("--pasta-projetos", dest="pasta_projetos")
    p.add_argument("--remover-fundo", choices=["sim", "nao"])
    p.set_defaults(f=cmd_configurar)

    def opcoes_gerar(p):
        p.add_argument("roteiro")
        p.add_argument("-p", "--projeto", required=True, help="pasta do projeto")
        p.add_argument("--modulos", help="ex.: 1,3 (padrão: todos)")
        p.add_argument("--refazer", action="store_true", help="gera de novo módulos já enviados (gasta créditos)")
        p.add_argument("--dry-run", action="store_true", help="mostra o que seria enviado, sem enviar")

    def opcoes_aguardar(p):
        p.add_argument("--intervalo", type=int, default=30, help="segundos entre consultas")
        p.add_argument("--timeout", type=int, default=3 * 3600, help="desiste depois de N segundos")

    p = sub.add_parser("gerar")
    opcoes_gerar(p)
    p.set_defaults(f=cmd_gerar)

    p = sub.add_parser("aguardar")
    p.add_argument("-p", "--projeto", required=True)
    opcoes_aguardar(p)
    p.set_defaults(f=cmd_aguardar)

    p = sub.add_parser("decupar")
    p.add_argument("-p", "--projeto", required=True)
    p.add_argument("--args-decupagem", help='repassado ao decupar.py, ex.: "--keep-pause 0.4"')
    p.add_argument("--refazer", action="store_true")
    p.set_defaults(f=cmd_decupar)

    p = sub.add_parser("status")
    p.add_argument("-p", "--projeto", required=True)
    p.set_defaults(f=cmd_status)

    p = sub.add_parser("produzir")
    opcoes_gerar(p)
    opcoes_aguardar(p)
    p.add_argument("--sem-decupagem", action="store_true")
    p.add_argument("--args-decupagem")
    p.set_defaults(f=cmd_produzir)

    a = ap.parse_args()
    try:
        a.f(a)
    except RuntimeError as e:
        erro(str(e))


if __name__ == "__main__":
    main()
