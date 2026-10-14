# Painel Carteira KYCC

Painel do Intex com todos os clientes do cliente que passaram por parecer KYCC:
**https://claude.ai/artifact/4UYEKv3js3zd19bjnan9X9** (artefato do tipo Dashboard, privado).

Mostra: indicadores da carteira, uma linha do tempo com os prazos de todas as condicionantes
(com os marcos de 30/10/2026 e 06/11/2026), a tabela de clientes e, ao clicar, a ficha do
cliente (veredito, risco, TPV, protocolo, whitelist, pontos de atenção e condicionantes com o
"Por quê").

## Quando atualizar

- **Parecer final com fluxo liberado ou condicionado** (Não objeção, Não objeção condicionada):
  inclua o cliente. Uma minuta pode entrar com `versao` "001 (minuta)"; troque quando for emitida.
- **Objeção ou sobrestamento**: inclua também, com `fluxo` "Suspenso", para o histórico ficar
  completo, salvo se o usuário pedir para deixar de fora.
- **Revisão do parecer ou condicionante cumprida**: atualize o registro (status "Atendida",
  nova versão, novo fluxo).

Pergunte ao usuário antes de incluir só se o veredito for ambíguo. Nos demais casos, inclua e
avise em uma linha, com o link.

## O que entra como condicionante no painel

O painel é de **acompanhamento**: entra só o que foi **efetivamente pedido à Trace** (o que está no
e-mail enviado, ou no parecer já comunicado), com o prazo dado a ela. Não entram:
- acompanhamentos ainda não pedidos (ex.: documentação complementar que só será pedida depois do
  protocolo): entram quando o segundo e-mail for enviado;
- controles internos do Intex: revisão periódica (a data fica só no campo `proxima_revisao` da
  ficha), leitura interna do art. 91, gatilhos;
- nada que o parecer recomende sem ter virado pedido.

Na dúvida se algo foi pedido, confira o texto do e-mail enviado ou pergunte ao usuário.

## Formato

Linha da carteira (todos os campos, `""` quando não houver):
`id` (minúsculo, sem espaço, estável: "urban"), `cliente` (nome curto), `razao_social`, `cnpj`,
`psav`, `parecer` (número), `versao`, `data_parecer` (AAAA-MM-DD), `fluxo` ("Liberado",
"Aguardando condicionante", "Suspenso" ou "A confirmar"), `veredito` (como na caixa do parecer),
`risco_intex`, `risco_origem` (com fonte e data), `tpv_declarado`, `tpv_aprovado`,
`volume_observado` (com fonte; [E] se estimado), `protocolo_previsto`, `proxima_revisao`
(AAAA-MM-DD), `whitelist` (um endereço por linha, `\n`, com rede e ativo) e `pontos` (até 3
pontos de atenção, um por linha).

Condicionante: `codigo` (como no parecer), `tipo` ("Suspensiva", "Temporal", "Acompanhamento"
), `titulo` (o pedido como foi feito à Trace, em poucas palavras), `prazo` (AAAA-MM-DD ou ""), `status`
("Pendente" ou "Atendida") e `motivo` (o "Por quê" em uma frase).

Sem nomes de pessoas físicas nem CPF: o painel mostra empresas, endereços e datas.

## Como atualizar

1. **Sempre** baixe os dados atuais do painel, mesmo que você tenha cópias locais desta sessão: outras
   sessões e pessoas também atualizam o painel, e gravar uma cópia antiga apaga o trabalho delas.
   Leia `datasets/carteira` e `datasets/condicionantes` com `ArtifactData` `get` (anote a `version`)
   e baixe os arquivos da `source.url` de cada um com `Artifact` `action: "read"`, `path` = o id
   depois de `/_blob/`. Aplique a mudança sobre esses arquivos.
   (Alternativa antiga, só se o `get` falhar:) Liste os arquivos com `Artifact` `action: "list"`,
   `scope: "assets"` e a URL acima, e leia os de nome `carteira.json` e `condicionantes.json`
   mais recentes com `action: "read"` e `path` = id do asset. Ou leia antes os documentos
   `datasets/carteira` e `datasets/condicionantes` com `ArtifactData` `get`, que trazem a `url`
   (`/_blob/<id>`) de cada um.
2. Escreva o `registro.json` do cliente (formato acima) e rode
   `python <skill>/scripts/atualizar_carteira.py carteira.json condicionantes.json registro.json`.
3. Suba os dois arquivos com `Artifact` (`url` do painel, `asset: true`, `file_path`).
4. Com `ArtifactData` `batch`, pinado nas versões lidas no passo 1, atualize `datasets/carteira` e `datasets/condicionantes`
   (`update` com `if_version` lido no passo 1): `source.url` com o novo `/_blob/...`,
   `source.name` e `updated: {at: <ISO agora>, by: "Claude, parecer <número>"}`.
5. Não mexa em `files/index.html` para incluir cliente: a página lê tudo dos dados.
