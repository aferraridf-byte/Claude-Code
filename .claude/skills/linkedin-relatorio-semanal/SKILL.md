---
name: linkedin-relatorio-semanal
description: Relatório semanal de desempenho do conteúdo no LinkedIn. Exporta no navegador o .xlsx de análises de conteúdo dos últimos 365 dias, coleta por post comentários, compartilhamentos, seguidores ganhos, texto e formato, compara a última semana com a média histórica, identifica o que os melhores posts têm em comum (gancho, formato, tamanho, tema, dia e horário), salva o relatório em LinkedIn/Relatórios e devolve os 3 aprendizados da semana. Use sempre que o usuário pedir o relatório semanal do LinkedIn, análise dos posts ou das métricas do LinkedIn, "como foram meus posts", "aprendizados da semana", ou quando a tarefa agendada de sábado disparar, mesmo que ele não diga "relatório".
---

# Relatório semanal do LinkedIn

Entrega: **um relatório (.xlsx + .md) em `LinkedIn/Relatórios/` e os 3 aprendizados da semana no chat.** Rode o fluxo inteiro sem pedir confirmação. Pergunte só se faltar algo que você não consegue obter (veja "Sem navegador").

## Pasta de trabalho

Procure uma pasta `LinkedIn` nesta ordem: na pasta de trabalho atual (no Cowork, a pasta selecionada), em `~/LinkedIn`, `~/Documents/LinkedIn`, `~/Documentos/LinkedIn` e `~/OneDrive*/**/LinkedIn`. Se não existir, crie-a na pasta de trabalho atual (ou em `~`) e diga onde ficou. Estrutura:

```
LinkedIn/
  Exportações/              # cada .xlsx exportado do LinkedIn (guarde todos)
  Dados/posts_detalhe.csv   # detalhes por post, acumulados semana a semana
  Relatórios/               # Relatorio_LinkedIn_AAAA-MM-DD.xlsx e .md
```

## Passo 1: exportar os últimos 365 dias (navegador)

Precisa de um navegador **já logado** no LinkedIn do usuário (Claude in Chrome). Nunca faça login, nunca peça senha, código ou cookie; se aparecer tela de login ou verificação, pare e avise.

1. Abra `https://www.linkedin.com/analytics/creator/content/` (Perfil → Análises → Impressões de publicações).
2. No seletor de período, escolha **Últimos 365 dias**.
3. Clique em **Exportar** e confirme. Baixa `AggregateAnalytics_<nome>_<início>_<fim>.xlsx` (formato atual) ou `Content_<início>_<fim>_<nome>.xlsx` (antigo) em Downloads.
4. Mova o arquivo para `LinkedIn/Exportações/`.

O export traz impressões e engajamentos por dia, novos seguidores por dia e até 50 posts por engajamentos e 50 por impressões (link e data). **Não traz** texto, formato, comentários, compartilhamentos nem seguidores por post: isso vem do passo 2.

## Passo 2: coletar os detalhes por post (navegador)

Monte a lista de posts a visitar:

- **Todos os posts publicados nos últimos 7 dias.** Confira na atividade do perfil (Perfil → Atividade → Mostrar todas as publicações), porque post sem engajamento pode não estar no export.
- Posts do export que ainda **não estão** no `posts_detalhe.csv`. Na primeira execução são todos; vá com calma.
- Posts publicados nos **últimos 30 dias**, para atualizar as métricas, que ainda mudam. Os mais antigos que já estão no CSV não precisam ser revisitados.

Para cada post:

1. **Análise do post**: abra `https://www.linkedin.com/analytics/post-summary/urn:li:activity:<ID>/` (o ID de 19 dígitos está no link do export). Se não abrir, abra o post e clique em "Ver análises". Anote impressões, membros alcançados, reações, comentários, compartilhamentos (republicações), salvamentos, envios, seguidores ganhos com esta publicação e visualizações do perfil a partir dela.
2. **O post**: abra o link e anote o texto completo, o formato e a primeira linha (o gancho).
3. Acrescente uma linha ao CSV. Para os posts revisitados só para atualizar as métricas, deixe texto, gancho e formato vazios: o script mantém os valores das coletas anteriores.

Espere alguns segundos entre as páginas e não ultrapasse ~80 páginas por execução. Se faltar, o restante entra na semana seguinte. Só leia: nunca curta, comente, compartilhe nem altere nada.

`LinkedIn/Dados/posts_detalhe.csv` (UTF-8, separado por vírgula; crie com este cabeçalho se não existir):

```
url,publicado_em,formato,tema,gancho,tipo_gancho,texto,caracteres,impressoes,alcance,reacoes,comentarios,compartilhamentos,salvamentos,envios,seguidores_ganhos,visitas_perfil,coletado_em
```

- `url`: copie **exatamente** o link do export (é a chave que liga o CSV ao export). Para post que não está no export, use o link do post.
- `publicado_em`: opcional (`AAAA-MM-DD HH:MM`). O script tira dia e hora do próprio ID do post.
- `formato`: `texto`, `imagem`, `carrossel` (documento/PDF), `vídeo`, `artigo`, `enquete`, `link` ou `repost`.
- `tema`: rótulo curto (1 a 3 palavras). **Reutilize os rótulos que já existem no CSV**; crie um novo só se nenhum servir, para os temas serem comparáveis entre semanas.
- `tipo_gancho`: `Pergunta`, `Lista`, `Dado/número`, `História pessoal`, `Contraintuitivo/provocação`, `Novidade/notícia`, `Citação` ou `Afirmação direta`. Se ficar vazio, o script classifica a primeira linha por heurística.
- Números sem separador de milhar (`1234`). `coletado_em`: data e hora da coleta.

