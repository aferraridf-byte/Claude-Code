---
name: video-heygen-completo
description: Produz o vídeo inteiro com avatar HeyGen, de ponta a ponta e sem trabalho manual no site, em quatro etapas. 1) Roteiro: com a skill treinamento-heygen quando for curso ou treinamento. 2) Lançamento: envia o roteiro pela API do HeyGen, um vídeo por módulo, e acompanha a renderização. 3) Saída: baixa o MP4 e decupa com a skill decupagem-video. 4) Edição: anima com a skill animacao-aulas e entrega o MP4 final. Use sempre que o usuário pedir para "fazer o vídeo completo", "gerar o vídeo no HeyGen", "lançar/mandar o roteiro pro HeyGen", "do roteiro ao vídeo final", "produzir o módulo/curso em vídeo" ou "automatizar o HeyGen", ou quando ele aprovar um roteiro e quiser o vídeo pronto. Para só escrever roteiro, só decupar ou só animar um MP4 que já existe, use direto a skill da etapa.
---

# Vídeo HeyGen completo (roteiro → HeyGen → decupagem → edição)

Esta skill **orquestra** as outras: não reescreve roteiro, decupagem nem animação. Cada etapa usa a skill dona dela; aqui ficam o lançamento automático no HeyGen, o encadeamento e as regras de passagem entre etapas.

```
tema/briefing ─► [1] roteiro.json ─► (aprovação) ─► [2] HeyGen API ─► [3] download + decupagem ─► [4] edição ─► MP4 final
                 treinamento-heygen                   scripts/heygen.py     decupagem-video            animacao-aulas
```

**Só há uma parada obrigatória: a aprovação do roteiro.** Gerar no HeyGen gasta créditos, por isso o "ok" do usuário ao roteiro final é o que autoriza o lançamento. Depois disso, siga até o fim sem pedir confirmação. Pare apenas se algo falhar ou se o resultado tiver algum ponto da seção "Quando parar e avisar".

`SKILL_DIR` = pasta onde este SKILL.md está. O script é `"$SKILL_DIR/scripts/heygen.py"`: só usa a biblioteca padrão do Python, então não precisa de `pip install`. No Windows, use `python` (ou `py`) no lugar de `python3`.

## Configuração (uma vez por máquina)

1. **Chave da API.** O usuário cria a chave em https://app.heygen.com/developers/api (permissão completa, ou personalizada com escrita em vídeos e leitura em avatares, vozes e usuário) e grava na variável de ambiente `HEYGEN_API_KEY`, **digitando ele mesmo no terminal**. Nunca peça para colar a chave no chat, nunca a escreva em arquivo do projeto e nunca a mostre em comando.
   - macOS/Linux: acrescentar `export HEYGEN_API_KEY="..."` ao `~/.zshrc` ou `~/.bashrc` e abrir um terminal novo.
   - Windows: `setx HEYGEN_API_KEY "..."` e abrir um terminal novo.
   - Sessão na nuvem (claude.ai/code): a chave entra como variável de ambiente nas configurações do ambiente (menu do ambiente na barra de título > Edit), e a rede precisa liberar `api.heygen.com` e `heygen.ai` (downloads). Vale a partir da próxima sessão.
   - A cobrança da API é separada da assinatura do site. Se `verificar` mostrar saldo zero, avise o usuário.
2. **Avatar e voz:**
   ```bash
   python3 "$SKILL_DIR/scripts/heygen.py" avatares            # looks privados: digital twin do Alexandre etc.
   python3 "$SKILL_DIR/scripts/heygen.py" vozes --privadas    # vozes clonadas; sem --privadas lista as públicas em português
   python3 "$SKILL_DIR/scripts/heygen.py" configurar --avatar <look_id> [--voz <voice_id>] [--engine avatar_v]
   ```
   - Mostre a lista e pergunte qual look usar só se houver mais de um candidato óbvio. Sem `--voz`, o vídeo sai com a voz padrão do avatar, que no digital twin é a voz clonada dele.
   - Use `--engine` apenas com um valor que esteja em `engines=` do look escolhido. Sem ele, o HeyGen usa o Avatar IV.
   - Para o fundo, siga o que a skill animacao-aulas pede em `references/entrada-heygen.md`. `--fundo "#RRGGBB"` ou `--fundo <url-de-imagem>` só aparece com `--remover-fundo sim` em avatar treinado com matting. Sem `--fundo`, fica o fundo da gravação.
   - Siglas com pronúncia errada recorrente (Coaf, Gafi, PLD): crie um glossário em Brand Kit no HeyGen e grave com `--glossario <id>`.
   - A configuração fica em `$SKILL_DIR/config.json`, que está no `.gitignore`. Modelo em `config.example.json`.
