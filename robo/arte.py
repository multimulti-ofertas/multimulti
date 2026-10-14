"""Artes MultiMulti no estilo do DESIGN.md do mydealz (comunidade de ofertas), com o laranja da marca.

Cada arte é um "cartão de oferta" como num feed de promoções feito por gente: fundo cinza-claro,
cartão branco de cantos arredondados com borda fininha, quem postou em cima ("MultiMulti Ofertas ·
achei pra você"), foto em moldura arredondada, título em negrito, preço em laranja, pílula de
vendas em vermelho "quente" e botões em pílula. Fonte Nunito Sans em dois pesos (500 e 700).

feed(cfg, saida)  -> 1080x1350
story(cfg, saida) -> 1080x1920

cfg: photo (caminho), title, new ("R$ 48,47"), numero, extra (ex.: "+100 mil vendidos"),
     badge (só aparece se for desconto, ex.: "45% OFF"), category (opcional)
"""
import os
import re

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps

# ---------- tokens (DESIGN.md mydealz, cor principal trocada pelo laranja da marca) ----------
LARANJA = (251, 96, 1)        # warm #fb6001 -> cor principal: preço e botão
LARANJA_FORTE = (196, 72, 0)  # texto laranja sobre fundo claro
QUENTE = (206, 23, 54)        # hot #ce1736 -> pílula de vendas
FRIO = (3, 78, 177)           # cold #034eb1
MENTA = (222, 253, 228)       # discount-surface
VERDE_FORTE = (25, 126, 37)   # green-strong (texto do desconto)
CANVAS = (243, 245, 247)      # fundo da página
BRANCO = (255, 255, 255)      # cartão
TINTA = (0, 0, 0)             # títulos
CORPO = (107, 109, 112)       # texto secundário
APAGADO = (167, 169, 172)
LINHA = (223, 225, 228)       # hairline

# nomes antigos usados por outros módulos
OR, BK, WH = LARANJA, TINTA, BRANCO

_AQUI = os.path.join(os.path.dirname(__file__), "fontes")
MEDIO = os.path.join(_AQUI, "NunitoSans-Medium.ttf")   # 500
NEGRITO = os.path.join(_AQUI, "NunitoSans-Bold.ttf")   # 700
FORTE = os.path.join(_AQUI, "NunitoSans-Black.ttf")    # 900: só chamada, preço e número
BOLD = TEXTO = TEXTO_B = DISPLAY = DISPLAY2 = COND = NEGRITO

# escala: a arte tem 1080px, ~2,5x a tela de um celular (os tokens do guia são para 390-430px)
X = 2.5
R_MD = int(8 * X)      # cartões, molduras
BORDA = 3              # hairline
PAD = int(16 * X)      # respiro interno do cartão
M = 44                 # margem da arte
W, H = 1080, 1350


# ---------- texto ----------

def fonte(path, size):
    return ImageFont.truetype(path, size)


