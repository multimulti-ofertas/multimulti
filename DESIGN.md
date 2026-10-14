---
version: 1.0
name: MultiMulti
description: |
  Achadinhos masculinos da Shopee (carro, ferramentas, cuidado, estilo) no Instagram @multimulti.ofertas.
  O visual é o cartaz de oferta do supermercado brasileiro: o preço gigante com os centavos pequenos no
  alto, a foto do produto grande sobre branco, campos de cor chapada em laranja e preto, e o número da
  vitrine como etiqueta. Direto, barulhento como um encarte, mas limpo: nada de ornamento.

colors:
  laranja: "#FF6B1A"      # fundo do cartaz, destaque, segunda metade da marca
  preto: "#111111"        # tinta principal, etiqueta, faixas
  branco: "#FFFFFF"       # campo da foto, texto sobre preto
  cinza-claro: "#D2D2D2"  # só textos secundários sobre preto (ex.: @multimulti.ofertas)

typography:
  preco:
    fontFamily: Barlow Condensed Black
    use: reais do preço (centavos e "R$" na mesma fonte, menores e alinhados no alto)
    size: feed 320px · story até 420px · Reels 520px (diminui até caber)
    letterSpacing: -0.02em
  display:
    fontFamily: Barlow Condensed Black
    use: gancho do Reels (MAIÚSCULAS), "nº X", "Link na bio", logotipo
    size: 92–420px
  titulo:
    fontFamily: Barlow SemiBold
    use: nome do produto, em frase normal (só a 1ª letra, marcas e siglas em maiúscula)
    size: feed 50px · story 56px · Reels 64px · no máximo 2 linhas
    lineHeight: 1.12
  linha-pequena:
    fontFamily: Barlow SemiBold / Bold
    use: "+100 mil vendidos", "link na bio" da etiqueta, @ do perfil
    size: 34–56px
  centavos-e-cifrao:
    centavos: 42% da altura do preço, alinhados no alto
    cifrao: 26% da altura do preço, alinhado no alto

spacing:
  margem: 56px nas artes estáticas, 72px no Reels (uma só, usada em tudo)
  formatos: feed 1080x1350 · story 1080x1920 · Reels 1080x1920, 30fps, 10s

fontes-no-repositorio: robo/fontes/ (licença OFL, OFL.txt)
codigo: robo/arte.py (feed e story) · robo/reel.py (Reels)
---

# MultiMulti — DESIGN.md

## 1. Tema visual e atmosfera

**A ideia:** o cartaz de oferta pintado do supermercado brasileiro vira o layout. Quem passa o dedo
pelo feed precisa ler o preço antes de qualquer outra coisa, como lê o cartaz de um corredor de
mercado.

- **Densidade:** alta, mas com uma coisa dominante por vez: a foto em cima, o preço embaixo.
- **Tom:** direto e popular, de encarte, sem parecer barato. Confiante, nunca gritado com enfeites.
- **Filosofia:** tirar todo ornamento e colocar no lugar escala (preço maior), conteúdo real (a foto de
  verdade do produto) e campos de cor chapada. Regras herdadas da taste-skill
  (github.com/Leonxlnx/taste-skill).

## 2. Paleta de cores e funções

| Nome | Hex | Função |
|---|---|---|
| Laranja | `#FF6B1A` | Fundo do cartaz (metade de baixo do feed e do story, telas de gancho e preço do Reels). Cor do "nº X" sobre preto. Segunda metade do logotipo. |
| Preto | `#111111` | Toda a tinta sobre laranja e branco: preço, título, vendas. Etiqueta do número, faixa "Link na bio", tela final do Reels. |
| Branco | `#FFFFFF` | Campo da foto do produto (as fotos da Shopee têm fundo branco, então o campo some e o produto fica solto). Texto sobre preto. |
| Cinza-claro | `#D2D2D2` | Só o @ do perfil sobre preto. Nunca em texto principal. |

