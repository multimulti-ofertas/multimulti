# MultiMulti: robô de achadinhos da Shopee

Todo dia, sozinho:

| Horário (Cuiabá) | O que acontece |
|---|---|
| 07:00 | Busca os mais vendidos da Shopee no tema do dia, escolhe 6, gera link de afiliado, arte, story, Reels e legenda, e atualiza a vitrine |
| 08:00 · 15:00 · 20:00 | Posta 2 stories por vez (os 6 produtos do dia) |
| 12:00 | Posta no feed do Instagram a arte do produto principal |
| 18:00 · 21:00 | Posta um Reels por vez (2º e 3º produtos) |
| Segunda 07:00 | Renova o token do Instagram |

**Vitrine (link da bio):** https://multimulti-ofertas.github.io/multimulti/
Cada post diz "Link na bio → produto nº X", e na vitrine o produto aparece com esse número.

Temas: segunda carro · terça ferramentas · quarta cuidado · quinta estilo · sexta a domingo top (mistura).

## Configuração (uma vez só)

### 1. Ligar a vitrine
Settings → Pages → **Source: GitHub Actions**.

### 2. Secrets
Settings → Secrets and variables → Actions → **New repository secret**:

| Nome | De onde vem |
|---|---|
| `SHOPEEAPPID` | Painel de afiliados Shopee → Open API |
| `SHOPEESECRET` | Painel de afiliados Shopee → Open API |
| `IGUSERID` | App da Meta → Instagram → ID da conta |
| `IGTOKEN` | App da Meta → Instagram → gerar token |
| `GH_PAT` (opcional) | Token do GitHub com permissão de Secrets, para renovar o `IG_TOKEN` sozinho |
| `ANTHROPIC_API_KEY` (opcional) | Para títulos e legendas escritos por IA |

Sem a Shopee configurada, o robô só pula o dia (não dá erro).

## Testar
Actions → **Gerar ofertas do dia** → Run workflow → marque **demo**. Depois baixe o arquivo `teste-demo` no fim da página da execução.

Postar na mão: Actions → **Postar no Instagram** → Run workflow → escolha feed, reel ou story.

## Mudar regras
Tudo fica em `robo/config.py`: palavras buscadas, nota mínima, vendas mínimas, desconto mínimo, quantos produtos por dia.

## Estrutura
- `robo/shopee.py`: API de afiliados da Shopee
- `robo/gerar.py`: escolhe os produtos e monta tudo
- `robo/arte.py`, `robo/reel.py`: arte do feed, story e Reels (padrão laranja/preto)
- `robo/texto.py`: títulos e legendas (IA opcional)
- `robo/instagram.py`, `robo/postar.py`: publicação pela API oficial do Instagram
- `docs/`: vitrine (`index.html` + `produtos.json`) e mídias publicadas
