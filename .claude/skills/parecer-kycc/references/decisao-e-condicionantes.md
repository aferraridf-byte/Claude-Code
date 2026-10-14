# Decisão, classificação e condicionantes

## Risco: perfil, conduta e residual

O parecer separa dois eixos e depois julga o residual. Escreva os três no resumo.

- **Risco de perfil** (inerente): o que a entidade é. PSAV, provisão de liquidez, pagamentos
  internacionais com stablecoin, alto volume, custódia em exchange estrangeira e regime de transição
  são, por natureza, **ALTO**. Ele só baixa um patamar quando o próprio perfil é mais contido (volume
  baixo, modelo simples, autorização já concedida, auditoria independente robusta) e isso está
  documentado.
- **Risco de conduta** (apurado): o que o dossiê mostra que a entidade fez. Imprecisões declaratórias,
  lacunas, documentos vencidos, divergências não explicadas, apontamentos de supervisão, sinais
  on-chain. Escala: BAIXO, MÉDIO, MÉDIO-ALTO, ALTO. Diga sempre se há ou não **indício de
  ilicitude**.
- **Risco residual (classificação do Intex)**: BAIXO, MÉDIO, MÉDIO-ALTO, ALTO ou CRÍTICO. É
  julgamento, não soma. Na prática, o padrão para PSAV é ALTO; MÉDIO-ALTO quando a conduta é limpa e
  os controles são comprovados (Parfin); CRÍTICO acompanha objeção.

Compare sempre com a **classificação de origem** da Trace e explique a divergência com fatores
verificáveis que ela não considerou.

## Vereditos

Use o título da caixa no formato `VEREDITO: <DECISÃO> — <SITUAÇÃO DO FLUXO>`. Os nomes abaixo
seguem a prática de mercado; crie variação só se o caso pedir.

| Decisão | Quando | Situação do fluxo |
|---|---|---|
| **NÃO OBJEÇÃO** | Nada impede; só acompanhamento e gatilhos | FLUXO LIBERADO |
| **NÃO OBJEÇÃO CONDICIONADA** | Há condicionantes; o fluxo depende de S (suspensivas) e/ou de T (temporal) | "S1 a S3 PENDENTES, FLUXO NÃO LIBERADO" ou "S1 CUMPRIDA, FLUXO LIBERADO" |
| **SOBRESTAMENTO** | Faltam peças essenciais para formar juízo (ex.: sem DF, sem atestado de carteiras, sem KYB de origem) | DECISÃO SUSPENSA ATÉ O ENVIO DE <itens> |
| **OBJEÇÃO** | Ilicitude ou indício relevante, sanção, exposição direta a sancionado/ilícito sem explicação, fraude documental, recusa em fornecer informação essencial, prazo regulatório perdido | FLUXO NÃO ADMITIDO |

Na objeção, diga o que precisaria mudar para reexame, se algo puder mudar.

## Condicionantes

Taxonomia fixa. A numeração é sequencial dentro de cada tipo e se mantém entre versões do mesmo
parecer (S1 continua S1 na revisão, mesmo cumprida: escreva "S1 — atendida e encerrada em DD/MM").

| Código | Tipo | Efeito |
|---|---|---|
| **S#** | Suspensiva | Impede a liberação do fluxo até ser cumprida |
| **T#** | Temporal | Exigível numa data certa (ex.: protocolo até 30/10/2026); se não cumprida, **suspensão automática**, sem nova deliberação |
| **AC#** | Acompanhamento | Sem efeito suspensivo; tem prazo (padrão: **60 dias** da data do parecer) |
| **G#** | Gatilho de reavaliação imediata | Evento que reabre o parecer, independentemente do prazo de revisão |
| **R** | Revisão periódica | Revisão integral: **6 meses** para ALTO e MÉDIO-ALTO, **12 meses** para MÉDIO ou abaixo; rescreening das carteiras, no mínimo, trimestral |

