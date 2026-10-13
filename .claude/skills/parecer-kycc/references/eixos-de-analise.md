# Eixos de análise do cliente do cliente

Cada eixo traz o que conferir, onde costuma estar no dossiê e as armadilhas que já apareceram
em pareceres anteriores (BGX, Foxbit OTC, Parfin). A lista não é um formulário: um achado só vai
para o parecer se mudar a leitura de risco, uma condicionante ou uma limitação.

Marque cada dado como **[D]** (extraído de documento, com a peça identificável) ou **[E]**
(estimativa sua, com a conta explicitada). Nunca produza um percentual ou valor sem base: se o
relatório não traz denominador, diga que não foi possível estimar.

## Sumário
1. Peças que normalmente chegam
2. Classificação de origem (o parecer da Trace)
3. Regulatório e marco temporal
4. Modelo de negócio e coerência entre fontes
5. Societário, beneficiário final e governança
6. Financeiro e capital
7. Volume (TPV declarado x observado)
8. Carteiras e análise on-chain
9. Programa de PLD/FT e evidência de execução
10. Background (sanções, PEP, mídia, processos)
11. Integridade documental
12. Contrapartes e terceiros relevantes

---

## 1. Peças que normalmente chegam

Um dossiê completo, enviado pela Trace, costuma trazer:

| Grupo | Peças típicas |
|---|---|
| Parecer de origem | "Análise de Background Check" / KYB da Trace, com classificação (às vezes score, ex. "33/100", modelo "Pix Inc v1.0"); ficha do Pipefy |
| Societário | Cartão CNPJ, QSA, contrato social e última alteração registrada (Junta), certidão/ficha da Junta, cap table, organograma, documentos e CVs dos sócios/administradores |
| Financeiro | Balanço e DRE (último exercício encerrado), balancete, declaração de faturamento, extratos bancários (às vezes em print), extrato de exchange |
| Carteiras | Atestado/declaração de controle de wallets, prints de custódia, relatórios de KYT (Chainalysis, Crystal, TRM, Elliptic) |
| Programa PLD/FT | Política de PLD/FT, AIR (avaliação interna de risco), manuais, contratos e evidências de ferramentas (KYC, screening, KYT, Travel Rule), exemplos de CDD |
| Background | Relatórios BigDataCorp/BeCompliance/outros, por PJ e por sócio |
| Regulatório | Recibos/listagem de entregas IN RFB 1.888 ou DeCripto (IN RFB 2.291/2025), declaração de intenção de pedido de autorização |
| Comunicação | E-mails de pendência entre a Trace e o cliente, transcrição de call de compliance |

Use o inventário (`scripts/inventario.py`) para saber o que chegou. O que **faltar** e for
relevante vira limitação (seção 5) e, se for decisivo, condicionante. Relatórios citados pela Trace
mas não compartilhados com o Intex são uma falta: registre que "os relatórios-fonte não foram
compartilhados".

## 2. Classificação de origem

O parecer da Trace é o ponto de partida, não a conclusão. Sempre:

- registre a classificação de origem (e o score/modelo, se houver) na ficha;
- confira se ela se apoiou em **documentos superados** (contrato social anterior à última
  alteração, DF de exercícios antigos, política vencida);
- confira se ela **incorporou** screening de carteiras, análise on-chain, ofícios ou apontamentos de
  supervisão que estão no próprio dossiê;
- refaça as contas dela (conversões de câmbio, reconciliação de volume). Em BGX, a reconciliação
  da Trace tinha falha de método;
- diga com clareza se **diverge** e por quê, com fatores verificáveis. Divergir não é acusar:
  explique que a divergência não decorre de ilicitude apurada, quando for o caso.

## 3. Regulatório e marco temporal

Pontos fixos (confira o texto e os artigos em `normas.md`):

- O Intex é provedor de liquidez por conta própria; a Trace é PSAV contratante; o objeto é cliente da
  Trace. O cliente do cliente pode ser PSAV não autorizada em período de transição.
- **Prazo em curso não é irregularidade.** Antes de 30/10/2026, a ausência de autorização PSAV
  ou de protocolo **não é achado desfavorável**; é pendência com prazo. O que se pede antes do marco
  é **previsibilidade**: entidade requerente, modalidade, escritório, data prevista. O comprovante de
  protocolo vira condicionante **temporal** (T1) exigível no marco. Depois de 30/10/2026, a falta de
  protocolo é impeditiva.
- O inverso também vale: **exigibilidade futura não neutraliza documento vencido**, apontamento de
  supervisão já formalizado nem obrigação acessória vigente. Separe, com datas, o que venceu do que
  ainda corre; um "Quadro de vigências" ajuda quando há vários prazos.
- Calcule e escreva os **dias restantes** até o marco, a partir da data do parecer, e a margem entre a
  data prevista de protocolo e o marco.
- Confira o histórico de entregas da IN RFB 1.888 / DeCripto como prova de atividade anterior a
  02/02/2026 (relevante para o regime de transição) e a continuidade das entregas.
