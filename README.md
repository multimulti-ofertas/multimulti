# MultiMulti: robô de achadinhos da Shopee

Todo dia, sozinho:

| Horário (Cuiabá) | O que acontece |
|---|---|
| 07:00 | Busca os mais vendidos da Shopee no tema do dia, escolhe 4, gera link de afiliado, arte, story, Reels e legenda, e atualiza a vitrine |
| 12:00 | Posta no feed do Instagram a arte do produto principal |
| 19:00 | Posta o Reels do segundo produto |
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
| `SHOPEE_APP_ID` | Painel de afiliados Shopee → Open API |
| `SHOPEE_SECRET` | Painel de afiliados Shopee → Open API |
| `IG_USER_ID` | App da Meta → Instagram → ID da conta |
| `IG_TOKEN` | App da Meta → Instagram → gerar token |
| `GH_PAT` (opcional) | Token do GitHub com permissão de Secrets, para renovar o `IG_TOKEN` sozinho |
| `ANTHROPIC_API_KEY` (opcional) | Para títulos e legendas escritos por IA |

Sem a Shopee configurada, o robô só pula o dia (não dá erro).

## Testar
Actions → **Gerar ofertas do dia** → Run workflow → marque **demo**. Depois baixe o arquivo `teste-demo` no fim da página da execução.

Postar na mão: Actions → **Postar no Instagram** → Run workflow → escolha feed ou reel.

## Mudar regras
Tudo fica em `robo/config.py`: palavras buscadas, nota mínima, vendas mínimas, desconto mínimo, quantos produtos por dia.

## Estrutura
- `robo/shopee.py`: API de afiliados da Shopee
- `robo/gerar.py`: escolhe os produtos e monta tudo
- `robo/arte.py`, `robo/reel.py`: arte do feed, story e Reels (padrão laranja/preto)
- `robo/texto.py`: títulos e legendas (IA opcional)
- `robo/instagram.py`, `robo/postar.py`: publicação pela API oficial do Instagram
- `docs/`: vitrine (`index.html` + `produtos.json`) e mídias publicadas