Proporção típica: 55% branco (foto), 40% laranja, 5% preto (etiqueta/faixa).
Um fundo, uma tinta, um destaque. **Nenhuma outra cor**, nem para categoria.

## 3. Regras de tipografia

Uma família só: **Barlow** (Condensed Black para números e chamadas, SemiBold para textos).

| Papel | Fonte | Tamanho | Regra |
|---|---|---|---|
| Preço (reais) | Barlow Condensed Black | 320px feed / até 420px story / 520px Reels | A maior coisa da arte depois da foto. Diminui até caber; nunca quebra linha. |
| Centavos `,47` | Barlow Condensed Black | 42% do preço | Alinhados pelo alto, à direita dos reais. |
| `R$` | Barlow Condensed ExtraBold | 26% do preço | Alinhado pelo alto, à esquerda dos reais. |
| Número `nº 1` | Barlow Condensed Black | até 210px (feed), 92px (faixa), 420px (Reels) | Dentro da etiqueta preta ou da faixa. |
| Gancho do Reels | Barlow Condensed Black, MAIÚSCULAS | até 230px | Todas as linhas do mesmo tamanho, alinhadas à esquerda. |
| Título do produto | Barlow SemiBold | 50 / 56 / 64px | Frase normal, no máximo 2 linhas. Cortar o nome antes de " - ", tirar palavras soltas no fim ("e", "com", "para"). |
| Linha pequena | Barlow SemiBold | 34–56px | "+100 mil vendidos", "45% OFF · +10 mil vendidos". |

- Três tamanhos fazem o trabalho: gigante (preço), médio (título) e pequeno (vendas). Nada no meio.
- Alinhado à esquerda por padrão. Centralizado só a faixa "Link na bio nº X" do story.
- Título nunca em Tudo Com Maiúscula; maiúsculas só no gancho do Reels.

## 4. Componentes

**Cartaz de preço** (`preco_layer`)
`R$` pequeno no alto · reais gigantes · `,centavos` pequenos no alto. Sem "POR APENAS", sem "DE/POR"
riscado (a planilha não traz preço antigo; com a API, o desconto vai na linha pequena: "45% OFF · ...").

**Etiqueta do número** (feed)
Retângulo preto chapado, cantos retos, 300px de largura, encostado na margem de baixo à direita.
`nº 1` branco gigante + `link na bio` laranja embaixo.

**Faixa de chamada** (story)
Faixa preta de lado a lado entre y=1580 e y=1740. `Link na bio` branco + `nº 2` laranja, na mesma linha.

**Campo da foto**
Retângulo branco sem moldura. A foto é recortada do branco em volta e ampliada o máximo possível com
40px de folga. Nunca colocar nada por cima da foto.

**Logotipo**
`MULTI` preto + `MULTI` laranja (sobre branco) ou `MULTI` branco + `MULTI` laranja (sobre preto),
Barlow Condensed Black, 40–52px, no canto de cima à esquerda. Nunca sobre o laranja.

**Reels: quatro telas cheias, 10s**
1. 0–2s: gancho em MAIÚSCULAS gigantes, preto sobre laranja.
2. 2–5,2s: foto grande sobre branco com zoom lento (até 6%) e o título embaixo.
3. 5,2–8s: cartaz de preço preto sobre laranja + linha de vendas.
4. 8–10s: `Link na bio` branco + `nº X` laranja gigante pulsando + @ do perfil, sobre preto.
Entradas: sobe 40–80px e aparece, em cascata de 0,12s. Só posição e transparência.

## 5. Princípios de layout

- **Feed (1080x1350):** branco de 0 a 760 (faixa de 90px da marca + foto), laranja de 760 até o fim.
  Título logo abaixo da divisa. Preço e etiqueta terminam juntos na margem de baixo.
