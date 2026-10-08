---
name: decupagem-video
description: Decupagem automática de vídeos, que remove os trechos sem fala (silêncios, pausas entre cenas, respiros no início e no fim) e devolve o vídeo cortado pronto, com áudio e vídeo sincronizados. Pensada para vídeos gerados no HeyGen (avatar com voz sintética), mas serve para qualquer vídeo com fala limpa. Processa um arquivo ou uma pasta inteira. Use sempre que o usuário indicar um ou mais vídeos (.mp4, .mov, .webm, .mkv) ou uma pasta de vídeos e pedir para decupar, cortar silêncios, tirar pausas, remover partes sem fala, "limpar" ou "enxugar" o vídeo, ou disser apenas "decupa esse", mesmo sem pedir um arquivo explicitamente.
---

# Decupagem de vídeo (remoção de trechos sem fala)

O usuário indica vídeos e espera receber **só o vídeo cortado, pronto**. Não peça confirmação antes de processar e não mostre uma análise prévia esperando aprovação: rode, confira e entregue. Perguntas só depois, se o relatório indicar algo estranho (veja "Quando avisar o usuário").

## Por que funciona bem com HeyGen

A voz do avatar HeyGen é sintética e sai com silêncio digital quase absoluto entre as falas. Por isso a detecção por volume (filtro `silencedetect` do ffmpeg) é confiável com limiar rígido (-40 dB). Não é preciso reconhecimento de voz.

## Pré-requisitos (verifique na primeira execução)

- `ffmpeg -version` precisa funcionar. Se não houver ffmpeg, ofereça instalar: macOS `brew install ffmpeg`; Windows `winget install Gyan.FFmpeg` (depois, abrir um terminal novo); Linux `sudo apt install ffmpeg`.
- Python 3.8+. No Windows o comando costuma ser `python` (ou `py`); no macOS/Linux, `python3`.

## Fluxo

1. **Identifique a entrada**: o caminho que o usuário deu (arquivo ou pasta). Se ele disser só "decupa os vídeos" sem caminho, procure vídeos na pasta atual e em `~/Downloads` exportados recentemente, e confirme qual antes de rodar.
2. **Rode o script** (o caminho do script é relativo a esta skill):

   ```bash
   python3 <pasta-da-skill>/scripts/decupar.py "<vídeo ou pasta>"
   ```

   - Arquivo → gera `<nome>_decupado.mp4` ao lado do original.
   - Pasta → processa todos os vídeos (ignora os que já terminam em `_decupado`) e salva em `<pasta>/decupados/`.
   - O original **nunca** é alterado.

   A recodificação leva tempo proporcional à duração do vídeo. Para vídeos acima de ~5 min ou pastas com vários vídeos, **rode em segundo plano** e acompanhe a saída, para não estourar o tempo limite do comando. O script imprime uma linha `Processando ...` por vídeo e, no fim, o relatório em JSON.

3. **Confira o relatório**: `sincronia_ok` precisa ser `true` em todos os vídeos. O script sai com código 1 se algum falhar. Se `sincronia_ok` for `false` ou houver `erro`, não diga que está pronto; investigue (veja "Problemas").
4. **Entregue** com um resumo curto em prosa: onde está o arquivo, duração original → final, tempo removido (%), e as pausas longas sinalizadas, se houver. Em lote, uma linha por vídeo.

## Parâmetros (padrões calibrados para HeyGen)

| Opção | Padrão | O que faz |
|---|---|---|
| `--noise` | `-40` | Limiar de silêncio em dB. Áudio com ruído de fundo: use -35 ou -30. |
| `--min-silence` | `0.6` | Só pausas maiores que isso são cortadas. Pausas naturais entre frases (< 0,6 s) ficam intactas. |
| `--keep-pause` | `0.30` | Cada silêncio cortado vira uma pausa desse tamanho (metade antes, metade depois), para evitar corte seco e sílabas comidas. |
| `--crf` / `--preset` | `20` / `veryfast` | Qualidade e velocidade do H.264. |
| `--dry-run` | — | Só analisa e imprime o relatório, sem cortar. Use para diagnóstico, não no fluxo normal. |
| `--report arquivo.json` | — | Salva o relatório em arquivo. |

Se o usuário pedir um ritmo "mais solto" ou "mais enxuto", ajuste `--keep-pause` (0,5 = mais respiro; 0,15 = bem seco) e `--min-silence`. Se ele fixar uma preferência ("sempre com 0,4 de pausa"), atualize os padrões deste arquivo.

## Como o script garante a sincronia

Com centenas de cortes, um desalinhamento mínimo por corte vira segundos de descompasso no fim. O script evita isso: alinha todo corte à grade de quadros do vídeo e fatia o áudio em blocos de exatamente 1 quadro (`asetnsamples`) antes de selecionar. Testado com 13 cortes em 95 s: 0 ms de diferença entre áudio e vídeo e nenhuma deriva entre o início e o fim. Não troque essa abordagem por `trim`/`concat` com `split`, que acumula quadros na memória e estoura em vídeos longos.

## Quando avisar o usuário

- **Pausas longas internas (≥ 3 s)** aparecem em `silencios_longos_3s`. Nos vídeos HeyGen com texto na tela, uma pausa longa pode ser proposital (tempo de leitura). Elas são cortadas como as demais. Liste os timecodes no resumo e ofereça refazer com `--min-silence` maior que a pausa, se ele quiser preservá-las.
- **Quase nada removido (< 2 %)** num vídeo que deveria ter pausas: provavelmente há música de fundo ou ruído. Sugira exportar do HeyGen sem trilha musical, ou tente `--noise -30`.
- **Mais de 40 % removido**: confira com `--dry-run` se o limiar não está comendo fala baixa antes de entregar.

## Problemas

- `sincronia_ok: false`: verifique se o vídeo tem taxa de quadros variável (`ffprobe` → `avg_frame_rate` ≠ `r_frame_rate`). Se tiver, converta antes para taxa constante (`ffmpeg -i in.mp4 -r 30 -c:a copy cfr.mp4`) e rode de novo.
- Erro de opção desconhecida envolvendo `filter_complex`: o script escolhe `-/filter_complex` (ffmpeg 7+) ou `-filter_complex_script` (ffmpeg 5–6) pela versão detectada. Se a detecção falhar, ajuste a função `filter_args` em `decupar.py`.
- Lentidão em vídeos longos: no macOS dá para acelerar trocando `-c:v libx264` por `-c:v h264_videotoolbox -b:v 6M` (codificador de hardware), ao custo de arquivos um pouco maiores.
