#!/usr/bin/env python3
"""Monta o parecer KYCC do Intex Bank (.docx + .pdf) a partir de um JSON de conteúdo.

Uso:
    python build_parecer_kycc.py conteudo.json SAIDA.docx [--sem-pdf]

O layout (cabeçalho com logo, rodapé paginado, Trebuchet MS 9 pt, paleta Intex,
ficha, caixa de veredito, tabelas com cabeçalho azul-marinho) vem de
assets/modelo_kycc.docx. Este script só escreve o corpo e o número no rodapé.
O formato do JSON está em references/formato-json.md.

Marcação inline aceita em qualquer texto: **negrito** e *itálico*.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from xml.sax.saxutils import escape

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELO = os.path.join(SKILL, "assets", "modelo_kycc.docx")

NAVY, GREEN, TEXT, GREY, BORDER = "141D32", "92C024", "222222", "5A5F6B", "C9CCD3"
LABEL_FILL, VERDICT_FILL = "EEF1F5", "F2F8E6"
PAGE_W = 10206  # largura útil em twips (A4, margens de 1,5 cm)

ASSINATURA_PADRAO = {
    "nome": "Alexandre Ferrari",
    "cargo": "Coordenador de Ativos Virtuais e Compliance Digital",
    "instituicao": "Intex Bank — Banco de Câmbio S.A.",
}


# ---------------------------------------------------------------- runs e parágrafos
def _rpr(bold=False, italic=False, color=TEXT, size=None):
    p = []
    if bold:
        p.append("<w:b/><w:bCs/>")
    if italic:
        p.append("<w:i/><w:iCs/>")
    p.append(f'<w:color w:val="{color}"/>')
    if size:
        p.append(f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>')
    return "<w:rPr>" + "".join(p) + "</w:rPr>"


def runs(texto, color=TEXT, size=None, bold=False):
    """Converte **negrito** e *itálico* em runs."""
    out = []
    texto = str(texto)
    for tok in re.split(r"(\*\*.+?\*\*|\*[^*\s][^*]*?\*)", texto):
        if not tok:
            continue
        b, i = bold, False
        if tok.startswith("**") and tok.endswith("**"):
            tok, b = tok[2:-2], True
        elif tok.startswith("*") and tok.endswith("*") and len(tok) > 2:
            tok, i = tok[1:-1], True
        partes = tok.split("\n")
        for k, parte in enumerate(partes):
            if k:
                out.append(f"<w:r>{_rpr(b, i, color, size)}<w:br/></w:r>")
            if parte:
                out.append(f'<w:r>{_rpr(b, i, color, size)}<w:t xml:space="preserve">{escape(parte)}</w:t></w:r>')
    return "".join(out)


def para(texto, after=80, line=252, jc="both", color=TEXT, size=None, bold=False,
         keep_next=False, border_bottom=None, before=None):
    ppr = []
    if keep_next:
        ppr.append("<w:keepNext/>")
    if border_bottom:
        sz, cor = border_bottom
        ppr.append(f'<w:pBdr><w:bottom w:val="single" w:sz="{sz}" w:space="2" w:color="{cor}"/></w:pBdr>')
    bef = f' w:before="{before}"' if before is not None else ""
    sp = f'<w:spacing{bef} w:after="{after}"'
    sp += f' w:line="{line}" w:lineRule="auto"/>' if line else "/>"
    ppr.append(sp)
    if jc:
        ppr.append(f'<w:jc w:val="{jc}"/>')
    return f"<w:p><w:pPr>{''.join(ppr)}</w:pPr>{runs(texto, color, size, bold)}</w:p>"


def titulo_secao(texto):
    return para(texto, after=90, before=200, line=None, jc=None, color=NAVY, size=23,
                bold=True, keep_next=True, border_bottom=(8, GREEN))


def subtitulo(texto):
    return para(texto, after=50, before=120, line=None, jc=None, color=NAVY, size=19,
                bold=True, keep_next=True)


def bullets(itens):
    out = []
    for it in itens:
        out.append(
            '<w:p><w:pPr><w:pStyle w:val="PargrafodaLista"/><w:numPr><w:ilvl w:val="0"/>'
            '<w:numId w:val="2"/></w:numPr><w:spacing w:after="50" w:line="246" w:lineRule="auto"/>'
            f'<w:jc w:val="both"/></w:pPr>{runs(it)}</w:p>')
    return "".join(out)


# ---------------------------------------------------------------- tabelas
def _borders(top=(4, BORDER), left=(4, BORDER), bottom=(4, BORDER), right=(4, BORDER)):
    def b(nome, v):
        return f'<w:{nome} w:val="single" w:sz="{v[0]}" w:space="0" w:color="{v[1]}"/>'
    return "<w:tcBorders>" + b("top", top) + b("left", left) + b("bottom", bottom) + b("right", right) + "</w:tcBorders>"


def _cell(conteudo_xml, w, fill=None, borders=None, mar=(50, 90)):
    shd = f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>' if fill else ""
    return (f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>{borders or _borders()}{shd}'
            f'<w:tcMar><w:top w:w="{mar[0]}" w:type="dxa"/><w:left w:w="{mar[1]}" w:type="dxa"/>'
            f'<w:bottom w:w="{mar[0]}" w:type="dxa"/><w:right w:w="{mar[1]}" w:type="dxa"/></w:tcMar>'
            f"</w:tcPr>{conteudo_xml}</w:tc>")


def _cell_text(texto, bold=False, color=TEXT):
    # Células aceitam lista de parágrafos ou texto com \n\n separando parágrafos.
    blocos = texto if isinstance(texto, list) else str(texto).split("\n\n")
    return "".join(
        f'<w:p><w:pPr><w:spacing w:after="30" w:line="236" w:lineRule="auto"/></w:pPr>'
        f"{runs(b, color, 16, bold)}</w:p>" for b in blocos)


def _tbl(grid, rows_xml):
    cols = "".join(f'<w:gridCol w:w="{w}"/>' for w in grid)
    return (f'<w:tbl><w:tblPr><w:tblW w:w="{PAGE_W}" w:type="dxa"/><w:tblLayout w:type="fixed"/>'
            '<w:tblCellMar><w:left w:w="10" w:type="dxa"/><w:right w:w="10" w:type="dxa"/></w:tblCellMar>'
            '<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1" w:lastColumn="0" w:noHBand="0" w:noVBand="1"/>'
            f"</w:tblPr><w:tblGrid>{cols}</w:tblGrid>{rows_xml}</w:tbl>")


def _larguras(colunas):
    """colunas: lista de nomes ou de [nome, peso]. Pesos viram twips somando PAGE_W."""
    nomes, pesos = [], []
    for c in colunas:
        if isinstance(c, (list, tuple)):
            nomes.append(c[0]); pesos.append(float(c[1]))
        else:
            nomes.append(c); pesos.append(1.0)
    tot = sum(pesos)
    ws = [int(PAGE_W * p / tot) for p in pesos]
    ws[-1] += PAGE_W - sum(ws)
    return nomes, ws


def ficha(linhas):
    rows = []
    for rot, val in linhas:
        rows.append('<w:tr><w:trPr><w:cantSplit/></w:trPr>'
                    + _cell(_cell_text(rot, bold=True, color=NAVY), 2300, fill=LABEL_FILL)
                    + _cell(_cell_text(val), PAGE_W - 2300) + "</w:tr>")
    return _tbl([2300, PAGE_W - 2300], "".join(rows))


def tabela(spec):
    nomes, ws = _larguras(spec["colunas"])
    head = '<w:tr><w:trPr><w:cantSplit/><w:tblHeader/></w:trPr>' + "".join(
        _cell(_cell_text(n, bold=True, color="FFFFFF"), w, fill=NAVY) for n, w in zip(nomes, ws)) + "</w:tr>"
    body = []
    for linha in spec["linhas"]:
        if len(linha) != len(ws):
            raise SystemExit(f"Linha com {len(linha)} células numa tabela de {len(ws)} colunas: {linha[:1]}")
        body.append('<w:tr><w:trPr><w:cantSplit/></w:trPr>' + "".join(
            _cell(_cell_text(c), w) for c, w in zip(linha, ws)) + "</w:tr>")
    out = ""
    if spec.get("legenda"):
        out += para(spec["legenda"], after=40, line=None, jc=None, color=GREY, size=15, keep_next=True)
    out += _tbl(ws, head + "".join(body))
    out += '<w:p><w:pPr><w:spacing w:after="40"/></w:pPr></w:p>'
    return out


def veredito(v):
    conteudo = (f'<w:p><w:pPr><w:spacing w:after="50"/></w:pPr>{runs(v["titulo"], NAVY, 21, True)}</w:p>')
    textos = v.get("texto", "")
    for t in (textos if isinstance(textos, list) else [textos]):
        if t:
            conteudo += f'<w:p><w:pPr><w:spacing w:after="30"/><w:jc w:val="both"/></w:pPr>{runs(t)}</w:p>'
    cell = _cell(conteudo, PAGE_W, fill=VERDICT_FILL, mar=(100, 160),
                 borders=_borders(top=(18, GREEN), left=(18, GREEN)))
    return (_tbl([PAGE_W], f"<w:tr>{cell}</w:tr>")
            + '<w:p><w:pPr><w:spacing w:after="40" w:line="252" w:lineRule="auto"/></w:pPr></w:p>')


def assinatura(a, local_data):
    a = {**ASSINATURA_PADRAO, **(a or {})}
    out = ""
    if local_data:
        out += para(local_data, after=160, before=200, line=None, jc=None, keep_next=True)
    else:
        out += '<w:p><w:pPr><w:keepNext/><w:spacing w:after="160"/></w:pPr></w:p>'
    out += para("______________________________________", after=20, line=None, jc=None, color=GREY, keep_next=True)
    out += para(a["nome"], after=10, line=None, jc=None, color=NAVY, size=20, bold=True, keep_next=True)
    out += para(a["cargo"], after=10, line=None, jc=None, color=GREY, keep_next=True)
    out += para(a["instituicao"], after=0, line=None, jc=None, color=GREY)
    return out


# ---------------------------------------------------------------- montagem
def bloco(b):
    if isinstance(b, str):
        return para(b)
    tipo, val = next(iter(b.items()))
    if tipo == "p":
        return para(val)
    if tipo == "sub":
        return subtitulo(val)
    if tipo == "bullets":
        return bullets(val)
    if tipo == "tabela":
        return tabela(val)
    if tipo == "veredito":
        return veredito(val)
    if tipo == "nota":
        return para(val, after=60, line=None, color=GREY, size=15)
    raise SystemExit(f"Tipo de bloco desconhecido: {tipo}")


def corpo(c):
    x = para(c["titulo"], after=20, line=None, jc=None, color=NAVY, size=30, bold=True)
    x += ('<w:p><w:pPr><w:pBdr><w:bottom w:val="single" w:sz="12" w:space="4" w:color="92C024"/></w:pBdr>'
          f'<w:spacing w:after="120"/></w:pPr>{runs(c.get("subtitulo", ""), GREY, 19)}</w:p>')
    x += ficha(c["ficha"])
    for s in c["secoes"]:
        x += titulo_secao(s["titulo"])
        for b in s.get("blocos", []):
            x += bloco(b)
    x += assinatura(c.get("assinatura"), c.get("local_data"))
    return x


def pendencias_md(c, destino):
    p = c.get("pendencias")
    if not p:
        return None
    linhas = [f"Assunto: {p.get('assunto', 'Pendências — diligência complementar ' + c.get('objeto_curto', ''))}", ""]
    if p.get("saudacao"):
        linhas += [p["saudacao"], ""]
    if p.get("abertura"):
        linhas += [p["abertura"], ""]
    for grupo in p.get("grupos", []):
        linhas.append(grupo["titulo"])
        for it in grupo["itens"]:
            linhas.append(f"- {it}")
        linhas.append("")
    if p.get("fecho"):
        linhas += [p["fecho"], ""]
    linhas.append(f"Ref.: {c['numero']}")
    with open(destino, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas).replace("**", ""))
    return destino


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        sys.exit(__doc__)
    src, out = args
    c = json.load(open(src, encoding="utf-8"))
    for campo in ("numero", "titulo", "ficha", "secoes"):
        if campo not in c:
            sys.exit(f"Campo obrigatório ausente no JSON: {campo}")

    tmp = tempfile.mkdtemp()
    with zipfile.ZipFile(MODELO) as z:
        z.extractall(tmp)
    doc = os.path.join(tmp, "word", "document.xml")
    xml = open(doc, encoding="utf-8").read()
    if "{{CORPO}}" not in xml:
        sys.exit("modelo alterado: placeholder {{CORPO}} ausente em assets/modelo_kycc.docx")
    open(doc, "w", encoding="utf-8").write(xml.replace("{{CORPO}}", corpo(c)))
    ftr = os.path.join(tmp, "word", "footer1.xml")
    open(ftr, "w", encoding="utf-8").write(
        open(ftr, encoding="utf-8").read().replace("{{NUMERO}}", escape(c["numero"])))

    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    if os.path.exists(out):
        os.remove(out)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for raiz, _, arqs in os.walk(tmp):
            for a in arqs:
                cam = os.path.join(raiz, a)
                arc = os.path.relpath(cam, tmp)
                # [Content_Types].xml primeiro, como o Word espera
                z.write(cam, arc)
    shutil.rmtree(tmp)
    print("docx:", out)

    pend = pendencias_md(c, os.path.splitext(out)[0] + "_pendencias.md")
    if pend:
        print("pendências:", pend)

    if "--sem-pdf" not in sys.argv:
        outdir = os.path.dirname(os.path.abspath(out))
        r = subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", outdir, out],
                           capture_output=True, text=True, timeout=180)
        pdf = os.path.splitext(out)[0] + ".pdf"
        print("pdf:", pdf if os.path.exists(pdf) else f"falhou ({r.stderr.strip()[:200]})")


if __name__ == "__main__":
    main()
