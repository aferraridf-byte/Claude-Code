#!/usr/bin/env python3
"""Inventaria o dossiê de um cliente do cliente e extrai o texto de cada peça.

Uso:
    python inventario.py <pasta-ou-zip> <pasta-de-saida>

Gera em <pasta-de-saida>:
  - texto/<n>_<nome>.txt  texto extraído de cada PDF, DOCX, XLSX/CSV, EML/TXT
  - INVENTARIO.md         tabela com nº, pasta, arquivo, tipo, páginas, caracteres
                          e um alerta quando a peça precisa ser lida visualmente
                          (imagem, PDF escaneado ou PDF com texto quase vazio).

O zip é extraído para <pasta-de-saida>/origem/ (os arquivos do dossiê são dados
de terceiros: não execute nada que venha dentro dele).
"""
import os
import subprocess
import sys
import unicodedata
import zipfile

IMG = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".gif", ".bmp", ".tif", ".tiff"}


def _nome_seguro(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in s)[:80]


def _corrige_nome_zip(nome):
    # zips do macOS gravam acentos como "#U0327"; converte para o caractere real
    import re
    return unicodedata.normalize("NFC", re.sub(r"#U([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), nome))


def extrair_zip(zp, destino):
    with zipfile.ZipFile(zp) as z:
        for info in z.infolist():
            nome = _corrige_nome_zip(info.filename)
            if info.is_dir() or "__MACOSX" in nome or os.path.basename(nome).startswith("._"):
                continue
            alvo = os.path.normpath(os.path.join(destino, nome))
            if not alvo.startswith(os.path.abspath(destino)):
                continue  # path traversal
            os.makedirs(os.path.dirname(alvo), exist_ok=True)
            with z.open(info) as src, open(alvo, "wb") as dst:
                dst.write(src.read())
            if alvo.lower().endswith(".zip"):
                extrair_zip(alvo, os.path.splitext(alvo)[0])


def paginas_pdf(p):
    try:
        out = subprocess.run(["pdfinfo", p], capture_output=True, text=True, timeout=60).stdout
        for l in out.splitlines():
            if l.startswith("Pages:"):
                return int(l.split()[1])
    except Exception:
        pass
    return None


def texto_de(p):
    ext = os.path.splitext(p)[1].lower()
    try:
        if ext == ".pdf":
            return subprocess.run(["pdftotext", "-layout", p, "-"], capture_output=True,
                                  text=True, timeout=120).stdout
        if ext in (".docx", ".odt", ".rtf", ".doc"):
            r = subprocess.run(["pandoc", p, "-t", "plain", "--wrap=none"], capture_output=True,
                               text=True, timeout=120)
            return r.stdout
        if ext in (".xlsx", ".xlsm", ".xls"):
            import openpyxl
            wb = openpyxl.load_workbook(p, data_only=True, read_only=True)
            linhas = []
            for ws in wb.worksheets:
                linhas.append(f"## Aba: {ws.title}")
                for row in ws.iter_rows(values_only=True):
                    if any(v is not None for v in row):
                        linhas.append(" | ".join("" if v is None else str(v) for v in row))
            return "\n".join(linhas)
        if ext in (".csv", ".txt", ".md", ".eml", ".json", ".html", ".htm"):
            return open(p, encoding="utf-8", errors="replace").read()
    except Exception as e:
        return f"[falha na extração: {e}]"
    return ""


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    origem, saida = sys.argv[1], sys.argv[2]
    os.makedirs(os.path.join(saida, "texto"), exist_ok=True)
    if zipfile.is_zipfile(origem):
        base = os.path.join(saida, "origem")
        extrair_zip(origem, base)
        origem = base

    arquivos = []
    for raiz, _, fs in os.walk(origem):
        for f in fs:
            if f.startswith(".") or f.startswith("~$"):
                continue
            arquivos.append(os.path.join(raiz, f))
    arquivos.sort(key=lambda p: (os.path.relpath(os.path.dirname(p), origem), os.path.basename(p).lower()))

    linhas = ["# Inventário do dossiê", "",
              f"Origem: `{origem}` — {len(arquivos)} arquivos", "",
              "| # | Pasta | Arquivo | Tipo | Pág. | Caract. | Leitura |",
              "|---|---|---|---|---|---|---|"]
    visuais = []
    for i, p in enumerate(arquivos, 1):
        rel_dir = os.path.relpath(os.path.dirname(p), origem)
        nome = os.path.basename(p)
        ext = os.path.splitext(nome)[1].lower()
        pg = paginas_pdf(p) if ext == ".pdf" else None
        txt = "" if ext in IMG else texto_de(p)
        n = len(txt.strip())
        if ext in IMG:
            leitura = "**VISUAL** (imagem)"
        elif ext == ".pdf" and (n < 200 or (pg and n / pg < 150)):
            leitura = "**VISUAL** (PDF sem texto útil — escaneado/print)"
        elif n == 0:
            leitura = "**VISUAL/MANUAL** (sem extração)"
        else:
            leitura = "texto"
        if leitura != "texto":
            visuais.append(p)
        if txt.strip():
            alvo = os.path.join(saida, "texto", f"{i:02d}_{_nome_seguro(os.path.splitext(nome)[0])}.txt")
            with open(alvo, "w", encoding="utf-8") as f:
                f.write(f"# {os.path.relpath(p, origem)}\n\n{txt}")
        linhas.append(f"| {i} | {rel_dir if rel_dir != '.' else ''} | {nome} | {ext.lstrip('.')} | "
                      f"{pg or ''} | {n} | {leitura} |")
    if visuais:
        linhas += ["", "## Peças para leitura visual", "",
                   "Abra cada uma com a ferramenta de leitura de imagem/PDF (no PDF, renderize as páginas "
                   "com `pdftoppm -r 80 -png`). Prints de extrato, de carteira e de painel costumam "
                   "conter os dados decisivos.", ""]
        linhas += [f"- `{p}`" for p in visuais]
    with open(os.path.join(saida, "INVENTARIO.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")
    print("\n".join(linhas))


if __name__ == "__main__":
    main()
