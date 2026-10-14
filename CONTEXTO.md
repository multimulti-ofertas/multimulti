# Contexto do projeto MultiMulti (para continuar em outra conversa)

Atualizado em 14/out/2026, 14:20 (Cuiabá). Ao abrir uma conversa nova com o Claude, diga:
"Leia o CONTEXTO.md do repositório multimulti-ofertas/multimulti e vamos continuar."

## O que é
Perfil de achadinhos masculinos da Shopee (carro, ferramentas, cuidado, estilo) com link de afiliado.
Instagram @multimulti.ofertas · Página do Facebook "MultiMulti Ofertas".
Mercado Livre foi descartado. Grupo/canal do WhatsApp pausado até ter um chip separado.

## Situação agora (14/out)
- **Rotina LIGADA e postando no Instagram E na Página do Facebook** (Facebook desde 14/out 14:15). 1º post do feed saiu em 14/out às 10:46 (nº 1, Máquina de barbear 3 em 1).
- Produtos de 14/out: nº 1 a 8 (feed: 1 e 2 · Reels: 3 e 4 · stories: todos). Planilha atual rende ~5 dias (até ~19/out).
- Esperando a Shopee liberar a Open API (prazo até sex 16/out, resposta no **Outlook**).

## Como funciona (robô = GitHub Actions deste repositório, horário de Cuiabá)
| Horário | O que acontece | Onde mudar |
|---|---|---|
| 06:25 | "Gerar ofertas do dia": escolhe 8 produtos, monta feed/story/Reels/legendas, atualiza a vitrine | .github/workflows/gerar.yml |
| 08:00 e 20:00 | Post no feed (+ story) | robo/config.py → ROTINA |
| 12:00 e 21:00 | Reels (+ story) | robo/config.py → ROTINA |
| 08:00 a 22:00 | 1 story por hora (os 8 produtos se revezam) | robo/config.py → ROTINA |
| Segunda 06:00 | Renova o token do Instagram (só salva se existir o secret GH_PAT) | token.yml |
- "Postar no Instagram" roda de hora em hora (xx:50) e publica o que a tabela ROTINA manda para aquela hora.
  São 19 publicações/dia; limite da conta é 100 por 24h.
- Chave geral: `POSTAR_NO_INSTAGRAM` em robo/config.py (False = só monta produtos e vitrine, não posta).
- Se uma publicação falhar no meio, o que já saiu fica marcado (não repete post).
- Temas: segunda carro · terça ferramentas · quarta cuidado · quinta estilo · sexta a domingo top (mistura).
  Se a planilha não tem o tema do dia, completa com outros temas.

## De onde vêm os produtos
- **Sem a API da Shopee (ainda):** planilhas .csv na pasta `ofertas/`. Como baixar: painel de afiliados →
  Oferta → Oferta de produto → buscar → "Selecione todos os produtos nesta página" → "Obter Link em Massa".
  Mandar o arquivo para o Claude colocar em `ofertas/`.
- Regras: nunca repete produto (nem um muito parecido de outra loja), só 1 de cada tipo por dia,
  tira palmilhas/lentes/feminino. A foto é pega na página da Shopee; o produto é recortado do fundo branco.
- Nomes curtos e limpos: `texto.nome_curto` (acentos, sem "profissional/original/códigos").
- Quando acabar a planilha, o "Gerar ofertas do dia" falha com "Acabaram os produtos novos".
- Quando a API sair (secrets SHOPEEAPPID e SHOPEESECRET), ela passa a ter prioridade sozinha.

## Visual (feed, story, Reels e vitrine)
- Inspirado num Reels de referência ("Websites in 2026"): fundo quase preto, produto recortado flutuando e
  inclinado com brilho laranja, nome em maiúsculas condensadas (Barlow Condensed), preço grande laranja,
  círculo com o número, "LINK NA BIO →". Story também diz "ou responde o story que eu te mando o link".
