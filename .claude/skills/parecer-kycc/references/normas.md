# Base normativa

Verificada no texto oficial (API de normativos do BCB, DOU e Planalto) em **13/10/2026**. A
regulação de ativos virtuais muda depressa: antes de citar um prazo ou artigo num parecer, confira
se há norma posterior a esta data (busca em
`https://www.bcb.gov.br/estabilidadefinanceira/buscanormas` ou na API
`https://www.bcb.gov.br/api/conteudo/app/normativos/exibenormativo?p1=<tipo>&p2=<nº>`). O acesso
direto ao bcb.gov.br pode ser bloqueado pelo proxy; use a ferramenta de scrape disponível. Se
encontrar alteração, use o texto novo e avise o usuário de que esta referência precisa ser atualizada.

Só normas públicas. Políticas internas do Intex podem ser mencionadas se o usuário fornecer o nome e
a versão; não invente.

## Sumário
- Cadeia e provimento de liquidez (Res. BCB 520)
- Marco temporal: transição (art. 88) e vedação de contraparte (art. 91, alterado pela Res. BCB 589/2026)
- Autorização (Res. BCB 519)
- Câmbio (Res. BCB 521)
- Capital mínimo (Res. Conjunta 14 e Res. BCB 517)
- PLD/FT (Lei 9.613, Circular 3.978 e Res. BCB 591/2026; Res. BCB 44)
- Travel Rule (art. 44 e art. 89 da Res. 520)
- Obrigações acessórias (IN RFB 1.888 → IN RFB 2.291/2025, DeCripto)
- Lei 14.478/2022

## Cadeia e provimento de liquidez — Res. BCB nº 520/2025 (vigente desde 02/02/2026, art. 92)

- **Art. 2º, XIV**: define provedores de liquidez do mercado de ativos virtuais como instituições e
  entidades que atuam **por conta própria**, nos termos da contratação por PSAV, tendo como
  contrapartes principais investidores institucionais e as próprias PSAV.
- **Art. 38**: conteúdo mínimo do contrato entre a PSAV e o provedor de liquidez. **§ 1º**: é vedado
  ao provedor de liquidez atuar tendo como contrapartes os demais clientes e usuários da PSAV
  contratante (exceção do § 2º para RFQ do art. 67, § 6º). **§ 3º**: a PSAV contratante responde
  perante o BCB pelas operações do provedor contratado.
