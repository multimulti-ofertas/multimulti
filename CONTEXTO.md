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
3. Depois da Shopee: no ManyChat, religar "Auto-DM de links dos comentários" (está STOPPED) e configurar "Instagram Default Reply" para mandar o link da vitrine no direct
4. Opcional: `ANTHROPIC_API_KEY` para legendas por IA; ManyChat PRO para responder em qualquer post

## Contas e e-mails
- GitHub: usuário multimulti-ofertas, entra com o Google ([e-mail removido], que está cheio); reserva: Outlook
- ManyChat, Meta for Developers e Shopee Afiliados: e-mail do Outlook ([e-mail removido])

## Preferências
- Explicações bem leigas, um passo de cada vez, em português
- Nunca colar tokens/senhas no chat