- Reels: cena contínua de 10s (chamada → produto flutuando → preço → "Link na bio nº X").
- Música nos Reels (desde 14/out): trechos de 10s em robo/musicas/*.m4a (Coleção de Sons da Meta), já cortados
  no drop, com fade e volume -14 LUFS. robo/musica.py alterna pelo nº do produto. 11 músicas (lista em robo/musicas/LEIA.txt).
  Só os trechos ficam no repositório (público), nunca a música inteira. O João NÃO quer as músicas salvas no computador dele.
  Músicas virais do Instagram: impossível pela API (e com direito autoral derruba o Reels) — não insistir.
- Legendas em tom de conversa ("Achei esse e lembrei de você…") + "📩 Ou manda EU QUERO no direct…".
- Código: robo/arte.py, robo/reel.py, robo/texto.py. Fontes em robo/fontes e docs/fontes (licença OFL).
- Histórico de tentativas de visual em 14/out (não usar de novo): cartaz laranja/preto da taste-skill,
  cartão branco estilo mydealz, fundo laranja. O João escolheu o escuro com produto flutuando.

## Vitrine (link da bio)
- https://multimulti-ofertas.github.io/multimulti (v5, docs/index.html)
- Futurista e interativa: busca fixa no topo ("Viu no Insta? Digita o nº do post"), carrossel automático dos
  achados do dia, produto 3D que inclina com o mouse/celular, grade em perspectiva, partículas, filtros por categoria.
- Link direto para um produto: ...multimulti/?n=4

## ManyChat (plano grátis) — tudo manda o botão "Abrir a vitrine 🔥"
1. "Direct: EU QUERO → vitrine": direct com EU QUERO, QUERO, LINK ou EUQUERO
2. Resposta a qualquer story
3. Direct com preço, valor, quanto, comprar, onde, oi, olá, bom dia, boa tarde, boa noite, produto, achado
4. Resposta padrão (Configurações → Instagram) para qualquer outra mensagem
- A antiga "Auto-DM de links dos comentários" continua parada (no grátis só vale para 1 post).
- Mandar o link exato de cada produto no direct só com ManyChat PRO (~US$ 15/mês).
- Falta testar: alguém de outra conta mandar "EU QUERO" no direct.

## Ferramentas para o Claude
- Actions → "Gerar ofertas do dia" com opções: `previa` (monta e guarda no ramo `previa`, não publica),
  `so_vitrine` (só vitrine, nada no Instagram), `demo` (produtos de mentira).
- Actions → "Checar Instagram": testa o token e mostra o resultado nos avisos (annotations) da execução.
- Actions → "Postar no Instagram" manual: tipo auto/feed/reel/story.
- O Claude dispara workflows pela API REST (gh api .../dispatches) e lê avisos em check-runs/<job>/annotations.
  Registros (logs) e artefatos não abrem pelo proxy: por isso a prévia vai para o ramo `previa`.

## Facebook (Página MultiMulti Ofertas, id 1361895823674839)
- robo/facebook.py espelha o Instagram: feed, Reels e story. Se a Página ficar para trás, o próximo horário põe o que faltou do dia.
- No Facebook a legenda troca "Link na bio" por link direto (...multimulti/?n=X) e tira a linha do direct.
- Secret `FBPAGETOKEN`: token DE PÁGINA que não vence (conferido no Depurador: Tipo Page, Expira Nunca).
  App MultiMulti Robo ganhou o caso de uso "Gerenciar tudo na sua Página" (pages_show_list, pages_read_engagement,
  pages_manage_posts + business_management; a Página está no portfólio MultiMulti.Ofertas).
- Sem FBPAGETOKEN o Facebook é só pulado com aviso. "Postar" manual tem a opção `so_facebook`.
- Marcações em produtos.json: fb_feed, fb_reel, fb_story.
- Rotina tolera atraso do GitHub (hora = agora+10min) e recupera feed/Reels pulados no mesmo dia.
- Workflows fixados em ubuntu-24.04 (GitHub muda o ubuntu-latest para 26 em 19/out).
- Cuidado: disparar 2 "Postar" seguidos — um agendado chegando cancela o manual que estava na fila.

## Instagram / Meta
- 14/out: a Meta bloqueou a conta de desenvolvedor por "atividade incomum" (API access blocked). O João
  confirmou a conta no **perfil pessoal** (não como a página) e o acesso voltou no mesmo dia.
  Se acontecer de novo: POSTAR_NO_INSTAGRAM = False, João confirma a conta, rodar "Checar Instagram".
- Token: secret IGTOKEN. **Sem o secret GH_PAT ele não se renova sozinho: vence ~60 dias depois de gerado
  (meados de dezembro).** Próximo passo sugerido: criar o GH_PAT (guiar o João, sem colar no chat).

## Falta
0. Bio do Instagram diz "Comenta EU QUERO no post" mas o que funciona é DIRECT (auto-DM de comentário está parado).
   Trocar por "📩 Manda EU QUERO no direct que eu te mando o link". (revisão de 14/out)
1. Shopee: cadastro de afiliado APROVADO em 13/out; informações fiscais em "Avaliação Pendente";
   pedido "Quero ativar a API" enviado em 13/out (resposta no Outlook, até 3 dias úteis).
   Depois: pegar AppID e Secret em "Abrir API" e salvar como secrets `SHOPEEAPPID` e `SHOPEESECRET`
   (no GitHub: primeiro cole o valor na caixa Secret, depois digite o nome).
2. Criar o secret GH_PAT para o token do Instagram se renovar sozinho.
3. Testar o ManyChat com outra conta.
4. Opcional: `ANTHROPIC_API_KEY` para legendas por IA; ManyChat PRO.
5. Atenção ao tamanho do repositório: as mídias somam ~10 MB/dia no histórico do git (apagadas da vitrine após 10 dias).

## Já configurado
- GitHub Pages ligado (Source: GitHub Actions); link da vitrine na bio do Instagram
- Secret `IGTOKEN` (app da Meta "MultiMulti Robo", modo desenvolvimento, empresa MultiMulti.Ofertas)
- O ID da conta do Instagram é descoberto pelo próprio token (não precisa de IGUSERID)
- Verificação em duas etapas no GitHub; acesso do Claude limitado a este repositório

## Contas e e-mails
- GitHub: usuário multimulti-ofertas, entra com o Google ([e-mail removido], que está cheio); reserva: Outlook
- ManyChat, Meta for Developers e Shopee Afiliados: e-mail do Outlook ([e-mail removido])

## Preferências do João
- Explicações bem leigas, um passo de cada vez, em português
- Nunca colar tokens/senhas no chat
- Não criar coisas que ele não pediu (ex.: o DESIGN.md próprio, que foi removido); quando pedir para usar algo
  de fora (skill, DESIGN.md), usar o que ele indicou
- Produtos nunca repetidos
- Antes de ligar algo novo: revisar tudo e testar primeiro
- Ao chegar no limite da sessão, abrir conversa nova com a frase do topo deste arquivo
