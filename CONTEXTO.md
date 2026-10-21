# Contexto do projeto MultiMulti (para continuar em outra conversa)

Atualizado em 21/out/2026, 08:55 (Cuiabá). Ao abrir uma conversa nova com o Claude, diga:
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
- **API da Shopee LIBERADA em 15/out** (secrets SHOPEEAPPID/SHOPEESECRET salvos; prévia de 16/out testada OK).
  A partir de 16/out o robô busca sozinho: só +500 vendas (VENDAS_MINIMAS_API; era 1 mil até 19/out), nota ≥4.6, sem exigir desconto, tema confirmado
  pelo nome (planilha.tema), 1 de cada tipo por dia (planilha.TIPOS/MESMO_TIPO). Planilhas viram reserva.
  Dia de tema: 25 palavras sorteadas das ~60–75 do tema (config.PALAVRAS, 2 páginas cada; ampliado 21/out). SÓ produtos do tema (João, 19/out):
  se não der 12, saem menos stories. Só sexta–domingo ("top") misturam temas.
  Trava de tipo (19/out, pedido do João): o mesmo tipo (compressor, capa de volante, meia...) evita voltar por 7 dias
  (config.TIPO_FOLGA_DIAS). Feed/Reels pegam tipos novos; se faltar produto pra fechar 12, os stories aceitam tipo recente.
- 15/out: e-mails pessoais apagados de TODO o histórico do git (reescrito + force push). Nunca escrever e-mail aqui.
  Ruleset "Proteger main" ATIVO (bloqueia force push e apagar o main; não cobre o ramo midia). Falta conferir: GitHub Settings → Emails (manter e-mail privado).

> Foco (15/out): só Instagram + Facebook; WhatsApp em breve. TikTok e Kwai CANCELADOS pelo João
> (API do TikTok não aprova postar nas próprias contas; Kwai não tem API). Não reabrir sem ele pedir.

## Como funciona (robô = GitHub Actions deste repositório, horário de Cuiabá)
| Horário | O que acontece | Onde mudar |
|---|---|---|
| 06:25 | "Gerar ofertas do dia": escolhe 8 produtos, monta feed/story/Reels/legendas, atualiza a vitrine | .github/workflows/gerar.yml |
| 11:00 e 19:00 (12h e 20h Brasília) | Post no feed (+ story) | robo/config.py → ROTINA |
| 12:00 e 20:00 (13h e 21h Brasília) | Reels (+ story) | robo/config.py → ROTINA |
| 09:00 a 20:00 (10h–21h Brasília) | 1 story por hora, 12 por dia, cada produto UMA vez (12 produtos por dia, nunca repete) | robo/config.py → ROTINA |
| Sábado 07:00 | "Top 3 da semana": vídeo dos 3 mais vendidos dos últimos 7 dias, música baixa, + roteiro e legenda.
  O João baixa em .../multimulti/semana/ e posta À MÃO com a narração dele | .github/workflows/semana.yml, robo/top3.py |
| Segunda 06:00 | Renova o token do Instagram (só salva se existir o secret GH_PAT) | token.yml |
- "Postar no Instagram" roda 4x por hora (xx:02, :17, :32, :47; o GitHub atrasa/pula). O post da hora sai entre hh:00 e ~hh:20. Ele CONTA o que já saiu no dia
  (robo/postar.py → plano) e só posta o que falta até aquela hora: rodar 2x não duplica, hora perdida é recuperada.
- A tabela ROTINA (config.py) diz quantos de cada tipo saem até cada hora.
  São 16 publicações/dia no Instagram (+ as mesmas no Facebook); limite do Instagram é 100 por 24h.
  Horários trocados em 14/out (valem a partir de 15/out) com base nos estudos de 2026 (almoço e noite);
  rever pelos Insights do Instagram depois de ~2 semanas. ROTINA_ANTIGA em config.py só serviu para 14/out.
- Chave geral: `POSTAR_NO_INSTAGRAM` em robo/config.py (False = só monta produtos e vitrine, não posta).
- Se uma publicação falhar no meio, o que já saiu fica marcado (não repete post). Falha do Instagram tenta de novo 1x após 30s.
- Temas: segunda carro · terça ferramentas · quarta cuidado · quinta estilo · sexta a domingo top (mistura).
  Dia de tema usa SÓ produtos do tema (se faltar, saem menos stories); só o "top" mistura.

## De onde vêm os produtos
- **Sem a API da Shopee (ainda):** planilhas .csv na pasta `ofertas/`. Como baixar: painel de afiliados →
  Oferta → Oferta de produto → buscar → "Selecione todos os produtos nesta página" → "Obter Link em Massa".
  Mandar o arquivo para o Claude colocar em `ofertas/`.