- Ofício ou apontamento do BCB citado em qualquer peça (até em manual interno do analisado) é
  achado próprio: peça cópia do ofício e da resposta.

## 4. Modelo de negócio e coerência entre fontes

- Compare a descrição do negócio no KYB, no e-mail, na política, no site, no CNAE e no contrato
  social. Descrições divergentes (corretagem OTC × pagamentos internacionais × provisão de liquidez ×
  serviços de pagamento) são achado.
- Pagamentos internacionais/transfronteiriços com ativos virtuais entram no perímetro cambial (Res.
  BCB 521/2025): sinalize.
- CNAE sem atividade de ativos virtuais (ex.: 6619-3/02, correspondentes) é ponto de atenção para a
  autorização.
- Modelos B2B2C/"VASP-as-a-Service" e provisão de liquidez a outras VASPs ampliam a cadeia: o
  cliente do cliente tem clientes que podem ser PSAVs não autorizadas. Pergunte quem são e se ele
  aplica o mesmo filtro de autorização.

## 5. Societário, beneficiário final e governança

- Contrato social: a última alteração registrada bate com o que a Trace usou? Sede, filiais, CNPJ
  matriz/filial, objeto social, administradores.
- QSA × cap table × contrato: participações coincidem? Beneficiário final por participação (corte de
  25%) e por controle, inclusive em holdings e no exterior.
- **Histórico de outra gestão**: CNPJ antigo, razões sociais anteriores e entregas fiscais desde
  anos atrás podem pertencer a controladores anteriores. Confira se o *track record* invocado é da
  gestão atual (data de entrada dos sócios, compra de quotas).
- Organograma não oficial/não assinado: válido para fins declaratórios, registre.
- **Acumulação de funções**: sócio relevante que também é administrador e CCO/Diretor de
  Compliance; ou compliance terceirizado a escritório ligado a sócio. Não é vedado, mas reduz a
  independência da segunda linha e tende a ser exigência no processo de autorização.

## 6. Financeiro e capital

- Qual é o último exercício encerrado? DF auditadas ou não? Quem assinou (contador com CRC e UF,
  administradores)?
- Sinais de qualidade: saldos com natureza invertida, ausência de grupo de PL, ausência de despesa de
  pessoal, colunas que não reconciliam, "prejuízo do exercício" com valor positivo, receita que diverge
  da declaração de faturamento.
- **Ativos de terceiros** (valores em custódia, clientes) lançados no ativo próprio levantam dúvida
  sobre segregação patrimonial.
- **PL × capital referencial**: o BCB divulgou faixa de R$ 10,8 a 37,2 milhões conforme o conjunto
  de atividades (Res. Conjunta 14/2025 e Res. BCB 517/2025, ver `normas.md`). A comparação
  **dimensiona a distância, não afirma descumprimento** de requisito ainda não aferido. O ponto que
  vale hoje para o Intex é se a entidade tem capacidade financeira compatível com o volume declarado.
- PL negativo ou capital irrisório com volume alto: o limite não pode ser calibrado por capacidade
  própria; se houver suporte intragrupo, peça a evidência.