Regras:
- **Cada condicionante traz o seu "*Por quê:*"**, em 1 a 3 frases, depois do pedido. O usuário lê só
  a seção de condicionantes, então o motivo tem de se sustentar sozinho: cite o fato (com número e
  data) e o efeito para o Intex, sem remeter apenas ao achado ("ver A3"). Quando o motivo vier de uma
  lacuna nas conversas entre a Trace e o cliente (pedido feito e não atendido, resposta com print em
  vez de documento), diga isso em uma frase ("a Trace pediu o PDF em 10/09 e recebeu outro print").
  Se o pedido seria dispensável em condições normais, diga ("seria desnecessária se a política
  estivesse revisada"). Os gatilhos e a revisão periódica também levam um "Por quê" de uma linha.
- **Protocolo (regra do Intex)**: a T do protocolo pede o comprovante (número, data e modalidade)
  **enviado ao Intex até 30/10/2026**; sem ele, o fluxo é **suspenso em 02/11/2026**. Vale para todos
  os clientes do fluxo indireto. Se o BCB mudar o prazo do art. 88, as duas datas acompanham.
- **Previsibilidade regulatória**: antes do fim do prazo de protocolo, uma **declaração de intenção**
  (entidade, modalidade, data prevista) basta e é aceita até essa data; não exija carta de escritório
  nem comprovante. Depois do prazo, vale a T do protocolo.
  Procure a declaração no próprio dossiê antes de pedi-la: costuma estar no formulário de onboarding
  (Pipefy, campo de autorização BCB), no parecer da Trace ou na call. Cite onde está; se o usuário
  disser que já a tem, confirme a fonte com ele em vez de supor um documento externo.
- **Carteiras**: o atestado precisa cobrir **só os endereços que serão whitelistados e transacionados**
  com a liquidez do Intex. Não peça atestado de todas as carteiras do cliente; peça a confirmação de
  que a whitelist fica restrita aos endereços atestados e de que endereço novo só entra depois de
  atestado e triado.
- **Corroboração rebaixa**: se outra fonte já corrobora o ponto (ex.: on-chain confirma o volume
  declarado), o pedido do documento faltante vira AC, não S, e o "Por quê" explica isso.
- Condicionante é **dirigida à Trace** (cliente do Intex), não ao cliente dela.
- Cada condicionante diz **o que** entregar, **em que forma** (documento, data-base, assinado por
  quem) e **até quando**.
- Use S só para o que de fato impede o juízo ou a segurança do fluxo. O que é exigível mas não
  impede (política vencida com nova versão anunciada, DF auditada prevista) vai como AC com prazo.
- Na tabela de achados, a coluna "Encaminhamento" aponta o código (S2, AC1 · G4, "Registro", "Sem
  providência").
- **Horizonte curto.** Se o marco regulatório estiver mais perto que o prazo padrão de AC (60
  dias), priorize as S, encurte os prazos e diga no resumo e ao usuário que a liberação pode durar
  poucos dias. Não deixe AC vencer depois do marco que pode encerrar o fluxo.
- **Art. 91 depois de 06/11/2026.** Enquanto o Intex não fixar sua leitura (ver `normas.md`), use
  uma T própria: "suspensão automática em 06/11/2026, salvo autorização do analisado ou manifestação
  escrita do Intex admitindo a continuidade com o pedido em análise". Ela depende de decisão interna
  do Intex, não de entrega da Trace: diga isso no texto e na resposta ao usuário.
- Quando um item muda a data (ex.: BCB prorroga o prazo), a condicionante temporal se desloca junto,
  sem reabrir as demais; escreva isso.

### Gatilhos padrão (adapte e numere)
- Protocolo de autorização não comprovado no marco; indeferimento, arquivamento ou exigência do BCB
  que afete a continuidade.
- Exposição direta, ou indireta acima de tolerância zero, a categoria sancionada ou severa em
  carteira atribuída ao analisado.
- Uso de endereço sob controle do analisado não declarado.
- Mídia adversa, sanção, processo sancionador, medida judicial de constrição ou novo encerramento de
  conta bancária envolvendo o analisado, sócios, administradores ou contrapartes de liquidez.
- Volume observado acima de 150% do TPV cadastrado/recalibrado.
- Alteração de controle, de administradores ou da cadeia societária, inclusive no exterior.
- Alteração do marco regulatório (prorrogação, antecipação ou mudança de texto).

## Numeração e versões

- Formato: **`PAR-AVD-KYCC-AAAAMMDD-NNN`**. `AAAAMMDD` é a data do parecer; `NNN` é a versão do
  parecer **daquele objeto** (001 na primeira análise, 002 na segunda...).
- Revisão (resposta a condicionantes, fato novo): novo número com a data da revisão e o NNN
  seguinte. Na ficha: "consolida e substitui o(s) parecer(es) AAAAMMDD-001 ...". No enquadramento,
  um parágrafo diz o que a versão incorpora (documentos recebidos e datas). O parecer revisado é
  **completo e autônomo**: não é adendo.
- Se não souber o NNN (não há parecer anterior no contexto), use 001 e diga ao usuário que
  confirme.
- Nome do arquivo: `Parecer_KYCC_<Objeto>_<numero>.docx`.