3. **Conferir:** `python3 "$SKILL_DIR/scripts/heygen.py" verificar`. Ele confere a chave, o saldo, o ffmpeg, a skill de decupagem e se o avatar e o engine são compatíveis. Precisa sair com código 0 antes do primeiro lançamento.

## Etapa 1: roteiro

- **Curso, treinamento ou módulo de LMS:** siga a skill `treinamento-heygen` (estrutura → apostila → roteiro → questões → `gerar_pacote.py`). O JSON que ela monta (`curso.json`) é a entrada desta skill. Não é preciso converter nada.
- **Outro tipo de vídeo** (comunicado, institucional, explicação curta): escreva `roteiro.json` no mesmo formato, com um módulo por vídeo. Siga as regras de fala de `treinamento-heygen/references/guia_roteiro.md`: números e normas por extenso, frases curtas, sem parênteses nem barras, pronúncia das siglas.
  ```json
  {"curso": "Comunicado X", "modulos": [
    {"n": 1, "titulo": "Título curto", "cenas": [
      {"fala": "texto que o avatar fala", "tela_titulo": "até 6 palavras", "tela_destaques": ["até 3, de até 6 palavras"]}]}]}
  ```
- Apresente o roteiro e a duração estimada por módulo e **aguarde o ok**. Ajustes pedidos voltam para esta etapa.

## Etapa 2: lançamento no HeyGen, saída e decupagem

Projeto em `<pasta_projetos>/<curso-slug>` (padrão `~/Videos/HeyGen/...`), salvo se o usuário indicar outra pasta.

1. **Ensaio (sem custo):** `python3 "$SKILL_DIR/scripts/heygen.py" gerar roteiro.json -p "<projeto>" --dry-run`. Ele valida o roteiro e mostra o que seria enviado. Se houver alerta de número, sigla ou parêntese na fala, corrija o roteiro antes de lançar. São erros que o avatar lê literalmente e custariam uma regravação.
2. **Lançar, aguardar, baixar e decupar** de uma vez, **em segundo plano**, porque a renderização no HeyGen leva de minutos a horas:
   ```bash
   python3 "$SKILL_DIR/scripts/heygen.py" produzir roteiro.json -p "<projeto>" > "<projeto>/pipeline.log" 2>&1
   ```
   Acompanhe o log. O que ele faz:
   - envia **um vídeo por módulo** (tipo `studio`, uma cena de avatar por cena do roteiro). Só a `fala` vai para o HeyGen; o texto de tela fica para a edição;
   - consulta o status a cada 30 s, respeitando o limite de requisições, e baixa cada MP4 pronto em `<projeto>/01_heygen/M01_<titulo>.mp4`;
   - roda `decupagem-video/scripts/decupar.py` em cada um e salva em `<projeto>/02_decupado/M01_<titulo>_decupado.mp4`;
   - grava tudo em `<projeto>/estado.json`: video_id, status, durações e o relatório da decupagem.
3. **Retomar é seguro.** `gerar` nunca reenvia um módulo que já tem `video_id`, a não ser que tenha falhado. Se a sessão cair ou o tempo limite estourar (código 2), rode `aguardar -p "<projeto>"` e depois `decupar -p "<projeto>"`. Nada é gerado de novo. Use `--refazer --modulos N` **somente** quando o usuário pedir para regravar, porque gasta créditos.
4. **Conferir** com `python3 "$SKILL_DIR/scripts/heygen.py" status -p "<projeto>"`. Cada módulo precisa terminar `completed`, com arquivo decupado e `sincronia_ok: true`. Os parâmetros da decupagem são os padrões da skill decupagem-video. Para outro ritmo, use `decupar -p ... --refazer --args-decupagem "--keep-pause 0.4"`.

## Etapa 3: edição

