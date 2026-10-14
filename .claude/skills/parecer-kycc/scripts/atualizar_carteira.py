#!/usr/bin/env python3
"""Inclui ou atualiza um cliente nos dados do painel Carteira KYCC.

Uso:
    python atualizar_carteira.py carteira.json condicionantes.json registro.json

registro.json = {"cliente": {...uma linha da carteira...}, "condicionantes": [{...}, ...]}
(formato em references/carteira.md). O cliente é localizado pelo campo "id": se já
existir, a linha é substituída e TODAS as condicionantes dele são trocadas pelas novas;
se não existir, é acrescentado. Os dois arquivos de entrada são regravados no lugar.
"""
import json
import sys

CAMPOS = ["id", "cliente", "razao_social", "cnpj", "psav", "parecer", "versao", "data_parecer", "fluxo",
          "veredito", "risco_intex", "risco_origem", "tpv_declarado", "tpv_aprovado", "volume_observado",
          "protocolo_previsto", "proxima_revisao", "whitelist", "pontos"]
FLUXOS = {"Liberado", "Aguardando condicionante", "Suspenso", "A confirmar"}
TIPOS = {"Suspensiva", "Temporal", "Acompanhamento", "Revisão"}
STATUS = {"Pendente", "Atendida"}


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    fc, fk, fr = sys.argv[1:]
    cart = json.load(open(fc, encoding="utf-8"))
    conds = json.load(open(fk, encoding="utf-8"))
    reg = json.load(open(fr, encoding="utf-8"))
    cli, novas = reg["cliente"], reg["condicionantes"]
    faltam = [c for c in CAMPOS if c not in cli]
    if faltam:
        sys.exit(f"Campos ausentes no cliente: {faltam} (use \"\" quando não houver).")
    if cli["fluxo"] not in FLUXOS:
        sys.exit(f"fluxo deve ser um de {sorted(FLUXOS)}")
    for c in novas:
        c.setdefault("cliente_id", cli["id"])
        c["id"] = f"{cli['id']}-{c['codigo']}"
        if c["tipo"] not in TIPOS or c["status"] not in STATUS:
            sys.exit(f"{c['id']}: tipo em {sorted(TIPOS)} e status em {sorted(STATUS)}")
        if c.get("prazo") and len(c["prazo"]) != 10:
            sys.exit(f"{c['id']}: prazo em AAAA-MM-DD ou vazio")
        if not c.get("motivo"):
            sys.exit(f"{c['id']}: toda condicionante leva o motivo (Por quê)")
    ids = [c["id"] for c in novas]
    if len(ids) != len(set(ids)):
        sys.exit("Códigos de condicionante repetidos para o mesmo cliente.")
    existia = any(r["id"] == cli["id"] for r in cart)
    cart = [r for r in cart if r["id"] != cli["id"]] + [{k: cli[k] for k in CAMPOS}]
    cart.sort(key=lambda r: r["data_parecer"], reverse=True)
    conds = [c for c in conds if c["cliente_id"] != cli["id"]] + novas
    json.dump(cart, open(fc, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(conds, open(fk, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{'Atualizado' if existia else 'Incluído'}: {cli['cliente']} ({len(novas)} condicionantes). "
          f"Carteira com {len(cart)} clientes e {len(conds)} condicionantes.")


if __name__ == "__main__":
    main()
