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
- Condicionante é **dirigida à Trace** (cliente do Intex), não ao cliente dela.
- Cada condicionante diz **o que** entregar, **em que forma** (documento, data-base, assinado por
  quem) e **até quando**.
- Use S só para o que de fato impede o juízo ou a segurança do fluxo. O que é exigível mas não
  impede (política vencida com nova versão anunciada, DF auditada prevista) vai como AC com prazo.
- Na tabela de achados, a coluna "Encaminhamento" aponta o código (S2, AC1 · G4, "Registro", "Sem
  providência").
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
