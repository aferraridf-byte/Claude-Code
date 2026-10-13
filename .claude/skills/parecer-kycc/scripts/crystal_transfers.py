#!/usr/bin/env python3
"""Resume o relatório "Transfers" exportado da Crystal Expert (PDF) e projeta o volume mensal.

Uso:
    python crystal_transfers.py "Transfers - <entidade> - ... - Crystal Expert.pdf"

O PDF da Crystal não traz sentido nem contraparte por linha e corta a exportação nas
~1.000 transferências mais recentes, mesmo com filtro de datas maior. Por isso o script
informa o período REAL coberto e projeta o mês a partir dele. A projeção "por sentido"
supõe entradas ≈ saídas (vale para carteira de passagem; confira no relatório
Interactions/Address, que traz Received e Sent totais). Marque o resultado como [E].
"""
import collections
import datetime as dt
import re
import statistics
import subprocess
import sys

LINHA = re.compile(
    r"(\w{3} \d{2}, \d{4})\s+(?:\n\s*)?([0-9a-fA-Fx]{64,66})\s+(Token Transfer|Regular|[A-Z][\w ]+?)\s+"
    r"([\d,]+(?:\.\d+)?) (\w+)\s+[\d.,]+\s*\n\s*(\d{2}:\d{2}:\d{2} [ap]m)")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    txt = subprocess.run(["pdftotext", "-layout", sys.argv[1], "-"], capture_output=True, text=True).stdout
    filtro = re.search(r"(\w{3} \d{2}, \d{4}) — (\w{3} \d{2}, \d{4})", txt)
    linhas = LINHA.findall(txt)
    if not linhas:
        sys.exit("Nenhuma transferência reconhecida: o layout do relatório mudou; leia o PDF visualmente.")
    por_ativo = collections.defaultdict(list)
    momentos = []
    for data, _h, _tipo, valor, ativo, hora in linhas:
        quando = dt.datetime.strptime(f"{data} {hora}", "%b %d, %Y %I:%M:%S %p")
        momentos.append(quando)
        por_ativo[ativo].append(float(valor.replace(",", "")))
    ini, fim = min(momentos), max(momentos)
    dias = max((fim - ini).total_seconds() / 86400, 1 / 24)
    print(f"Transferências reconhecidas: {len(linhas)}")
    if filtro:
        print(f"Filtro do relatório: {filtro.group(1)} a {filtro.group(2)}")
    print(f"Período efetivamente coberto: {ini:%d/%m/%Y %H:%M} a {fim:%d/%m/%Y %H:%M} ({dias:.2f} dias)")
    if len(linhas) >= 990:
        print("ATENÇÃO: ~1.000 linhas — a exportação foi cortada; o período coberto é menor que o filtro.")
    for ativo, vals in sorted(por_ativo.items(), key=lambda kv: -sum(kv[1])):
        soma = sum(vals)
        mensal = soma / dias * 30
        print(f"\n{ativo}: {len(vals)} transf., soma {soma:,.2f}, mediana {statistics.median(vals):,.2f}, "
              f"maior {max(vals):,.2f}")
        print(f"  projeção mensal somando os dois sentidos: {mensal:,.0f} [E]")
        print(f"  projeção mensal por sentido (entradas ≈ saídas): {mensal / 2:,.0f} [E]")


if __name__ == "__main__":
    main()