- Regras: nunca repete produto (nem um muito parecido de outra loja), só 1 de cada tipo por dia,
  tira palmilhas/lentes/feminino.
  Tipo "chave de precisão" (chave de fenda/precisão) conta 1 por dia; "brinquedo", "rolo modelador" e unha/penteado (polygel, manicure, esmalte, penteado) e massinha/slime ficam fora (16/out).
  Acessório de cabelo feminino (scrunchie, presilha, "ferramenta trança", "ferramentas de cabelo") e anzol ficam fora (17/out).
  Chapinha fica fora (20/out, João). Body splash masculino pode.
  21/out: fora também maquiagem (corretivo/corretor/batom), pet/animais, cabide, sutiã, pipoca/salgado, meia médica (varizes, pós-cirurgia),
  costura/overlock, casamento/noivo, baby masculino, buço. Tipos novos: bits (=ponteira), fita métrica (=trena), caneta, adesivo, sérum (=vitamina C), navalha (=aparelho de barbear) etc.
  "Parecido" (planilha.parecido) ignora quantidade e plural ("40 peças ... chave" = "46 peças ... chaves") e compara até 120
  letras do nome; mesmo tipo + 60% das palavras do nome menor iguais também é "parecido"
  (18/out: jogos de chave catraca de 46 peças de lojas diferentes voltavam todo dia). "Par/pares de meia" = tipo meia; "pomada" virou tipo (1 por dia).
  Flanela/pano é um tipo só, pincel também (1 por dia). Nome com " | " é cortado ali ("Relógio digital wr | 100 % qualidade").
  O tipo é a palavra de planilha.TIPOS que aparece PRIMEIRO no nome; palavras de FORA valem só no começo da palavra
  (antes "trico" barrava todo produto "elétrico"). A foto é pega na página da Shopee; o produto é recortado do fundo branco.
- Nomes curtos e limpos: `texto.nome_curto` (acentos, sem "profissional/original/códigos"). Nome estranho → corrigir à mão em config.NOMES.
- Tema trocado numa data específica: config.TEMA_EM (ex.: 15/out virou "top" porque estilo estava fraco). Dia "top" alterna os temas.
- Quando acabar a planilha, o "Gerar ofertas do dia" falha com "Acabaram os produtos novos".
- Quando a API sair (secrets SHOPEEAPPID e SHOPEESECRET), ela passa a ter prioridade sozinha.

## Visual (feed, story, Reels e vitrine)
- Inspirado num Reels de referência ("Websites in 2026"): fundo quase preto, produto recortado flutuando e
  inclinado com brilho laranja, nome em maiúsculas condensadas (Barlow Condensed), preço grande laranja,
  círculo com o número, "LINK NA BIO →". Story também diz "ou responde o story que eu te mando o link".
- Reels: cena contínua de 10s (chamada → produto flutuando → preço → "Link na bio nº X"). A chamada já aparece no 1º quadro;
  capa = quadro dos 4,5s (thumb_offset); marca a 290px do topo para o grid não cortar.
