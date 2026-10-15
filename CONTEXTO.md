# Contexto do projeto MultiMulti (para continuar em outra conversa)

Atualizado em 14/out/2026, 16:45 (Cuiabá). Ao abrir uma conversa nova com o Claude, diga:
"Leia o CONTEXTO.md do repositório multimulti-ofertas/multimulti e vamos continuar."

## O que é
Perfil de achadinhos masculinos da Shopee (carro, ferramentas, cuidado, estilo) com link de afiliado.
Instagram @multimulti.ofertas · Página do Facebook "MultiMulti Ofertas".
Mercado Livre foi descartado. Grupo/canal do WhatsApp pausado até ter um chip separado.

## Situação agora (14/out)
- **Rotina LIGADA e postando no Instagram E na Página do Facebook** (Facebook desde 14/out 14:15). 1º post do feed saiu em 14/out às 10:46 (nº 1, Máquina de barbear 3 em 1).
- Produtos de 14/out: nº 1 a 8 (feed: 1 e 2 · Reels: 3 e 4 · stories: todos).
- Estoque (14/out, depois das planilhas de carro e ferramentas): passam no filtro carro 11 · ferramentas 4 · estilo 6 · cuidado 26 (~6 dias).
  As planilhas de carro/ferramentas vieram fracas: 191 itens, só 15 com 100+ vendas (resto: peça CNC chinesa, pingente, 0 vendas).
  Dica para o João: no painel, ordenar por "Mais vendidos" e buscar termos específicos (ex.: "kit chave catraca", "suporte celular carro").
- Esperando a Shopee liberar a Open API (prazo até sex 16/out, resposta no **Outlook**).

## Como funciona (robô = GitHub Actions deste repositório, horário de Cuiabá)
| Horário | O que acontece | Onde mudar |
|---|---|---|
| 06:25 | "Gerar ofertas do dia": escolhe 8 produtos, monta feed/story/Reels/legendas, atualiza a vitrine | .github/workflows/gerar.yml |
| 11:00 e 19:00 (12h e 20h Brasília) | Post no feed (+ story) | robo/config.py → ROTINA |
| 12:00 e 20:00 (13h e 21h Brasília) | Reels (+ story) | robo/config.py → ROTINA |
| 09:00 a 20:00 (10h–21h Brasília) | 1 story por hora, 12 por dia (os 8 produtos se revezam) | robo/config.py → ROTINA |
| Segunda 06:00 | Renova o token do Instagram (só salva se existir o secret GH_PAT) | token.yml |
- "Postar no Instagram" roda de hora em hora (xx:50) e publica o que a tabela ROTINA manda para aquela hora.
  São 16 publicações/dia no Instagram (+ as mesmas no Facebook); limite do Instagram é 100 por 24h.
  Horários trocados em 14/out (valem a partir de 15/out) com base nos estudos de 2026 (almoço e noite);
  rever pelos Insights do Instagram depois de ~2 semanas. ROTINA_ANTIGA em config.py só serviu para 14/out.
- Chave geral: `POSTAR_NO_INSTAGRAM` em robo/config.py (False = só monta produtos e vitrine, não posta).
- Se uma publicação falhar no meio, o que já saiu fica marcado (não repete post). Falha do Instagram tenta de novo 1x após 30s.
- Temas: segunda carro · terça ferramentas · quarta cuidado · quinta estilo · sexta a domingo top (mistura).
  Se a planilha não tem o tema do dia, completa com outros temas.

## De onde vêm os produtos
- **Sem a API da Shopee (ainda):** planilhas .csv na pasta `ofertas/`. Como baixar: painel de afiliados →
  Oferta → Oferta de produto → buscar → "Selecione todos os produtos nesta página" → "Obter Link em Massa".
  Mandar o arquivo para o Claude colocar em `ofertas/`.
- Regras: nunca repete produto (nem um muito parecido de outra loja), só 1 de cada tipo por dia,
  tira palmilhas/lentes/feminino. A foto é pega na página da Shopee; o produto é recortado do fundo branco.
- Nomes curtos e limpos: `texto.nome_curto` (acentos, sem "profissional/original/códigos"). Nome estranho → corrigir à mão em config.NOMES.
- Tema trocado numa data específica: config.TEMA_EM (ex.: 15/out virou "top" porque estilo estava fraco). Dia "top" alterna os temas.
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
- https://multimulti-ofertas.github.io/multimulti (v6, docs/index.html)
- v6 (14/out): "modo leve" no navegador do Instagram/Facebook e em celular — sem partículas, sem 3D, sem blur, animações só
  no slide visível, foto local em vez da da Shopee. Motivo: no Instagram a página travava ao trocar de produto, recarregava e ficava preta.
- Futurista e interativa: busca fixa no topo ("Digita o nº do post", encurtado para caber no celular), carrossel automático dos
  achados do dia, produto 3D que inclina com o mouse/celular, grade em perspectiva, partículas, filtros por categoria.
- Link direto para um produto: ...multimulti/?n=4

