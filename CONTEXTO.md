# Contexto do projeto MultiMulti (para continuar em outra conversa)

Atualizado em 13/out/2026. Ao abrir uma conversa nova com o Claude, diga:
"Leia o CONTEXTO.md do repositório multimulti-ofertas/multimulti e vamos continuar."

## O que é
Perfil de achadinhos masculinos da Shopee (carro, ferramentas, cuidado, estilo) com link de afiliado.
Instagram @multimulti.ofertas · Página do Facebook "MultiMulti Ofertas".
Mercado Livre foi descartado. Grupo/canal do WhatsApp pausado até ter um chip separado.

## Como funciona hoje
- Robô neste repositório (GitHub Actions), horário de Cuiabá:
  - 07:00 busca ofertas da Shopee do tema do dia, cria arte, story, Reels e legenda, atualiza a vitrine
  - 12:00 posta o feed · 19:00 posta o Reels
- Vitrine (link da bio): https://multimulti-ofertas.github.io/multimulti
  Cada post diz "Link na bio → produto nº X".
- ManyChat (grátis): "comenta EU QUERO" → manda o link no direct. No plano grátis vale para 1 post por automação.

## Já configurado
- GitHub Pages ligado (Source: GitHub Actions)
- Secret `IGTOKEN` (token do Instagram, app da Meta "MultiMulti Robo", modo teste)
- O ID da conta do Instagram é descoberto pelo próprio token (não precisa de IGUSERID)
- Verificação em duas etapas no GitHub; acesso do Claude limitado a este repositório

## Falta
1. Shopee aprovar o cadastro de afiliado (enviado em 13/out; resposta no Outlook)
2. Pegar AppID e Secret da Open API da Shopee e salvar como secrets `SHOPEEAPPID` e `SHOPEESECRET`
   (no GitHub: primeiro cole o valor na caixa Secret, depois digite o nome)
3. Colocar o link da vitrine na bio do Instagram
4. Opcional: `ANTHROPIC_API_KEY` para legendas por IA; ManyChat PRO para responder em qualquer post

## Contas e e-mails
- GitHub: usuário multimulti-ofertas, entra com o Google ([e-mail removido], que está cheio); reserva: Outlook
- ManyChat, Meta for Developers e Shopee Afiliados: e-mail do Outlook ([e-mail removido])

## Preferências
- Explicações bem leigas, um passo de cada vez, em português
- Nunca colar tokens/senhas no chat