## Passo 3: rodar a análise

Precisa de Python 3.8+ com `openpyxl` (`pip install openpyxl`). No Windows o comando costuma ser `python`.

```bash
python3 <pasta-da-skill>/scripts/analisar_linkedin.py \
  --export "LinkedIn/Exportações" \
  --detalhes "LinkedIn/Dados/posts_detalhe.csv" \
  --saida "LinkedIn/Relatórios"
```

- `--export` aceita o arquivo ou a pasta (usa o .xlsx mais recente).
- A semana analisada são os 7 dias que terminam no último dia do export. A média histórica vem dos blocos de 7 dias anteriores dentro do export (até 52 semanas). Use `--fim AAAA-MM-DD` para fixar outro fim.
- O script grava `Relatorio_LinkedIn_<fim>.xlsx` (abas Resumo, Por post, Posts, Padrões, Semanas e Notas) e `.md`, e imprime um JSON com `semana_x_historico`, `por_post`, `posts_da_semana`, `melhores_posts`, `padroes`, `aprendizados_candidatos` e `avisos`.

Como ele define os melhores posts: **score de 0 a 100** = média dos percentis do post em impressões, taxa de engajamento (engajamentos ÷ impressões), comentários, compartilhamentos e seguidores ganhos (só as métricas disponíveis para a maioria dos posts). Os melhores são os 20% de maior score (mínimo 3, máximo 10). Em cada dimensão (formato, gancho, tamanho, tema, dia e faixa horária), o script compara a participação de cada valor entre os melhores com a participação em todos os posts (lift) e a mediana de impressões do grupo.

## Passo 4: escrever os 3 aprendizados

Leia o JSON e o `.md` gerado. Leia também o relatório da semana anterior em `LinkedIn/Relatórios`, para não repetir um aprendizado que não mudou. Escreva **exatamente 3 aprendizados**, cada um com:

- **o fato com número** (ex.: "5 dos 8 melhores posts abrem com um dado concreto, contra 18% dos posts do ano; mediana de 4.735 impressões, contra 2.720"), e
- **a ação para a próxima semana** (ex.: "abrir o post de terça com o número da multa, não com a pergunta").

Regras:

- Pelo menos um aprendizado sobre **a semana x a média histórica** e pelo menos um sobre **o que os melhores posts têm em comum**.
- Não afirme padrão com menos de 2 posts entre os melhores ou com base menor que 5 posts. Se a base for pequena, diga que é um indício.
- Post com menos de 3 dias ainda está acumulando impressões. Não o chame de fraco por isso.
- Respeite os `avisos`: lista truncada em 50, posts sem detalhe e semana sem post mudam a conclusão.
- `aprendizados_candidatos` é ponto de partida, não resposta. Escolha, junte, corrija e reescreva em português claro, sem jargão.

Salve os 3 em `LinkedIn/Dados/aprendizados_<fim>.txt` (um por linha) e rode o script de novo com `--aprendizados LinkedIn/Dados/aprendizados_<fim>.txt`, para eles entrarem no topo do relatório.

## Passo 5: entregar

No chat, curto:

1. Os 3 aprendizados, numerados.
2. Uma linha com a semana em números: impressões, taxa de engajamento e novos seguidores, cada um com a variação contra a média.
3. O caminho do relatório.
4. O que ficou de fora, se algo ficou (post sem detalhe, coleta interrompida).

## Sem navegador

Se não houver navegador logado no LinkedIn (sessão na nuvem, Chrome desconectado ou LinkedIn pedindo login):

1. Procure um export de até 3 dias em `LinkedIn/Exportações/` e em `~/Downloads`. Se achar, rode os passos 3 a 5 com o CSV que existir e avise que os posts da semana ficaram sem detalhe (comentários, compartilhamentos, seguidores, gancho, formato e tema).
2. Se não achar, pare e diga ao usuário o que falta: exportar o .xlsx de 365 dias e deixá-lo em `LinkedIn/Exportações/`. Não tente outro caminho para entrar no LinkedIn.

## Agendamento

A skill foi feita para rodar como **tarefa agendada no app Claude para desktop (Cowork), aos sábados às 9h**, com o Claude in Chrome conectado ao navegador em que o LinkedIn está logado. Prompt da tarefa: `Rode a skill linkedin-relatorio-semanal e me dê os 3 aprendizados da semana.` O computador precisa estar ligado, com o app aberto, no horário.

## Problemas

- **"não achei a aba ENGAGEMENT"**: o arquivo não é o export de conteúdo (pode ser o de seguidores ou o de visitantes). Exporte de novo pela página de impressões de publicações.
- **Post aparece duas vezes no relatório**: a `url` do CSV não bate com a do export (por exemplo, `urn:li:share` num e `urn:li:activity` no outro). Corrija a `url` no CSV para a do export.
- **Datas trocadas (dia e mês)**: o script detecta D/M/AAAA quando algum primeiro campo passa de 12. Num export com poucos dias isso pode falhar; confira o período no topo do `.md`.