- Música nos Reels (desde 14/out): trechos de 10s em robo/musicas/*.m4a (Coleção de Sons da Meta), já cortados
  no drop, com fade e volume -14 LUFS. robo/musica.py alterna pelo nº do produto. 11 músicas (lista em robo/musicas/LEIA.txt).
  Só os trechos ficam no repositório (público), nunca a música inteira. O João NÃO quer as músicas salvas no computador dele.
  Músicas virais do Instagram: impossível pela API (e com direito autoral derruba o Reels) — não insistir.
- Legendas terminam com "#publi" (texto.com_publi, colocado na hora de postar). O João NÃO quer a palavra "afiliado" em nada
  público; vitrine diz "Contém links patrocinados da Shopee".
- Legendas em tom de conversa ("Achei esse e lembrei de você…") + "📩 Ou manda EU QUERO no direct…".
- Código: robo/arte.py, robo/reel.py, robo/texto.py. Fontes em robo/fontes e docs/fontes (licença OFL).
- Histórico de tentativas de visual em 14/out (não usar de novo): cartaz laranja/preto da taste-skill,
  cartão branco estilo mydealz, fundo laranja. O João escolheu o escuro com produto flutuando.

## Mídias (desde 20/out)
- Fotos, artes e Reels NÃO ficam no main (docs/media está no .gitignore). Ficam no ramo `midia`, com 1 commit só,
  recriado do zero a cada "Gerar ofertas do dia" (só os últimos 10 dias, config.GUARDAR_MIDIA_DIAS).
- .github/midia.sh: `baixar` (ramo → docs/media) e `enviar` (docs/media → recria o ramo). gerar.yml baixa, gera e
  envia o ramo ANTES de salvar o main; pages.yml, semana.yml e teste-voz.yml baixam antes de rodar. Prévia usa `git add -f`.
- Postar não precisa dos arquivos: usa as URLs da vitrine.

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
1. Destaques do Instagram: "Sobre" pronto e no ar (capa quadrada MULTI/MULTI + 4 stories). Próximo: "Avaliações" com
   prints de AVALIAÇÕES REAIS da Shopee que o João vai mandar (montar no visual da marca, esconder nome de quem avaliou,
   linha "Avaliação real de quem comprou na Shopee"). Depoimento inventado: não fazer.
2. Opcional: `ANTHROPIC_API_KEY` para legendas por IA; ManyChat PRO.
3. (Resolvido 20/out) Tamanho do repositório: mídias saíram do main (ver "Mídias" abaixo); o crescimento parou em ~62 MB.
   Limpar o histórico antigo (cairia para ~6 MB) exige force push no main, bloqueado pelo ruleset. Não vale o risco; só se o João pedir.

## Já configurado
- Bio do Instagram (14/out): "📩 Manda EU QUERO no direct" + link da vitrine em Links (conferido)
- GitHub Pages ligado (Source: GitHub Actions); link da vitrine na bio do Instagram
- Secret `IGTOKEN` (app da Meta "MultiMulti Robo", modo desenvolvimento, empresa MultiMulti.Ofertas)
- Nome do app "MultiMulti Robo" fica como está (João, 20/out: não precisa trocar). Não sugerir de novo.
- O ID da conta do Instagram é descoberto pelo próprio token (não precisa de IGUSERID)
- Verificação em duas etapas no GitHub; acesso do Claude limitado a este repositório

## Contas e e-mails
- GitHub: usuário multimulti-ofertas, entra com o Google (Gmail pessoal do João); e-mail principal = Gmail novo do negócio.
- Contato do Shopee Afiliados → Gmail novo (trocado em 19/out). O Outlook antigo (sem senha, sem recuperação) não é mais usado em nada.
  Migração (14/out): migrar tudo para um Gmail novo só do negócio (criado 14/out, com 2FA + celular + códigos;
  endereço com o João, não escrever aqui). Feito (14/out): Shopee → Gmail novo; GitHub e-mail principal → Gmail novo
  (avisos do Vigia chegam lá); ManyChat → e-mail Gmail novo + login pelo Google. Conta Meta (Facebook + Instagram): contato =
  Gmail novo + celular, Outlook removido, 2FA ligado (14/out). developers.facebook.com ainda mostrava
  "No contact email set" (conferir se atualiza sozinho).
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

## Atualização 19/out (fim do dia)
- Reels v2 (robo/reel2.py + robo/voz.py): narração com voz da Microsoft (edge-tts, pt-BR-AntonioNeural, config.VOZ="edge"),
  legenda animada sincronizada, produto com zoom/balanço, preço entra junto com a voz, ~12 s. Sem voz → Reels antigo.
- 19/out ~19h: feed nº 52 saiu ~10x (Instagram publicava e devolvia "action is blocked" 2207051; o robô repetia).
  João apagou os repetidos. Correção: instagram.checar_antes() roda ANTES de todo post (limite, arquivo, legenda,
  produto já no perfil, intervalo de 12 min); erro de bloqueio → docs/pausa.json pausa 24h; vigia avisa.
  Teste sem postar: workflow "Postar" com so_testar=true. Postagem religada pelo João às 22h.
- Dia de tema só com produtos do tema; +500 vendas, sem exigir desconto; trava de 7 dias por tipo (preferência).
- A tarefa agendada "Revisão diária 07h40" não existe mais (sumiu da lista); recriar só se o João pedir.
- Ideias em espera: 2º Instagram feminino (esperar 2–3 semanas de números); apresentador de IA (testar no CapCut à mão).

## Atualização 20–21/out
- Segurança conferida (20/out): nenhum .env nem chave no código ou nos 215 commits; chaves só nos Secrets; novo_token.txt no .gitignore.
- Nome do app da Meta fica "MultiMulti Robo" (João não quer trocar). E-mail de contato do Shopee Afiliados → Gmail novo (feito 19/out); Outlook não é mais usado.
- Mídias no ramo `midia` (ver seção "Mídias"). 1ª geração real (21/out) OK: 11 produtos, arquivos no ar, so_testar "PODE POSTAR".
  Limpeza do histórico antigo NÃO feita (ruleset bloqueia force push); repositório parado em ~62 MB.
- Chapinha fora (20/out). Vocabulário ampliado (21/out): ~60–75 buscas por tema, 25 sorteadas por dia; prévias de 26–29/out deram 12 produtos em cada tema.
- Clareador de virilha/axila/íntimo FORA (21/out, decisão do João). Clareador dental continua. Sem gastos por enquanto: nada de ANTHROPIC_API_KEY nem ManyChat PRO (21/out).