- Uso no parecer: o art. 2º, XIV, e o art. 38 sustentam o enquadramento ("o Intex atua como provedor de
  liquidez, por conta própria; a Trace é a PSAV contratante"). O § 1º do art. 38 reforça que o
  cliente do cliente **não é contraparte do Intex**. O art. 38 **não** trata de contraparte não
  autorizada: para isso, use o art. 91.

## Marco temporal

### Art. 88 — PSAV em funcionamento em 02/02/2026
- **I**: solicitar autorização no prazo máximo de **270 dias** da entrada em vigor →
  **30/10/2026** (contagem; a data não está escrita no texto).
- **§ 6º**: quem protocolar a tempo pode manter a prestação dos serviços até a conclusão do processo
  de autorização.
- **§ 7º**: quem não protocolar tempestivamente deve **cessar a prestação em até 30 dias** após o
  fim do prazo.
- **Indeferimento ou arquivamento** sem recurso: cessar em 30 dias da notificação — **Res. BCB 519,
  art. 18** (não é a 520).
- Na transição, o art. 88, II, exige, entre outros, observância da regulamentação de PLD/FT (alínea
  "c") e dos procedimentos da Lei 13.810/2019 (alínea "d").

### Art. 91 — vedação às instituições autorizadas (o Intex entre elas)
- **Redação original**: vedado, **a partir de 30/10/2026**, realizar ou viabilizar operações com
  contrapartes que prestem serviços de ativos virtuais e **não estejam autorizadas ou em processo de
  autorização**.
- **Redação vigente desde 01/10/2026 (Res. BCB 589/2026, DOU de 25/09/2026)**: vedado, **a partir
  de 06/11/2026**, realizar ou viabilizar operações no mercado de ativos virtuais que tenham como
  contrapartes instituições ou entidades que prestem serviços de ativos virtuais e **não estejam
  autorizadas a funcionar no país** pelo BCB, **exceto nas formas expressamente autorizadas nesta
  Resolução**. A expressão "ou em processo de autorização" **saiu do texto**.
- **Parágrafo único**: a vedação alcança negociação, intermediação e custódia, operações de câmbio,
  contas de pagamento e transações de pagamento.
- **Ponto interpretativo em aberto** (não resolva sozinho; apresente): a nota do BCB de 23/09/2026
  ainda menciona entidades "que não estejam autorizadas ou em processo de autorização", e o art. 88,
  § 6º, continua permitindo que a prestadora que protocolou opere até a decisão. A leitura literal do
  novo art. 91 alcança, a partir de 06/11/2026, contraparte apenas **protocolada**. Até haver
  orientação do usuário ou esclarecimento do BCB:
  - não trate o protocolo como suficiente por si só depois de 06/11/2026; descreva a tensão entre o
    art. 91 (literal) e o art. 88, § 6º (nota do BCB);
  - lembre que a vedação recai sobre a **contraparte do Intex** (a Trace), e alcança o cliente do
    cliente na medida em que o fluxo dele se apoia na liquidez do Intex;
  - se o usuário fixar uma leitura, siga-a e registre-a aqui.
- Pareceres anteriores a 01/10/2026 (BGX, Foxbit, Parfin) citam o marco de 30/10/2026 para o art. 91.
  Em pareceres novos, use **30/10/2026 para o protocolo (art. 88)** e **06/11/2026 para a vedação
  (art. 91)**.

## Autorização — Res. BCB nº 519/2025 (vigente desde 02/02/2026)
Disciplina os processos de autorização de corretoras de câmbio, corretoras/distribuidoras de TVM e
PSAV. Art. 26: processo em duas fases para PSAV já em atividade. Art. 18: cessação em 30 dias após
indeferimento/arquivamento definitivo.

## Câmbio — Res. BCB nº 521/2025 (vigente desde 02/02/2026; arts. 76-C, 82-A e anexos desde 04/05/2026)
Inclui atividades de PSAV no mercado de câmbio (altera as Res. BCB 277, 278 e 279/2022). Art. 76-A
da Res. 277: **pagamento ou transferência internacional com ativos virtuais**, transferências
ligadas a cartão internacional, transferências **de ou para carteira autocustodiada** e compra/venda
/troca de ativos referenciados em moeda fiduciária passam a ser operações de câmbio. Limite de
US$ 100 mil para a SPSAV quando a contraparte não for autorizada a operar em câmbio (art. 29, IV, da
Res. 277). Uso: modelo de negócio com pagamentos internacionais em stablecoin entra no perímetro
cambial.

## Capital mínimo — Res. Conjunta nº 14/2025 e Res. BCB nº 517/2025
- Res. Conjunta 14 (CMN/BCB, DOU de 04/11/2025; alterada pela Res. Conjunta 19/2026): metodologia de
  apuração do capital social integralizado e PL mínimos das instituições autorizadas (não só PSAV),
  por categorias de atividade, com parcela adicional para serviços intensivos em tecnologia e fator
  de captação.
- Res. BCB 517 (DOU de 04/11/2025): procedimentos de apuração; o art. 3º associa as PSAV às
  categorias de intermediação e de custódia e gestão.
- **Faixa de R$ 10,8 a 37,2 milhões**: **não está no texto normativo**. Foi indicada pelo BCB em
  coletiva de 10/11/2025 (diretor de Regulação), como resultado da metodologia. Cite assim: "faixa
  indicada pelo BCB, conforme o conjunto de atividades, a partir da metodologia da Res. Conjunta
  14/2025 e da Res. BCB 517/2025". A comparação com o PL do analisado dimensiona a distância; não
  afirma descumprimento.
- Res. BCB 580/2026: classifica as SPSAV como "Tipo 3", com exigências prudenciais a partir de
  01/01/2027.

## PLD/FT
- **Lei 9.613/1998**, alterada pela Lei 14.478/2022 para incluir as PSAV.
- **Circular BCB nº 3.978/2020**: política, procedimentos e controles de PLD/FT das instituições
  autorizadas; aplica-se às PSAV. A Res. 520 remete à "regulamentação específica" (art. 44, caput;
  art. 88, II, "c"); o anexo da Res. 521 cita a Circular 3.978 expressamente. Não há norma de PLD
  exclusiva para PSAV. Citação correta: **Circular BCB nº 3.978/2020** (não "Resolução").
- **Res. BCB nº 591/2026** (DOU extra de 01/10/2026, vigente na publicação): incluiu no art. 49 da
  Circular 3.978 a comunicação ao Coaf de (IV) câmbio em espécie ≥ US$ 10 mil e (V)
  **transferências de ativos virtuais para ou de carteiras autocustodiadas ≥ US$ 10 mil**; as
  operações de 01/10 a 31/12/2026 devem ser comunicadas no primeiro dia útil de janeiro de 2027.
  Uso: política de PLD de PSAV que não preveja essa comunicação está desatualizada. (A Res. BCB
  588/2026 foi revogada pela 591.)
- **Res. BCB nº 44/2020** (vigente desde 04/01/2021): execução das sanções do CSNU (Lei 13.810/2019),
  incluída a indisponibilidade de ativos.

## Travel Rule — Res. BCB 520, art. 44, parágrafo único, e art. 89
A PSAV deve transmitir à instituição receptora dados do originador e do beneficiário (art. 44, par.
único). Implantação gradual (art. 89): etapa doméstica em até 365 dias da vigência (≈ 02/02/2027),
etapa internacional 365 dias depois; até lá, admitem-se autodeclarações e abordagem baseada em risco
(§ 1º). Obrigatoriedade plena para todas as PSAV autorizadas a partir de **02/02/2028** (§ 3º). Uso:
"Travel Rule ainda não está em vigor" é meia verdade; a obrigação existe e está em implantação.
Ausência hoje não é descumprimento, mas falta de cronograma de ativação é ponto de acompanhamento.

## Obrigações acessórias — IN RFB 1.888/2019 → IN RFB 2.291/2025 (DeCripto)
A IN 2.291 (DOU de 17/11/2025) criou a DeCripto e revogou a IN 1.888 com efeitos a partir de
**01/07/2026** (art. 19, II). Entregas da IN 1.888 provam atividade anterior; a partir de jul/2026,
peça a DeCripto.

## Lei nº 14.478/2022
Diretrizes para a prestação de serviços de ativos virtuais e regulamentação das PSAV; incluiu as PSAV
na Lei 7.492/1986 e na Lei 9.613/1998 e criou o art. 171-A do Código Penal.
