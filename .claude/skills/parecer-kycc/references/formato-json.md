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

Se presente, o script grava `<saida>_pendencias.md`, o e-mail à Trace no padrão de
`references/mensagem-trace.md` (leia antes de escrever):

```json
"pendencias": {
  "assunto": "RE: <assunto do fio de e-mail com a Trace>",
  "saudacao": "Prezados, boa tarde. Tudo bem?",
  "abertura": "Um parágrafo: o que foi feito, o resultado e o que já foi aceito.",
  "grupos": [
    {"titulo": "Whitelist (condição para liberação)", "texto": "Uma frase, quando o bloco é um pedido só."},
    {"titulo": "Autorização no BCB", "itens": ["comprovante do protocolo ...", "até 05/11/2026, a situação do processo ..."], "nota": "Na falta desses itens, o fluxo é suspenso nas respectivas datas."},
    {"titulo": "Documentação complementar (até DD/MM/AAAA)", "itens": ["...", "..."]}
  ],
  "fecho": ["Preferencialmente, os documentos em PDF. Ficamos à disposição para uma breve call caso haja dúvidas sobre o escopo.", "Atenciosamente,"]
}
```

Os blocos são numerados pelo script. Sem motivo item a item: os motivos ficam no parecer.
A assinatura padrão é acrescentada ao fim.
