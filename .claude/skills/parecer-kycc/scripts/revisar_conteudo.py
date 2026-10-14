#!/usr/bin/env python3
"""Ferramentas de revisão do JSON de conteúdo do parecer.

Uso:
    python revisar_conteudo.py localizar conteudo.json termo [termo ...]
        Lista TODOS os lugares do parecer (ficha, resumo, tabela de achados, quadros,
        condicionantes, limitações, e-mail de pendências) em que o termo aparece.
        Use antes de corrigir um fato: a correção tem de chegar a todas as ocorrências.

    python revisar_conteudo.py negativas conteudo.json
        Lista as frases com afirmação de ausência ou negação ("não há", "não veio",
        "só verbal", "nada", "sem ..."). Cada uma deve ser conferida com
        buscar_dossie.py antes da entrega.

    python revisar_conteudo.py substituir conteudo.json trocas.json saida.json
        Aplica trocas de texto com segurança. trocas.json é uma lista
        [["texto antigo", "texto novo"], ...]. As trocas são feitas dentro das strings
        (aspas e acentos não quebram o JSON) e o script falha se algum texto antigo não
        for encontrado. No fim, mostra onde ainda restam os termos do campo opcional
        "conferir" de cada troca: [["antigo", "novo", ["termo a conferir", ...]], ...].
"""
import json
import re
import sys

NEGATIVAS = re.compile(
    r"[^.;]*\b(não (há|houve|veio|vieram|foi|foram|consta|constam|apresent\w*|comprov\w*|document\w*|identific\w*)"
    r"|nada (disso|consta)|sem (documento|comprova\w*|declara\w*|evid\w*|registro)|só verbal\w*"
    r"|apenas verbal\w*|ausência de|inexist\w*)[^.;]*[.;]?", re.IGNORECASE)


def caminhos(o, cam="$"):
    """Gera (caminho legível, texto) para cada string do JSON."""
    if isinstance(o, dict):
        for k, v in o.items():
            yield from caminhos(v, f"{cam}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from caminhos(v, f"{cam}[{i}]")
    elif isinstance(o, str):
        yield cam, o


def rotulo(c, cam):
    """Traduz o caminho JSON para a parte do parecer."""
    m = re.match(r"\$\.secoes\[(\d+)\]", cam)
    if m:
        sec = c["secoes"][int(m.group(1))]["titulo"]
        if ".tabela.linhas[" in cam:
            lin = re.search(r"\.tabela\.linhas\[(\d+)\]", cam).group(1)
            return f"{sec} › tabela, linha {int(lin) + 1}"
        return sec
    if cam.startswith("$.ficha"):
        return "Ficha"
    if cam.startswith("$.pendencias"):
        return "E-mail de pendências"
    return cam


def localizar(c, termos):
    achou = 0
    for termo in termos:
        t = termo.lower()
        print(f"\n## \"{termo}\"")
        for cam, s in caminhos(c):
            i = s.lower().find(t)
            if i >= 0:
                achou += 1
                print(f"- {rotulo(c, cam)}: …{s[max(0, i - 80): i + len(termo) + 80]}…")
    return achou


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        sys.exit(__doc__)
    cmd, arq = a[0], a[1]
    c = json.load(open(arq, encoding="utf-8"))
    if cmd == "localizar":
        localizar(c, a[2:])
    elif cmd == "negativas":
        n = 0
        for cam, s in caminhos(c):
            for m in NEGATIVAS.finditer(s):
                n += 1
                print(f"- {rotulo(c, cam)}: {m.group(0).strip()}")
        print(f"\n{n} afirmação(ões) de ausência/negação para conferir no dossiê.")
    elif cmd == "substituir":
        trocas = json.load(open(a[2], encoding="utf-8"))
        usados = [0] * len(trocas)

        def troca(o):
            if isinstance(o, dict):
                return {k: troca(v) for k, v in o.items()}
            if isinstance(o, list):
                return [troca(v) for v in o]
            if isinstance(o, str):
                for i, t in enumerate(trocas):
                    if t[0] in o:
                        o = o.replace(t[0], t[1])
                        usados[i] += 1
            return o

        novo = troca(c)
        faltou = [t[0] for t, u in zip(trocas, usados) if not u]
        if faltou:
            sys.exit("Textos não encontrados (nada foi gravado):\n" + "\n".join(f"- {f[:120]}" for f in faltou))
        json.dump(novo, open(a[3], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"{sum(usados)} troca(s) aplicada(s) em {a[3]}.")
        conferir = [x for t in trocas if len(t) > 2 for x in t[2]]
        if conferir and localizar(novo, conferir):
            print("\nAinda há ocorrências dos termos a conferir: veja se cada uma está coerente com a correção.")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