- **Story (1080x1920):** branco de 0 a 950 (marca em y=230, foto de 300 a 950), laranja embaixo.
  O preço ocupa todo o espaço livre entre o título e a linha de vendas.
- **Margem única:** 56px (estáticas) / 72px (Reels). Todo texto começa na mesma borda esquerda.
- **Divisões por campo de cor**, nunca por linha.
- Espaço que sobrou vira preço maior, não enfeite.

## 6. Profundidade e elevação

**Nenhuma.** Tudo é plano: sem sombra, sem brilho, sem degradê, sem vidro/desfoque, sem contorno.
A separação entre partes é só a troca de campo de cor (branco → laranja → preto).

## 7. Faça e não faça

**Faça**
- Preço sempre como a maior coisa escrita.
- Foto real do produto, grande, sobre branco.
- Uma ideia por tela no Reels.
- Título curto e em frase normal.

**Não faça**
- Etiquetinhas acima de títulos ("CUIDADO", "POR APENAS", "NOVO", "OFERTA").
- Contorno fino, caixas com borda, listras, padrões de fundo, grades.
- Degradê, sombra, brilho (glow), desfoque.
- Emoji dentro da arte (na legenda pode).
- Fonte monoespaçada; mais de uma família de fonte.
- Letrinha pequena em maiúsculas espaçadas.
- Numeração decorativa (01 / 02 / 03).
- Palavra destacada com outra cor ou itálico dentro do título.
- Telas quase vazias no Reels.
- Selo de categoria colorido.

## 8. Formatos e áreas seguras

| Formato | Tamanho | Área segura |
|---|---|---|
| Feed | 1080x1350 (4:5) | Inteiro. A grade do perfil corta para 3:4 no centro: preço e número não podem encostar nas laterais. |
| Story | 1080x1920 | O Instagram cobre ~200px em cima e ~180px embaixo: foto começa em 300, faixa termina em 1740. |
| Reels | 1080x1920 | Conteúdo entre y=220 e y=1450; largura útil até x≈930 (botões à direita, legenda embaixo). |
| Vitrine (site) | celular primeiro, 390px | Ver "Pendente" abaixo. |

**Pendente:** a vitrine (`docs/index.html`) ainda usa o visual antigo "futurista" (fundo escuro com
grade, brilho, vidro, fonte mono). Ela deve migrar para este sistema: fundo branco, cards de produto
como mini-cartazes laranja com preço em Barlow Condensed Black, número da vitrine na etiqueta preta.

## 9. Guia rápido para IA

**Cores:** laranja `#FF6B1A` · preto `#111111` · branco `#FFFFFF` · (cinza `#D2D2D2` só para @ sobre preto)
**Fontes:** Barlow Condensed Black (preço, números, chamadas) · Barlow SemiBold (títulos, vendas)

**Prompt pronto (arte nova):**
> Crie uma arte do MultiMulti seguindo o DESIGN.md: cartaz de oferta de supermercado. Foto do produto
> grande sobre branco na metade de cima; metade de baixo laranja #FF6B1A com o nome do produto em
> Barlow SemiBold (2 linhas no máximo), o preço gigante em Barlow Condensed Black preto com "R$" e
> centavos pequenos alinhados no alto, a linha "+X mil vendidos" e a etiqueta preta "nº X / link na bio".
> Sem etiquetinhas, contornos, sombras, degradês ou emoji.

**Prompt pronto (Reels):**
> Reels de 10s do MultiMulti seguindo o DESIGN.md: 4 telas cheias — gancho em maiúsculas gigantes
> sobre laranja, foto grande sobre branco com o título, cartaz de preço sobre laranja, "Link na bio nº X"
> sobre preto. Entradas subindo e aparecendo, sem outros efeitos.

**Antes de entregar, confira:** o preço é a maior coisa escrita? A foto está grande e sem moldura?
Existe alguma etiquetinha, contorno, sombra ou degradê? (Se sim, tire.) O título cabe em 2 linhas?
