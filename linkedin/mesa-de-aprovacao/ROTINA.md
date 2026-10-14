# Mesa de Aprovação: o que a rotina li-daily precisa seguir

O painel (`index.html`, publicado em https://claude.ai/artifact/MA7ko7oiKnmRLrQirYna5C)
só mostra os slides e prevê a fila. Quem publica no LinkedIn é a rotina li-daily, que
roda no computador do Alexandre. As regras abaixo valem a partir da versão de 14/10/2026
do painel e precisam entrar nas instruções da rotina.

## 1. Publicar todos os slides do carrossel no painel

Hoje a rotina publica só a capa (`img/<id>.jpg`) e o PDF fica no computador, então o
painel mostra uma imagem só. Para cada rascunho de carrossel:

1. Exportar cada página do PDF como JPG, no mesmo tamanho da capa:
   `img/<id>-01.jpg`, `img/<id>-02.jpg`, … `img/<id>-NN.jpg`.
2. Publicar esses arquivos junto com a página, no mesmo publish que já envia a capa
   (arquivos que não forem enviados continuam lá).
3. Gravar no documento `drafts/<id>`:
   - `slides`: a lista dos caminhos, na ordem (`["img/<id>-01.jpg", …]`);
   - `slides_total`: o número de slides;
   - `slides_alt` (opcional): uma descrição por slide, na mesma ordem.

Sem `slides`, o painel mostra a capa com um aviso dizendo quantos slides faltam e onde
está o PDF. Pendente agora: `2026-10-14-2` (Resolução CVM 249, 9 slides).

## 2. Campo `agenda` dos aprovados

O painel grava `agenda` quando o Alexandre aprova ou move um carrossel:

| `agenda`   | Botão no painel                     | Quando sai |
|------------|-------------------------------------|------------|
| `"ja"`     | Publicar já                         | Na próxima rodada (8h, 12h ou 16h), em qualquer dia, à frente de tudo |
| `"quarta"` | Fila de quarta / Aprovar para quarta | Só no dia de `config/carrosseis.dia` (hoje `"quarta"`) |
| ausente    | Aprovar (posts e cortes)            | Regra de sempre |

Ordem no passo D, a cada rodada:

1. **`agenda: "ja"`** (menor `fila` primeiro, depois `criado_em`): publicar nesta rodada,
   sem esperar o próximo dia útil e mesmo que já tenha saído um post hoje, desde que
   tenham passado pelo menos 4 horas do último post. Sai um por rodada. Conta como o
   post do dia: se não saiu nada antes, a fila normal só volta no dia seguinte.
2. **Dia do carrossel** (`config/carrosseis.dia`): se houver aprovado com
   `agenda: "quarta"` (menor `fila`, depois `criado_em`), ele é o post do dia, antes de
   cortes e posts. Se não houver, o dia segue a regra normal.
3. `agenda: "quarta"` **nunca** sai em outro dia da semana.
4. O resto não muda: um post por dia útil, cortes nos dias de `config/cortes`, ordem por
   `fila` e depois `criado_em`, cada linha separada (posts, cortes, carrosséis de quarta).

Ao publicar, o fluxo de sempre: `status: "publicado"`, `publicado_em`, `link_publicado`.
Quando o rascunho deixa de estar aprovado, o painel já limpa `fila` e `agenda`.