## ManyChat (plano grátis) — tudo manda o botão "Abrir a vitrine 🔥"
1. "Direct: EU QUERO → vitrine": direct com EU QUERO, QUERO, LINK ou EUQUERO
2. Resposta a qualquer story
3. Direct com preço, valor, quanto, comprar, onde, oi, olá, bom dia, boa tarde, boa noite, produto, achado
4. Resposta padrão (Configurações → Instagram) para qualquer outra mensagem
- A antiga "Auto-DM de links dos comentários" continua parada (no grátis só vale para 1 post).
- Mandar o link exato de cada produto no direct só com ManyChat PRO (~US$ 15/mês).
- Testado em 14/out de outra conta: "eu quero" no direct → resposta + botão → vitrine abre certa no celular.

## Proteção (14/out)
- "Vigia diário" (vigia.yml, 07:10): confere tokens IG/Página, vitrine, ofertas do dia, posts de ontem, robôs que falharam
  e estoque de produtos. Se algo quebrou, a execução FALHA e o GitHub manda e-mail para o e-mail principal (Gmail novo).
- Já ligados no repositório: varredura de segredos + bloqueio de envio com segredo (push protection).
- Workflows com permissão mínima; arquivo do token apagado sempre; e-mails tirados do CONTEXTO (repo é público).

## Ferramentas para o Claude
- Actions → "Gerar ofertas do dia" com opções: `previa` (monta e guarda no ramo `previa`, não publica; `data` simula outro dia),
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
- Token: secret IGTOKEN, renovado toda segunda pelo token.yml usando o secret GH_PAT (criado 14/out: fine-grained
  "robo-renovar-instagram", sem vencimento, só repo multimulti, só Secrets read/write). Testado em 14/out.

## Falta
1. Shopee: cadastro de afiliado APROVADO em 13/out; informações fiscais em "Avaliação Pendente";
   pedido "Quero ativar a API" enviado em 13/out (resposta no Outlook, até 3 dias úteis).
   Depois: pegar AppID e Secret em "Abrir API" e salvar como secrets `SHOPEEAPPID` e `SHOPEESECRET`
   (no GitHub: primeiro cole o valor na caixa Secret, depois digite o nome).
2. João vai trocar o nome de exibição do app da Meta de "MultiMulti Robo" para "MultiMulti Ofertas" (Configurações do app
   → Básico), porque o Facebook mostra "Postado por MultiMulti Robo". Não quebra tokens.
3. Opcional: `ANTHROPIC_API_KEY` para legendas por IA; ManyChat PRO.
4. Tamanho do repositório: as mídias somam ~10 MB/dia no histórico do git (apagadas da vitrine após 10 dias, mas o
   histórico guarda). O GitHub recomenda até 1 GB → resolver antes de ~jan/2027 (ex.: mídias num ramo separado recriado do zero).

## Já configurado
- Bio do Instagram (14/out): "📩 Manda EU QUERO no direct" + link da vitrine em Links (conferido)
- GitHub Pages ligado (Source: GitHub Actions); link da vitrine na bio do Instagram
- Secret `IGTOKEN` (app da Meta "MultiMulti Robo", modo desenvolvimento, empresa MultiMulti.Ofertas)
- O ID da conta do Instagram é descoberto pelo próprio token (não precisa de IGUSERID)
- Verificação em duas etapas no GitHub; acesso do Claude limitado a este repositório

## Contas e e-mails
- GitHub: usuário multimulti-ofertas, entra com o Google (Gmail pessoal do João); e-mail principal = Gmail novo do negócio.
- Contato do Shopee Afiliados e a resposta da API: ainda no Outlook do João.
  ATENÇÃO: o João NÃO sabe a senha do Outlook e ele não tem recuperação (só abre no app do celular).
  Plano (14/out): migrar tudo para um Gmail novo só do negócio (criado 14/out, com 2FA + celular + códigos;
  endereço com o João, não escrever aqui). Feito (14/out): Shopee → Gmail novo; GitHub e-mail principal → Gmail novo
  (avisos do Vigia chegam lá); ManyChat → e-mail Gmail novo + login pelo Google. Conta Meta (Facebook + Instagram): contato =
  Gmail novo + celular, Outlook removido, 2FA ligado (14/out). developers.facebook.com ainda mostrava
  "No contact email set" (conferir se atualiza sozinho).
  Falta: contato do Shopee Afiliados → Gmail novo
  (SÓ depois que chegar a resposta da API no Outlook).
- Senhas: gerenciador do Google (Google pessoal tem 2FA completo). Nunca em arquivo .txt.
- Este repositório é PÚBLICO (exigência do GitHub Pages grátis): nunca escrever e-mails, senhas, tokens ou dados pessoais aqui.

## Preferências do João
- Explicações bem leigas, um passo de cada vez, em português
- Nunca colar tokens/senhas no chat
- Não criar coisas que ele não pediu (ex.: o DESIGN.md próprio, que foi removido); quando pedir para usar algo
  de fora (skill, DESIGN.md), usar o que ele indicou
- Produtos nunca repetidos
- Antes de ligar algo novo: revisar tudo e testar primeiro
- Ao chegar no limite da sessão, abrir conversa nova com a frase do topo deste arquivo