- Quadro de pessoal: compare colaboradores declarados com vínculos em background (ex.: "sem
  vínculos" na BigDataCorp) e despesa de pessoal na DRE; estrutura de compliance declarada precisa
  de gente que a execute.
- Take rate (receita ÷ volume) atípico para o modelo declarado é sinal a explorar [E].

## 7. Volume (TPV declarado x observado)

Monte uma tabela Fonte | Valor | Leitura com todas as medidas disponíveis: TPV declarado, extratos
bancários (entradas e saídas), extrato de exchange, balancete (débitos em ativos de terceiros),
volume em USDT do relatório on-chain, KPI reports.

- Declarações públicas (CV, site, imprensa, pitch) entram na tabela como [D] de baixa
  confiabilidade, nunca como corroboração.
- Converta moedas com a taxa e a data explícitas, marcando [E].
- Volume observado **maior** que o declarado é compatível com intermediação, mas impede calibrar
  limite: peça recalibragem. Volume declarado como **projeção** sem lastro: aceite só o patamar
  corroborado.
- Extrato em **print** não identifica titularidade nem período com segurança; peça PDF do banco.
- Conta de passagem (saldo final residual) é coerente com provisão de liquidez, mas confirme o titular.

## 8. Carteiras e análise on-chain

O Intex não refaz o screening: o analista que envia o dossiê já fez a triagem inicial (Crystal
Intelligence) para afastar relação com ilícito. O parecer **lê** os relatórios recebidos e a
declaração de carteiras, e responde: as carteiras são de quem se diz, o que os relatórios realmente
dizem, e o que eles não cobrem.

- **Validação formal**: rode `scripts/validar_enderecos.py` em todos os endereços (Base58Check,
  EIP-55, homóglifos) e confira que coincidem caractere a caractere entre atestado, KYB, relatórios e
  declarações. Registre o resultado no achado de integridade.
- **Natureza da custódia**: autocustódia efetiva (cofre/MPC próprio) × endereço de depósito na
  exchange atribuído à conta do cliente × endereço de saque da exchange em **pool compartilhado**.
  Só os dois primeiros servem de âncora de atribuição; o pool não é estável nem exaustivo.
- **"Low" não é baixo risco quando o endereço é de VASP**: endereço hospedado em exchange não gera
  exposição calculada. Diga que é ausência de dado.
- **Exposição direta × indireta**; **limiar de tolerância zero** ("> 0%") dispara com qualquer valor;
  sem denominador e número de saltos não há magnitude. Não estime percentual sem base.
- **Rebaixamento por recategorização** (ex.: ALTO → BAIXO porque o endereço passou a ser
  "Exchange") não é remediação: peça evidência de remediação ou reprocessamento.
- **Divergência entre ferramentas** (ex.: Crystal 20% × Chainalysis HIGH): registre as duas, a data
  de cada uma e o que explica a diferença; exposição antiga (fora da janela de 12 meses) atenua, não
  apaga.
- Prints de painel revelam carteiras ou redes **não declaradas**: são endereços sob controle do
  cliente nunca triados (achado + gatilho).
- Cobertura: quantos endereços, quantas redes, frente ao volume declarado. Triagem única, sem
  monitoramento contínuo, é limitação.
- Ativos e tags relevantes: concentração em USDT, tag pública (Tronscan/Arkham) com o nome do
  cliente, interação com mixers (ex.: Wasabi), devoluções de fundos.

## 9. Programa de PLD/FT e evidência de execução

- **Vigência da política**: versão, data de aprovação, periodicidade de revisão que ela própria
  fixa. Calcule se está vencida e há quanto tempo.
- **Arcabouço citado**: menciona a Lei 14.478/2022, as Res. BCB 519/520/521/2025 e a norma de PLD
  aplicável (ver `normas.md`)? Erros de citação ("Resolução Bacen 3.978" em vez de Circular BCB
  3.978/2020) são achado de qualidade.
- **AIR**: existe, está datada, pontua as dimensões (produtos, clientes, canais, regiões,
  parceiros)? Parâmetros de seleção e monitoramento definidos?
- **Ferramentas**: KYC/KYB, screening (sanções/PEP/mídia), KYT on-chain, monitoramento
  transacional em moeda fiduciária. Atenção: **KYT on-chain não é monitoramento transacional
  fiduciário.** Contrato com fornecedor prova contratação, não uso; e confira se o **módulo
  alegado** (ex.: Travel Rule) está de fato no contrato.
- **Independência das ferramentas**: ferramenta de compliance fundada por sócio ou parte
  relacionada (ex.: base de endereços de risco própria) reduz a independência do controle.
- **Evidência de execução**: exemplos de CDD com dupla alçada, alertas tratados, dossiês,
  comunicações ao COAF; monitoramento contínuo ativo nos exemplos. Exemplo com campos vazios ou em
  ambiente de teste ("sandbox", "preview") é achado.
- **Travel Rule**: capacidade declarada × evidência. Verifique em `normas.md` se já há obrigação
  vigente antes de tratar a ausência como falha.
- Comitê de compliance: composição, periodicidade, atas.

## 10. Background

- Sanções, PEP e mídia adversa da PJ, sócios e administradores. Se a Trace afirma "nada consta"
  mas não compartilhou os relatórios-fonte, registre.
- Processos: natureza (penal, regulatória, cível, consumo, trabalhista, fiscal), polo e status.
  Advogado que figura como patrono não é parte. Execução fiscal em curso, notificações por
  pagamento indevido e disputas com bancos (derisking, encerramento de conta) são sinais
  relevantes para banco que avalia exposição indireta.
- Empresas relacionadas e nomes anteriores (ex.: outra razão social do mesmo grupo em processo).

## 11. Integridade documental

Peças da origem às vezes trazem dados de **outros clientes da Trace** (cartões de Pipefy, listas):
desconsidere-os e registre isso em Limitações.


Confira e registre num único achado: datas incoerentes (documento datado depois do nome do
arquivo, "30/12/1899"), texto-modelo não preenchido, assinaturas faltantes ou por um só
administrador, CNPJs divergentes entre peças, CRC sem UF, documentos em papel timbrado de outra
empresa, prints sem identificação de titular.

## 12. Contrapartes e terceiros

- Bancos, exchanges e provedores de liquidez do cliente do cliente (aparecem em balancete, extrato,
  call): algum foi apenado por operar com intermediador não autorizado (ex.: Banco Topázio, Copas,
  11/05/2026)? O padrão de exposição é o mesmo?
- Exchange estrangeira concentrando custódia e execução.
- Relação anterior entre a PSAV e o analisado: KYT, transações ou screening com data anterior ao
  onboarding podem indicar operação antes da aprovação. Pergunte.
- Clientes do cliente que sejam PSAVs (modelos B2B/B2B2C): a cadeia se alonga.
