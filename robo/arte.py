"""Artes MultiMulti, v3: o cartaz de oferta de supermercado vira o layout.

Ideia: o preço gigante com os centavos pequenos no alto, como no cartaz pintado à mão do mercado,
e o número da vitrine como etiqueta preta. Regras (taste-skill): poucos tamanhos de letra e bem
diferentes, foto grande sem moldura, campos de cor chapada, nada de etiquetinha, contorno fino,
listras, sombra ou degradê.

feed(cfg, saida)  -> 1080x1350
story(cfg, saida) -> 1080x1920

cfg: photo (caminho), title, new ("R$ 48,47"), numero, extra (opcional, ex.: "+100 mil vendidos"),
     badge (opcional, só aparece se for desconto, ex.: "45% OFF")
"""
import os
import re

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps

W, H = 1080, 1350
OR = (255, 107, 26)
BK = (17, 17, 17)
WH = (255, 255, 255)

_AQUI = os.path.join(os.path.dirname(__file__), "fontes")
DISPLAY = os.path.join(_AQUI, "BarlowCondensed-Black.ttf")      # preço, número, ganchos
DISPLAY2 = os.path.join(_AQUI, "BarlowCondensed-ExtraBold.ttf")
TEXTO = os.path.join(_AQUI, "Barlow-SemiBold.ttf")                # título e linhas pequenas
TEXTO_B = os.path.join(_AQUI, "Barlow-Bold.ttf")
# nomes antigos (usados em outros módulos)
BOLD, COND = TEXTO_B, DISPLAY

M = 56  # margem única de todas as artes


# ---------- texto ----------

def fonte(path, size):
    return ImageFont.truetype(path, size)