def text_layer(text, path, size, color, sx=1.0, tracking=0.0):
    f = fonte(path, size)
    l, t, r, b = f.getbbox(text)
    lay = Image.new("RGBA", (r - l + 4, b - t + 4), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((-l + 2, -t + 2), text, font=f, fill=color)
    return lay


def fit_layer(text, path, size, color, maxw, sx=1.0, tracking=0.0):
    while size > 12:
        lay = text_layer(text, path, size, color)
        if lay.width <= maxw:
            return lay
        size -= 2
    return text_layer(text, path, size, color)


def wrap(text, path, size, maxw, sx=1.0):
    f = fonte(path, size)
    lines, cur = [], ""
    for w in text.split():
        test = (cur + " " + w).strip()
        if f.getlength(test) <= maxw:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def bloco(text, path, size, color, maxw, linhas=2, entrelinha=1.2):
    while True:
        ls = wrap(text, path, size, maxw)
        if len(ls) <= linhas or size <= 30:
            break
        size -= 2
    ls = ls[:linhas]
    f = fonte(path, size)
    asc, desc = f.getmetrics()
    passo = int(size * entrelinha)
    lay = Image.new("RGBA", (maxw, passo * (len(ls) - 1) + asc + desc), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for i, l in enumerate(ls):
        d.text((0, i * passo), l, font=f, fill=color)
    box = lay.getbbox()
    return lay.crop((0, box[1], lay.width, box[3])) if box else lay


def preco_layer(valor, altura, color, maxw):
    """Preço bem grosso, numa linha só (diminui até caber)."""
    return fit_layer(valor, FORTE, altura, color, maxw)


# ---------- formas ----------

def pilula(texto, size, fundo, cor, borda=None, padx=None, pady=None, icone=None, cor_icone=None):
    """Botão/etiqueta totalmente arredondada (rounded.full do guia)."""
    t = text_layer(texto, NEGRITO, size, cor)
    ic = desenho(icone, int(size * 0.72), cor_icone or cor) if icone else None
    padx = padx if padx is not None else int(size * 0.9)
    pady = pady if pady is not None else int(size * 0.5)
    gap = int(size * 0.35) if ic else 0
    w = padx * 2 + t.width + (ic.width + gap if ic else 0)
    h = pady * 2 + max(t.height, ic.height if ic else 0)
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(lay).rounded_rectangle(
        [0, 0, w - 1, h - 1], radius=h // 2, fill=(fundo + (255,)) if fundo else None,
        outline=(borda + (255,)) if borda else None, width=BORDA if borda else 0)
    x = padx
    if ic:
        lay.paste(ic, (x, (h - ic.height) // 2), ic)
        x += ic.width + gap
    lay.paste(t, (x, (h - t.height) // 2), t)
    return lay


def desenho(nome, tam, cor):
    """Ícones desenhados (a fonte não tem esses símbolos): "seta" (↗) e "sobe" (▲)."""
    s = 4  # desenha grande e reduz, para a borda ficar lisa
    T = tam * s
    lay = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    c = cor + (255,)
    if nome == "sobe":
        d.polygon([(T * 0.5, T * 0.12), (T * 0.95, T * 0.85), (T * 0.05, T * 0.85)], fill=c)
    else:  # seta diagonal
        e = int(T * 0.14)
        d.line([(T * 0.18, T * 0.82), (T * 0.8, T * 0.2)], fill=c, width=e)
        d.line([(T * 0.34, T * 0.2), (T * 0.82, T * 0.2)], fill=c, width=e)
        d.line([(T * 0.8, T * 0.18), (T * 0.8, T * 0.66)], fill=c, width=e)
    return lay.resize((tam, tam), Image.LANCZOS)


def cartao(w, h):
    """Cartão branco, cantos de 20px e borda fininha (deal-card)."""
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(lay).rounded_rectangle([0, 0, w - 1, h - 1], radius=R_MD, fill=BRANCO + (255,),
                                          outline=LINHA + (255,), width=BORDA)
    return lay


def arredondar(im, raio):
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius=raio, fill=255)
    out = im.convert("RGBA")
    out.putalpha(mask)
    return out


def avatar(d):
    """Bolinha laranja com "MM" (avatar de quem postou)."""
    lay = Image.new("RGBA", (d, d), (0, 0, 0, 0))
    ImageDraw.Draw(lay).ellipse([0, 0, d - 1, d - 1], fill=LARANJA + (255,))
    t = text_layer("MM", NEGRITO, int(d * 0.38), BRANCO)
    lay.paste(t, ((d - t.width) // 2, (d - t.height) // 2), t)
    return lay


def autor(subtitulo, escala=1.0):
    """Linha de quem postou: avatar + "MultiMulti Ofertas" + subtítulo."""
    d = int(84 * escala)
    av = avatar(d)
    nome = text_layer("MultiMulti Ofertas", NEGRITO, int(34 * escala), TINTA)
    sub = text_layer(subtitulo, MEDIO, int(28 * escala), CORPO)
    w = d + 22 + max(nome.width, sub.width)
    lay = Image.new("RGBA", (w, d), (0, 0, 0, 0))
    lay.paste(av, (0, 0), av)
    alt = nome.height + 10 + sub.height
    y = (d - alt) // 2
    lay.paste(nome, (d + 22, y), nome)
    lay.paste(sub, (d + 22, y + nome.height + 10), sub)
    return lay


# ---------- foto ----------

def trim_white(im, thr=245):
    im = im.convert("RGB")
    bg = Image.new("RGB", im.size, (255, 255, 255))
    diff = ImageChops.difference(im, bg).convert("L").point(lambda p: 255 if p > 255 - thr else 0)
    box = diff.getbbox()
    return im.crop(box) if box else im


def load_photo(path):
    im = Image.open(path)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        base = Image.new("RGB", im.size, BRANCO)
        base.paste(im, mask=im.split()[-1])
        im = base
    return trim_white(im.convert("RGB"))


def moldura_foto(path, w, h, pad=30):
    """Foto do produto dentro de uma moldura arredondada com borda fininha."""
    campo = Image.new("RGB", (w, h), BRANCO)
    ph = ImageOps.contain(load_photo(path), (w - 2 * pad, h - 2 * pad), Image.LANCZOS)
    campo.paste(ph, ((w - ph.width) // 2, (h - ph.height) // 2))
    lay = arredondar(campo, R_MD)
    ImageDraw.Draw(lay).rounded_rectangle([0, 0, w - 1, h - 1], radius=R_MD, outline=LINHA + (255,), width=BORDA)
    return lay


# ---------- partes do cartão ----------

def numero_de(cfg):
    if cfg.get("numero"):
        return cfg["numero"]
    m = re.search(r"(\d+)", " ".join(cfg.get("cta") or []))
    return m.group(1) if m else ""


def desconto(cfg):
    b = cfg.get("badge") or ""
    return b if "%" in b else None


def subtitulo(cfg):
    cat = (cfg.get("category") or "").lower()
    return f"achei pra você · {cat}" if cat and cat != "achado" else "achei pra você"


def linha_preco(cfg, tam, maxw):
    """Preço laranja + (desconto em menta) + pílula de vendas em vermelho."""
    pr = preco_layer(cfg["new"], tam, LARANJA_FORTE, maxw)
    pecas = [pr]
    if desconto(cfg):
        pecas.append(pilula(desconto(cfg), int(tam * 0.36), MENTA, VERDE_FORTE))
    vendas = (cfg.get("extra") or "").replace("⭐ ", "nota ")
    if vendas:
        pecas.append(pilula(vendas, int(tam * 0.34), BRANCO, QUENTE, borda=LINHA, icone="sobe", cor_icone=QUENTE))
    gap = 22

    def linha(ps):
        lay = Image.new("RGBA", (sum(p.width for p in ps) + gap * (len(ps) - 1), max(p.height for p in ps)), (0, 0, 0, 0))
        x = 0
        for p in ps:
            lay.paste(p, (x, (lay.height - p.height) // 2), p)
            x += p.width + gap
        return lay

    tudo = linha(pecas)
    if tudo.width <= maxw or len(pecas) == 1:
        return tudo
    l1, l2 = linha(pecas[:-1]), pecas[-1]  # não coube: a pílula de vendas desce
    lay = Image.new("RGBA", (max(l1.width, l2.width), l1.height + 18 + l2.height), (0, 0, 0, 0))
    lay.paste(l1, (0, 0), l1)
    lay.paste(l2, (0, l1.height + 18), l2)
    return lay


def salvar(img, out):
    if out.lower().endswith((".jpg", ".jpeg")):  # o Instagram só aceita JPEG
        img.convert("RGB").save(out, quality=93)
    else:
        img.save(out)


# ---------- peças chamativas ----------

def selo_numero(numero, d=170):
    """Selo redondo laranja com o número da vitrine, colado no canto da foto."""
    lay = Image.new("RGBA", (d, d), (0, 0, 0, 0))
    ImageDraw.Draw(lay).ellipse([0, 0, d - 1, d - 1], fill=LARANJA + (255,), outline=BRANCO + (255,), width=8)
    a = text_layer("nº", NEGRITO, int(d * 0.2), BRANCO)
    b = fit_layer(str(numero), FORTE, int(d * 0.46), BRANCO, int(d * 0.7))
    alt = a.height + 6 + b.height
    y = (d - alt) // 2
    lay.paste(a, ((d - a.width) // 2, y), a)
    lay.paste(b, ((d - b.width) // 2, y + a.height + 6), b)
    return lay


def chamada_de(cfg):
    return cfg.get("chamada") or "Olha esse achado"


def topo_laranja(img, cfg, y, larg_util, tam=64):
    """Chamada em branco à esquerda e pílula da categoria à direita, sobre o laranja."""
    cat = (cfg.get("category") or "").strip()
    pc = pilula(cat, 30, BRANCO, LARANJA_FORTE, padx=30, pady=14) if cat and cat.lower() != "achado" else None
    maxw = larg_util - (pc.width + 24 if pc else 0)
    ch = fit_layer(chamada_de(cfg), FORTE, tam, BRANCO, maxw)
    img.paste(ch, (M + 6, y), ch)
    if pc:
        img.paste(pc, (M + larg_util - pc.width, y + (ch.height - pc.height) // 2), pc)
    return ch.height


def miolo_cartao(img, cfg, x0, y0, larg, y_fim, tam_tit=48, tam_preco=128, selo=170):
    """Foto + título + preço/vendas dentro do cartão, entre y0 e y_fim."""
    lp = linha_preco_forte(cfg, tam_preco, larg)
    yp = y_fim - lp.height
    tit = bloco(cfg["title"], NEGRITO, tam_tit, TINTA, larg, linhas=2)
    yt = yp - 24 - tit.height
    foto = moldura_foto(cfg["photo"], larg, yt - 32 - y0)
    img.paste(foto, (x0, y0), foto)
    sl = selo_numero(numero_de(cfg), selo)
    img.paste(sl, (x0 + larg - sl.width + 24, y0 - 24), sl)
    img.paste(tit, (x0, yt), tit)
    img.paste(lp, (x0, yp), lp)


def linha_preco_forte(cfg, tam, maxw):
    """Preço grande em laranja + desconto (menta) + vendas em pílula vermelha cheia."""
    pr = preco_layer(cfg["new"], tam, LARANJA_FORTE, maxw)
    pecas = [pr]
    if desconto(cfg):
        pecas.append(pilula(desconto(cfg), int(tam * 0.3), MENTA, VERDE_FORTE))
    vendas = (cfg.get("extra") or "").replace("⭐ ", "nota ")
    if vendas:
        pecas.append(pilula(vendas, int(tam * 0.27), QUENTE, BRANCO, icone="sobe"))
    gap = 22

    def linha(ps):
        lay = Image.new("RGBA", (sum(p.width for p in ps) + gap * (len(ps) - 1), max(p.height for p in ps)), (0, 0, 0, 0))
        x = 0
        for p in ps:
            lay.paste(p, (x, (lay.height - p.height) // 2 + (6 if p is not pr else 0)), p)
            x += p.width + gap
        return lay

    tudo = linha(pecas)
    if tudo.width <= maxw or len(pecas) == 1:
        return tudo
    l1, l2 = linha(pecas[:-1]), pecas[-1]
    lay = Image.new("RGBA", (max(l1.width, l2.width), l1.height + 16 + l2.height), (0, 0, 0, 0))
    lay.paste(l1, (0, 0), l1)
    lay.paste(l2, (0, l1.height + 16), l2)
    return lay


def cartao_liso(w, h, raio=None):
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(lay).rounded_rectangle([0, 0, w - 1, h - 1], radius=raio or R_MD + 8, fill=BRANCO + (255,))
    return lay


# ---------- feed ----------

def feed(cfg, out):
    img = Image.new("RGB", (W, H), LARANJA)
    larg_util = W - 2 * M
    h_topo = topo_laranja(img, cfg, 50, larg_util)

    cy0 = 50 + h_topo + 34
    cw, ch = W - 2 * M, H - M - cy0
    card = cartao_liso(cw, ch)
    img.paste(card, (M, cy0), card)
    x0, larg = M + PAD, cw - 2 * PAD

    btn = pilula(f"Link na bio · nº {numero_de(cfg)}", 44, LARANJA, BRANCO, icone="seta", padx=0, pady=28)
    # botão de ponta a ponta do cartão
    b = Image.new("RGBA", (larg, btn.height), (0, 0, 0, 0))
    ImageDraw.Draw(b).rounded_rectangle([0, 0, larg - 1, btn.height - 1], radius=btn.height // 2, fill=LARANJA + (255,))
    miolo = btn.crop((0, 0, btn.width, btn.height))
    b.paste(miolo, ((larg - miolo.width) // 2, 0), miolo)
    yb = cy0 + ch - PAD - b.height
    img.paste(b, (x0, yb), b)

    miolo_cartao(img, cfg, x0, cy0 + PAD, larg, yb - 30)
    salvar(img, out)
    return img


# ---------- story ----------

def story(cfg, out):
    SW, SH = 1080, 1920
    img = Image.new("RGB", (SW, SH), LARANJA)
    # o Instagram cobre ~200px em cima e ~180px embaixo
    t1 = fit_layer("Olha o que achei hoje", FORTE, 84, BRANCO, SW - 2 * M)
    img.paste(t1, (M + 6, 240), t1)
    t2 = text_layer("Toca no link da bio e procura o número", MEDIO, 36, BRANCO)
    img.paste(t2, (M + 6, 240 + t1.height + 20), t2)

    cy0 = 240 + t1.height + 20 + t2.height + 50
    btn = pilula(f"Link na bio · nº {numero_de(cfg)}", 52, BRANCO, LARANJA_FORTE, icone="seta", padx=60, pady=32)
    yb = 1730 - btn.height
    cy1 = yb - 40
    cw = SW - 2 * M
    card = cartao_liso(cw, cy1 - cy0)
    img.paste(card, (M, cy0), card)
    img.paste(btn, ((SW - btn.width) // 2, yb), btn)

    x0, larg = M + PAD, cw - 2 * PAD
    miolo_cartao(img, cfg, x0, cy0 + PAD, larg, cy1 - PAD, tam_tit=54, tam_preco=140, selo=190)
    salvar(img, out)
    return img