- **Aula, curso ou treinamento:** siga a skill `animacao-aulas`, um projeto por módulo, com estas entradas:
  - **vídeo:** o MP4 de `02_decupado/` (não o bruto de `01_heygen/`). Avise àquela skill que os silêncios já foram removidos a pedido do usuário. Isso não conta como "cortar a fala": a sincronia por palavra é feita sobre o arquivo decupado;
  - **roteiro:** `<projeto>/roteiro.json`, que vira a pauta das animações;
  - **marca:** a que o usuário pediu; sem indicação, a padrão daquela skill.
  
  Siga todas as regras e checagens de QA da `animacao-aulas`. Esta skill não as substitui.
- **Outro tipo de vídeo:** pergunte uma única vez qual skill de edição usar. Se ele não quiser edição, o entregável é o decupado.
- A primeira configuração da `animacao-aulas` (`config.env`, `MOTOR_TEMPLATE`) é dela. Se faltar algo, resolva por lá antes de seguir.

## Entrega

Em prosa curta:
- caminho absoluto do MP4 final de cada módulo (e da pasta do projeto);
- por módulo: duração estimada → duração no HeyGen → duração decupada → duração final;
- **calibração:** palavras por minuto reais = palavras da fala ÷ (duração no HeyGen ÷ 60). Se ficar longe de 140, sugira o novo `--ppm` para o `gerar_pacote.py` da treinamento-heygen;
- alertas que restaram (pausas longas cortadas, divergências fala × roteiro, selo de IA com texto-modelo etc.).

## Quando parar e avisar

- `verificar` falhou (chave, saldo, avatar ou engine): diga exatamente o que falta. Não tente contornar.
- Módulo `failed` no HeyGen: mostre `failure_code` e `failure_message`. Se a causa for o roteiro (texto, cena longa demais), corrija e relance só esse módulo. Se for do HeyGen (renderização), relance uma vez com `gerar --modulos N` e, se falhar de novo, avise.
- Duração no HeyGen mais de 30% acima ou abaixo da estimada: provável pronúncia estranha, trecho pulado ou velocidade da voz errada. Mostre ao usuário antes de animar.
- A decupagem removeu menos de 2% ou mais de 40%, ou `sincronia_ok` deu false: siga a seção "Quando avisar o usuário" da skill decupagem-video.
- Na edição, a transcrição diverge do roteiro em norma, número ou prazo: vale a regra da `animacao-aulas` (o usuário decide antes de animar).

## Regras fixas

- **Chave só na variável de ambiente.** Nunca no chat, em arquivo, em log ou em commit.
- **Não gerar de novo sem pedido.** Cada vídeo gasta créditos. O `estado.json` é a fonte da verdade sobre o que já foi enviado.
- **Conteúdo só do roteiro aprovado.** Nada é acrescentado à fala depois do ok. Mudança de texto volta para a Etapa 1 e é aprovada de novo.
- **Original nunca é sobrescrito.** O bruto do HeyGen fica em `01_heygen/`, o decupado em `02_decupado/` e o final na saída da skill de edição.
- **Caminhos absolutos** nos comandos, com aspas.

## Referência rápida do script

| Comando | O que faz |
|---|---|
| `verificar` | confere chave, saldo, ffmpeg, decupagem, avatar e engine |
| `avatares [--publicos]` / `vozes [--privadas] [--idioma X]` | lista IDs para configurar |
| `configurar --avatar ID [--voz ID] [--engine E] [--velocidade 1.0] [--locale pt-BR] [--fundo X] [--remover-fundo sim] [--glossario ID] [--pasta-projetos P]` | grava `config.json` |
| `gerar ROTEIRO -p PASTA [--modulos 1,3] [--dry-run] [--refazer]` | valida e envia, um vídeo por módulo |
| `aguardar -p PASTA [--intervalo 30] [--timeout 10800]` | acompanha e baixa (código 2 = tempo limite, rodar de novo) |
| `decupar -p PASTA [--args-decupagem "..."] [--refazer]` | decupa o que já foi baixado |
| `status -p PASTA` | resumo por módulo |
| `produzir ROTEIRO -p PASTA [...]` | gerar + aguardar + decupar |

API usada: HeyGen v3. `POST /v3/videos` com `type: "studio"` (até 50 cenas por vídeo), `GET /v3/videos/{id}` (status `pending`/`processing`/`completed`/`failed`, `video_url`), `GET /v3/avatars/looks`, `GET /v3/voices`, `GET /v3/users/me`. Se o HeyGen mudar a API, a referência fica em developers.heygen.com/llms.txt. Ajuste as funções `payload_modulo` e `cmd_aguardar`.
