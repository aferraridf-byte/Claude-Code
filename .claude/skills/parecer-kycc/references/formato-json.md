# Formato do JSON de conteúdo

`scripts/build_parecer_kycc.py` lê um JSON com esta forma. O exemplo completo (parecer real, anonimizado) está em
`assets/exemplo_kycc.json`: copie-o como ponto de partida.

```json
{
  "numero": "PAR-AVD-KYCC-AAAAMMDD-NNN",
  "objeto_curto": "<Objeto>",
  "titulo": "PARECER DE DILIGÊNCIA COMPLEMENTAR (KYCC)",
  "subtitulo": "Razão social (marca) — uma linha que diga o que esta versão é",
  "ficha": [["Rótulo", "valor com **negrito**"], ...],
  "secoes": [
    {"titulo": "1. Enquadramento", "blocos": [ ...blocos... ]}
  ],
  "local_data": "São Paulo, <dia> de <mês> de <ano>.",
  "assinatura": {"nome": "...", "cargo": "...", "instituicao": "..."},
  "pendencias": { ... }
}
```

- `numero` vai na ficha (você o escreve lá) e no rodapé de todas as páginas (o script o insere).
- `assinatura` é opcional. Sem ela, sai o padrão: Alexandre Ferrari, Coordenador de Ativos Virtuais
  e Compliance Digital, Intex Bank — Banco de Câmbio S.A.
- `local_data` é opcional; quando presente, sai acima da linha de assinatura.

## Marcação inline

Em qualquer texto: `**negrito**` e `*itálico*`. Em células de tabela, `\n\n` separa parágrafos.
Não há outra marcação: nada de Markdown de títulos ou listas dentro de strings.

## Blocos

Cada bloco é um objeto com uma única chave:

| Bloco | Uso |
|---|---|
| `{"p": "texto"}` | Parágrafo justificado. Para Fatos/Atenuação/Agravamento e para condicionantes, comece com o rótulo em negrito: `"**Fatos.** ..."`, `"**S1 — título.** ..."` |
| `{"sub": "3.1 Título"}` | Subtítulo de seção (azul-marinho, 9,5 pt) |
| `{"bullets": ["...", "..."]}` | Lista com o marcador verde ▪ do modelo |
| `{"veredito": {"titulo": "VEREDITO: ...", "texto": "..." }}` | Caixa verde-clara do resumo. `texto` pode ser string ou lista de parágrafos |
| `{"tabela": {"colunas": [...], "linhas": [[...]], "legenda": "..."}}` | Tabela com cabeçalho azul-marinho repetido em cada página. `colunas` aceita nomes ou `[nome, peso]`; os pesos viram proporção da largura útil. `legenda` (opcional) sai acima, em cinza |
| `{"nota": "texto"}` | Texto pequeno cinza (observações, fontes) |

Larguras de referência (pesos) usadas no modelo:
- achados: `[["#", 480], ["Achado", 1900], ["Leitura", 6126], ["Encaminhamento", 1700]]`
- quadro de 3 colunas: `[["Fonte", 3900], ["Valor", 3100], ["Leitura", 3206]]`
- vigências: `[["Referência", 2600], ["Data-base", 1900], ["Vence / venceu", 1900], ["Situação em DD/MM/AAAA", 3806]]`

## Pendências (`pendencias`)

Se presente, o script grava `<saida>_pendencias.md`, um e-mail pronto para a Trace:

```json
"pendencias": {
  "assunto": "Diligência complementar <Objeto> — documentos e esclarecimentos",
  "saudacao": "Prezados, boa tarde.",
  "abertura": "Uma ou duas frases: o que foi analisado e qual a situação do fluxo.",
  "grupos": [
    {"titulo": "Antes da liberação do fluxo (suspensivas)", "itens": ["S1 — ...", "S2 — ..."]},
    {"titulo": "Prazo regulatório", "itens": ["T1 — ..."]},
    {"titulo": "Acompanhamento (até DD/MM/AAAA)", "itens": ["AC1 — ..."]}
  ],
  "fecho": "Ficamos à disposição."
}
```

Os itens são pedidos concretos, endereçados à Trace (a contraparte), nunca ao cliente dela, e
dizem o que entregar e em que forma (documento, data-base, assinatura).
