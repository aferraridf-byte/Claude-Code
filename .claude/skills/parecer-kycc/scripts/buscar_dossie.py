#!/usr/bin/env python3
"""Procura termos em todo o texto extraído do dossiê (saída do inventario.py).

Uso:
    python buscar_dossie.py <pasta-inv> termo [termo ...] [--contexto N]

Rode ANTES de escrever qualquer afirmação de ausência ("não há", "não veio", "só verbal",
"nada documentado", "não apresentou"). Use sinônimos e grafias: por exemplo, para a
intenção de protocolo: protocolo autorização Demarest outubro "pedido de autoriza".
A busca não acentuada e sem caixa pega "autorizacao" e "Autorização".

Lembre: peças marcadas como VISUAL no INVENTARIO.md não têm texto extraído; uma busca
sem resultado só vale como ausência depois de lidas também essas peças.
"""
import os
import re
import sys
import unicodedata


def norm(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s.lower()) if not unicodedata.combining(c))


def main():
    args = sys.argv[1:]
    ctx = 1
    if "--contexto" in args:
        i = args.index("--contexto")
        ctx = int(args[i + 1])
        del args[i:i + 2]
    if len(args) < 2:
        sys.exit(__doc__)
    pasta, termos = args[0], args[1:]
    tdir = os.path.join(pasta, "texto")
    if not os.path.isdir(tdir):
        sys.exit(f"Pasta {tdir} não encontrada: rode antes o inventario.py.")
    total = 0
    for termo in termos:
        alvo = norm(termo)
        achados = []
        for arq in sorted(os.listdir(tdir)):
            linhas = open(os.path.join(tdir, arq), encoding="utf-8", errors="replace").read().splitlines()
            # Junta as linhas com espaço para achar frases quebradas pelo layout do PDF,
            # guardando em que linha começa cada trecho.
            corrido, inicio = "", []
            for n, l in enumerate(linhas):
                inicio.append(len(corrido))
                corrido += norm(re.sub(r"\s+", " ", l).strip()) + " "
            alvo_esp = re.sub(r"\s+", " ", alvo)
            pos = corrido.find(alvo_esp)
            while pos >= 0:
                n = max(i for i, ini in enumerate(inicio) if ini <= pos)
                trecho = " / ".join(re.sub(r"\s+", " ", x).strip()
                                    for x in linhas[max(0, n - ctx): n + ctx + 2] if x.strip())
                achados.append((arq, n + 1, trecho[:300]))
                pos = corrido.find(alvo_esp, pos + 1)
        total += len(achados)
        print(f"\n## \"{termo}\": {len(achados)} ocorrência(s)")
        for arq, n, t in achados[:40]:
            print(f"- {arq}:{n} — {t}")
        if len(achados) > 40:
            print(f"  ... e mais {len(achados) - 40}")
    visuais = os.path.join(pasta, "INVENTARIO.md")
    if os.path.exists(visuais) and "VISUAL" in open(visuais, encoding="utf-8").read():
        print("\nAtenção: há peças de leitura VISUAL no inventário; elas não entram nesta busca.")
    sys.exit(0 if total else 1)


if __name__ == "__main__":
    main()