def text_layer(text, path, size, color, sx=1.0, tracking=0.0):
    """Uma linha de texto numa camada transparente justa (sem a folga de cima da fonte)."""
    f = fonte(path, size)
    if tracking:
        larg = sum(f.getlength(c) for c in text) + tracking * size * (len(text) - 1)
        asc, desc = f.getmetrics()
        lay = Image.new("RGBA", (int(larg) + 8, asc + desc + 8), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        x = 4
        for c in text:
            d.text((x, 4), c, font=f, fill=color)
            x += f.getlength(c) + tracking * size
        box = lay.getbbox()
        lay = lay.crop(box) if box else lay
    else:
        l, t, r, b = f.getbbox(text)
        lay = Image.new("RGBA", (r - l + 4, b - t + 4), (0, 0, 0, 0))
        ImageDraw.Draw(lay).text((-l + 2, -t + 2), text, font=f, fill=color)
    if sx != 1.0:
        lay = lay.resize((max(1, int(lay.width * sx)), lay.height), Image.LANCZOS)
    return lay


def fit_layer(text, path, size, color, maxw, sx=1.0, tracking=0.0):
    """Texto numa linha, diminuindo a fonte até caber em maxw."""
    while size > 12:
        lay = text_layer(text, path, size, color, sx, tracking)
        if lay.width <= maxw:
            return lay
        size -= 4
    return text_layer(text, path, size, color, sx, tracking)


def wrap(text, path, size, maxw, sx=1.0):
    f = fonte(path, size)
    lines, cur = [], ""
    for w in text.split():
        test = (cur + " " + w).strip()
        if f.getlength(test) * sx <= maxw:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def bloco(text, path, size, color, maxw, linhas=2, entrelinha=1.12):
    """Até `linhas` linhas; diminui a fonte até caber, e só corta palavras se ainda assim não couber."""
    while True:
        ls = wrap(text, path, size, maxw)
        if len(ls) <= linhas or size <= 34:
            break
        size -= 2
    if len(ls) > linhas:
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


def preco_partes(valor):
    """"R$ 1.299,90" -> ("1.299", "90")."""
    m = re.search(r"([\d\.]+),(\d{2})", valor or "")
    if not m:
        return (re.sub(r"[^\d\.]", "", valor or "") or "0"), ""
    return m.group(1), m.group(2)


def preco_layer(valor, altura, color, maxw):
    """Preço de cartaz: "R$" pequeno, reais gigantes, centavos pequenos no alto."""
    reais, cent = preco_partes(valor)
    while True:
        big = text_layer(reais, DISPLAY, altura, color, tracking=-0.02)
        rs = text_layer("R$", DISPLAY2, int(altura * 0.26), color)
        ct = text_layer("," + cent, DISPLAY, int(altura * 0.42), color) if cent else None
        gap = int(altura * 0.04)
        larg = rs.width + gap + big.width + (gap + ct.width if ct else 0)
        if larg <= maxw or altura < 60:
            break
        altura = int(altura * 0.92)
    lay = Image.new("RGBA", (larg, big.height), (0, 0, 0, 0))
    lay.paste(rs, (0, 0), rs)  # "R$" alinhado no alto, como no cartaz
    lay.paste(big, (rs.width + gap, 0), big)
    if ct:
        lay.paste(ct, (rs.width + 2 * gap + big.width, 0), ct)
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
        base = Image.new("RGB", im.size, WH)
        base.paste(im, mask=im.split()[-1])
        im = base
    return trim_white(im.convert("RGB"))


def campo_foto(path, w, h, pad=40):
    """Campo branco do tamanho pedido com a foto o maior possível dentro dele."""
    campo = Image.new("RGB", (w, h), WH)
    ph = ImageOps.contain(load_photo(path), (w - 2 * pad, h - 2 * pad), Image.LANCZOS)
    campo.paste(ph, ((w - ph.width) // 2, (h - ph.height) // 2))
    return campo


def marca(altura, fundo_claro=True):
    """Logotipo "multimulti": primeira metade na cor do texto, segunda em laranja."""
    c1 = BK if fundo_claro else WH
    a = text_layer("MULTI", DISPLAY, altura, c1, tracking=0.01)
    b = text_layer("MULTI", DISPLAY, altura, OR, tracking=0.01)
    lay = Image.new("RGBA", (a.width + b.width + 2, max(a.height, b.height)), (0, 0, 0, 0))
    lay.paste(a, (0, 0), a)
    lay.paste(b, (a.width + 2, 0), b)
    return lay


def etiqueta(numero, largura, cor_fundo=BK):
    """Etiqueta preta com o número da vitrine e "link na bio" embaixo."""
    num = fit_layer(f"nº {numero}", DISPLAY, 210, WH, largura - 60)
    sub = text_layer("link na bio", TEXTO_B, 40, OR)
    alt = 36 + num.height + 26 + sub.height + 36
    lay = Image.new("RGBA", (largura, alt), cor_fundo + (255,))
    lay.paste(num, ((largura - num.width) // 2, 36), num)
    lay.paste(sub, ((largura - sub.width) // 2, 36 + num.height + 26), sub)
    return lay


def numero_de(cfg):
    if cfg.get("numero"):
        return cfg["numero"]
    m = re.search(r"(\d+)", " ".join(cfg.get("cta") or []))
    return m.group(1) if m else ""


def desconto(cfg):
    b = cfg.get("badge") or ""
    return b if "%" in b else None


def salvar(img, out):
    if out.lower().endswith((".jpg", ".jpeg")):  # o Instagram só aceita JPEG
        img.convert("RGB").save(out, quality=93)
    else:
        img.save(out)


# ---------- feed ----------

def feed(cfg, out):
    img = Image.new("RGB", (W, H), OR)
    TOPO = 760
    ImageDraw.Draw(img).rectangle([0, 0, W, TOPO], fill=WH)
    img.paste(campo_foto(cfg["photo"], W, TOPO - 90, pad=40), (0, 90))  # faixa de cima é da marca
    mk = marca(40)
    img.paste(mk, (M, 44), mk)

    # título (até 2 linhas)
    tit = bloco(cfg["title"], TEXTO, 50, BK, W - 2 * M, linhas=2)
    img.paste(tit, (M, TOPO + 44), tit)

    # etiqueta do número, à direita, encostada no pé
    et = etiqueta(numero_de(cfg), 300)
    img.paste(et, (W - M - et.width, H - M - et.height), et)

    # preço de cartaz, à esquerda
    area = W - 2 * M - et.width - 40
    pr = preco_layer(cfg["new"], 320, BK, area)
    linha = cfg.get("extra") or ""
    if desconto(cfg):
        linha = f"{desconto(cfg)} · {linha}" if linha else desconto(cfg)
    ex = fit_layer(linha.replace("⭐ ", "nota "), TEXTO, 36, BK, area) if linha else None
    # preço + linha de vendas terminam na mesma altura da etiqueta
    fundo = H - M
    if ex:
        img.paste(ex, (M, fundo - ex.height), ex)
        fundo -= ex.height + 30
    img.paste(pr, (M - 6, fundo - pr.height), pr)

    salvar(img, out)
    return img


# ---------- story ----------

def story(cfg, out):
    SW, SH = 1080, 1920
    img = Image.new("RGB", (SW, SH), OR)
    TOPO = 950
    # o alto do story fica coberto pela barra do Instagram: a foto começa mais abaixo
    ImageDraw.Draw(img).rectangle([0, 0, SW, TOPO], fill=WH)
    img.paste(campo_foto(cfg["photo"], SW, TOPO - 300, pad=40), (0, 300))
    mk = marca(46)
    img.paste(mk, (M, 230), mk)

    tit = bloco(cfg["title"], TEXTO, 56, BK, SW - 2 * M, linhas=2)
    img.paste(tit, (M, TOPO + 50), tit)
    y = TOPO + 50 + tit.height + 50

    # faixa preta da chamada, acima da área da caixa de resposta do Instagram
    fy0, fy1 = 1580, 1740
    linha = cfg.get("extra") or ""
    if desconto(cfg):
        linha = f"{desconto(cfg)} · {linha}" if linha else desconto(cfg)
    ex = fit_layer(linha.replace("⭐ ", "nota "), TEXTO, 40, BK, SW - 2 * M) if linha else None
    fundo = fy0 - 44
    if ex:
        img.paste(ex, (M, fundo - ex.height), ex)
        fundo -= ex.height + 30
    alt = 420
    while True:  # o preço ocupa todo o espaço livre entre o título e as vendas
        pr = preco_layer(cfg["new"], alt, BK, SW - 2 * M)
        if pr.height <= fundo - y or alt < 120:
            break
        alt -= 10
    img.paste(pr, (M - 8, fundo - pr.height), pr)

    ImageDraw.Draw(img).rectangle([0, fy0, SW, fy1], fill=BK)
    c1 = text_layer("Link na bio", DISPLAY, 92, WH)
    c2 = text_layer(f"nº {numero_de(cfg)}", DISPLAY, 92, OR)
    tot = c1.width + 30 + c2.width
    cy = (fy0 + fy1) // 2
    img.paste(c1, ((SW - tot) // 2, cy - c1.height // 2), c1)
    img.paste(c2, ((SW - tot) // 2 + c1.width + 30, cy - c2.height // 2), c2)

    salvar(img, out)
    return img
