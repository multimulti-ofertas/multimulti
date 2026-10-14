# Contexto do projeto MultiMulti (para continuar em outra conversa)

Atualizado em 14/out/2026. Ao abrir uma conversa nova com o Claude, diga:
"Leia o CONTEXTO.md do repositório multimulti-ofertas/multimulti e vamos continuar."

## O que é
Perfil de achadinhos masculinos da Shopee (carro, ferramentas, cuidado, estilo) com link de afiliado.
Instagram @multimulti.ofertas · Página do Facebook "MultiMulti Ofertas".
Mercado Livre foi descartado. Grupo/canal do WhatsApp pausado até ter um chip separado.

## Como funciona hoje
- Robô neste repositório (GitHub Actions), horário de Cuiabá:
  - 07:00 busca 6 ofertas da Shopee do tema do dia, cria arte, story, Reels e legenda, atualiza a vitrine
  - Rotina (desde 14/out): feed 08:00 e 20:00 · Reels 12:00 e 21:00 · 1 story por hora das 08:00 às 22:00 (19 por dia; limite do Instagram é 50). 8 produtos por dia. Horários em robo/config.py → ROTINA
- **Sem a API da Shopee (ainda):** o robô lê as planilhas da pasta `ofertas/` (painel de afiliados →
  Oferta de produto → marcar tudo → "Obter Link em Massa" → baixa um .csv). Separa por tema, nunca
  repete produto nem um parecido, e só 1 de cada tipo por dia. A foto vem da página da Shopee.
  Uma planilha de 83 produtos rendeu 40 produtos novos (~7 dias). Quando acabar, baixar outra.
  Quando a API sair, ela passa a ter prioridade sozinha.
- Só vitrine (produtos aparecem no site, nada vai pro Instagram): Actions → Gerar ofertas do dia → marcar "so_vitrine"
  (usado em 14/out: os 6 de hoje estão só na vitrine)
- Nomes dos produtos: `texto.nome_curto` (curtos, com acento, sem palavras de anúncio)
- Vitrine v5: futurista e interativa (busca fixa no topo, carrossel automático, produto 3D, filtros, partículas)
- Prévia sem publicar: Actions → Gerar ofertas do dia → marcar "previa" (resultado no ramo `previa`)
- **Visual:** vitrine de produto premium no escuro (inspirado num Reels de referência de sites 2026): fundo quase preto, produto recortado flutuando com brilho laranja, nome em maiúsculas condensadas (Barlow Condensed), preço grande laranja, círculo com o número. Vale para feed, story, Reels e vitrine. Código: robo/arte.py, robo/reel.py, docs/index.html
- Vitrine (link da bio): https://multimulti-ofertas.github.io/multimulti
  Cada post diz "Link na bio → produto nº X".
- ManyChat (grátis), tudo leva para a vitrine: direct com EU QUERO/QUERO/LINK/EUQUERO; resposta a qualquer story; direct com preço/valor/oi/onde etc.; e resposta padrão para qualquer outra mensagem. A antiga "Auto-DM de links dos comentários" continua parada (no grátis só vale para 1 post).

## Já configurado
- GitHub Pages ligado (Source: GitHub Actions)
- Secret `IGTOKEN` (token do Instagram, app da Meta "MultiMulti Robo", modo teste)
- O ID da conta do Instagram é descoberto pelo próprio token (não precisa de IGUSERID)
- Verificação em duas etapas no GitHub; acesso do Claude limitado a este repositório

- Link da vitrine já está na bio do Instagram
- Vitrine com visual futurista (v2) e aviso "ofertas chegam em breve" quando vazia

## Falta
1. ~~Shopee aprovar o cadastro de afiliado~~ APROVADO em 13/out. Instagram multimulti.ofertas verificado no painel
   (categorias: Automóveis, Roupas/Sapatos Masculinos, Acessórios de Moda, Cupons, Peças para Veículos)
   - Informações fiscais enviadas em 13/out, "Avaliação Pendente"
   - "Abrir API" ainda sem acesso (AppID/Senha vazios, botão Aplicar apagado): esperar a aprovação fiscal
     - Pedido "Quero ativar a API" enviado em 13/out pela Central de Ajuda do Afiliado
       (help.shopee.com.br → Acesso rápido → E-mail). Prazo: até 3 dias úteis, resposta no Outlook
     - Plano B se demorar: artigo "Saiba Como Obter Link em Massa" na Central de Ajuda
2. Pegar AppID e Secret da Open API da Shopee e salvar como secrets `SHOPEEAPPID` e `SHOPEESECRET`
   (no GitHub: primeiro cole o valor na caixa Secret, depois digite o nome)
3. (feito em 14/out) ManyChat configurado. Para mandar o link exato de cada produto no direct, só com ManyChat PRO
4. Opcional: `ANTHROPIC_API_KEY` para legendas por IA; ManyChat PRO para responder em qualquer post

## Contas e e-mails
- GitHub: usuário multimulti-ofertas, entra com o Google ([e-mail removido], que está cheio); reserva: Outlook
- ManyChat, Meta for Developers e Shopee Afiliados: e-mail do Outlook ([e-mail removido])

## Preferências
- Explicações bem leigas, um passo de cada vez, em português
- Nunca colar tokens/senhas no chat
