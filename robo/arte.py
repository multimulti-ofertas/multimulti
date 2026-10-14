"""Artes MultiMulti: vitrine de produto premium, no escuro.

Inspiração: sites de produto "2026" — fundo quase preto, o produto flutuando grande e inclinado com
um brilho colorido atrás (aqui, o laranja da marca), o nome em maiúsculas grossas e condensadas,
textos pequenos e elegantes, e um círculo com o número como a "seta" de um carrossel.

feed(cfg, saida)  -> 1080x1350
story(cfg, saida) -> 1080x1920
recorte(foto)     -> (imagem RGBA sem o fundo branco, True) ou (foto, False) se o fundo não for branco

cfg: photo (caminho), title, new ("R$ 48,47"), numero, extra (ex.: "+100 mil vendidos"),
     badge (só aparece se for desconto, ex.: "45% OFF"), category (opcional), chamada (opcional)
"""
import math
import os
import re

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps

# ---------- cores ----------
FUNDO = (10, 10, 12)
LARANJA = (255, 107, 26)
LARANJA_CLARO = (255, 150, 80)
BRANCO = (255, 255, 255)
CINZA = (168, 168, 176)
CINZA_ESCURO = (60, 60, 66)
# nomes antigos usados por outros módulos
OR, BK, WH = LARANJA, FUNDO, BRANCO

_AQUI = os.path.join(os.path.dirname(__file__), "fontes")
GROSSA = os.path.join(_AQUI, "BarlowCondensed-Black.ttf")     # nome, preço, chamadas
GROSSA2 = os.path.join(_AQUI, "BarlowCondensed-Bold.ttf")     # rótulos em maiúsculas
TEXTO = os.path.join(_AQUI, "Barlow-Medium.ttf")              # textos pequenos
TEXTO_B = os.path.join(_AQUI, "Barlow-SemiBold.ttf")
BOLD = COND = DISPLAY = GROSSA

W, H = 1080, 1350
M = 64


# ---------- texto ----------

def fonte(path, size):
    return ImageFont.truetype(path, size)


def text_layer(text, path, size, color, sx=1.0, tracking=0.0):
    """Uma linha de texto numa camada justa. tracking em fração do tamanho (0.12 = espaçado)."""
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
        return lay.crop(box) if box else lay
    l, t, r, b = f.getbbox(text)
    lay = Image.new("RGBA", (r - l + 4, b - t + 4), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((-l + 2, -t + 2), text, font=f, fill=color)
    return lay


def fit_layer(text, path, size, color, maxw, sx=1.0, tracking=0.0):
    while size > 12:
        lay = text_layer(text, path, size, color, tracking=tracking)
        if lay.width <= maxw:
            return lay
        size -= 2
    return text_layer(text, path, size, color, tracking=tracking)


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


def bloco(text, path, size, color, maxw, linhas=2, entrelinha=0.98):
    while True:
        ls = wrap(text, path, size, maxw)
        if len(ls) <= linhas or size <= 34:
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
    return lay.crop((0, box[1], box[2], box[3])) if box else lay


def preco_layer(valor, altura, color, maxw):
    """Preço: "R$" menor alinhado no alto, número grande."""
    m = re.match(r"\s*R\$\s*(.+)", valor or "")
    num = m.group(1) if m else (valor or "")
    while True:
        big = text_layer(num, GROSSA, altura, color)
        rs = text_layer("R$", GROSSA2, int(altura * 0.34), color)
        gap = int(altura * 0.06)
        if rs.width + gap + big.width <= maxw or altura < 40:
            break
        altura = int(altura * 0.92)
    lay = Image.new("RGBA", (rs.width + gap + big.width, big.height), (0, 0, 0, 0))
    lay.paste(rs, (0, int(big.height * 0.04)), rs)
    lay.paste(big, (rs.width + gap, 0), big)
    return lay


def titulo_caps(t):
    return (t or "").upper()


# ---------- luz e produto ----------

def brilho(w, h, cx, cy, raio, cor=LARANJA, forca=0.85):
    """Brilho radial colorido (o "holofote" atrás do produto), como camada RGBA."""
    y, x = np.ogrid[:h, :w]
    d = np.sqrt((x - cx) ** 2 + ((y - cy) * 1.05) ** 2) / raio
    a = np.clip(1 - d, 0, 1) ** 2.2 * forca
    lay = np.zeros((h, w, 4), dtype=np.uint8)
    lay[..., 0], lay[..., 1], lay[..., 2] = cor
    lay[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(lay, "RGBA")


def chao(w, h, cx, cy, larg, alt, cor=LARANJA, forca=0.55):
    """Reflexo de luz no "chão", embaixo do produto."""
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(lay).ellipse([cx - larg // 2, cy - alt // 2, cx + larg // 2, cy + alt // 2],
                                fill=cor + (int(255 * forca),))
    return lay.filter(ImageFilter.GaussianBlur(alt * 0.6))


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


def recorte(path):
    """Tira o fundo branco da foto (só o branco que encosta na borda). Se a borda não for quase toda
    branca (foto com cenário), devolve a foto inteira e False."""
    from scipy import ndimage
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(int)
    claro = (a.min(axis=2) > 232) & ((a.max(axis=2) - a.min(axis=2)) < 18)
    borda = np.concatenate([claro[0], claro[-1], claro[:, 0], claro[:, -1]])
    if borda.mean() < 0.85:
        return load_photo(path), False
    lab, _ = ndimage.label(claro)
    ids = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    fundo = np.isin(lab, list(ids))
    alpha = Image.fromarray(np.where(fundo, 0, 255).astype(np.uint8))
    alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    out = im.convert("RGBA")
    out.putalpha(alpha)
    box = alpha.getbbox()
    return (out.crop(box) if box else out), True


def produto(path, caixa_w, caixa_h, angulo=-7):
    """O produto pronto para flutuar: recortado e inclinado, ou num quadro arredondado inclinado."""
    im, ok = recorte(path)
    if ok:
        im = ImageOps.contain(im, (caixa_w, caixa_h), Image.LANCZOS)
        return im.rotate(angulo, resample=Image.BICUBIC, expand=True)
    im = ImageOps.contain(im, (int(caixa_w * 0.86), int(caixa_h * 0.86)), Image.LANCZOS).convert("RGBA")
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius=28, fill=255)
    im.putalpha(mask)
    return im.rotate(angulo * 0.5, resample=Image.BICUBIC, expand=True)


def cena(w, h, path, cx, cy, caixa_w, caixa_h, raio_brilho, flutua=0.0, escala=1.0, angulo=-7, prod=None):
    """Fundo escuro + brilho + reflexo + produto centrado em (cx, cy). Devolve RGB."""
    img = Image.new("RGBA", (w, h), FUNDO + (255,))
    img.alpha_composite(brilho(w, h, cx, cy, raio_brilho))
    img.alpha_composite(brilho(w, h, cx, cy, raio_brilho * 0.45, LARANJA_CLARO, 0.35))
    p = prod if prod is not None else produto(path, caixa_w, caixa_h, angulo)
    if escala != 1.0:
        p = p.resize((max(1, int(p.width * escala)), max(1, int(p.height * escala))), Image.LANCZOS)
    py = int(cy - p.height / 2 + flutua)
    img.alpha_composite(chao(w, h, cx, int(cy + p.height / 2 + 30), int(p.width * 0.8), 70))
    img.alpha_composite(p, (int(cx - p.width / 2), py))
    return img


# ---------- peças ----------

def marca(altura=40):
    a = text_layer("MULTI", GROSSA, altura, BRANCO, tracking=0.06)
    b = text_layer("MULTI", GROSSA, altura, LARANJA, tracking=0.06)
    lay = Image.new("RGBA", (a.width + b.width + int(altura * 0.06), max(a.height, b.height)), (0, 0, 0, 0))
    lay.paste(a, (0, 0), a)
    lay.paste(b, (a.width + int(altura * 0.06), 0), b)
    return lay


def circulo_numero(numero, d=150, cor=LARANJA):
    """Círculo de contorno com o número, como a seta de um carrossel."""
    s = 3
    D = d * s
    lay = Image.new("RGBA", (D, D), (0, 0, 0, 0))
    ImageDraw.Draw(lay).ellipse([4 * s, 4 * s, D - 4 * s, D - 4 * s], outline=cor + (255,), width=4 * s)
    lay = lay.resize((d, d), Image.LANCZOS)
    a = text_layer("Nº", GROSSA2, int(d * 0.17), CINZA, tracking=0.1)
    b = fit_layer(str(numero), GROSSA, int(d * 0.44), BRANCO, int(d * 0.66))
    alt = a.height + 8 + b.height
    y = (d - alt) // 2
    lay.paste(a, ((d - a.width) // 2, y), a)
    lay.paste(b, ((d - b.width) // 2, y + a.height + 8), b)
    return lay


def seta(tam, cor=BRANCO):
    s = 4
    T = tam * s
    lay = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    e = int(T * 0.09)
    d.line([(T * 0.12, T * 0.5), (T * 0.86, T * 0.5)], fill=cor + (255,), width=e)
    d.line([(T * 0.58, T * 0.22), (T * 0.88, T * 0.5), (T * 0.58, T * 0.78)], fill=cor + (255,), width=e, joint="curve")
    return lay.resize((tam, tam), Image.LANCZOS)


def numero_de(cfg):
    if cfg.get("numero"):
        return cfg["numero"]
    m = re.search(r"(\d+)", " ".join(cfg.get("cta") or []))
    return m.group(1) if m else ""


def desconto(cfg):
    b = cfg.get("badge") or ""
    return b if "%" in b else None


def rotulo(cfg):
    cat = (cfg.get("category") or "").strip().upper()
    base = "ACHADO DO DIA"
    return f"{cat} · {base}" if cat and cat != "ACHADO" else base


def linha_vendas(cfg):
    partes = []
    if desconto(cfg):
        partes.append(desconto(cfg))
    if cfg.get("extra"):
        partes.append(cfg["extra"].replace("⭐ ", "nota "))
    return " · ".join(partes)


def salvar(img, out):
    if out.lower().endswith((".jpg", ".jpeg")):  # o Instagram só aceita JPEG
        img.convert("RGB").save(out, quality=93)
    else:
        img.save(out)


def texto_oferta(img, cfg, x, y, larg, tam_nome=86, tam_preco=200):
    """Rótulo laranja, nome em maiúsculas, preço grande e vendas. Devolve o y final."""
    r = text_layer(rotulo(cfg), GROSSA2, 30, LARANJA, tracking=0.14)
    img.alpha_composite(r, (x, y))
    y += r.height + 22
    nome = bloco(titulo_caps(cfg["title"]), GROSSA, tam_nome, BRANCO, larg, linhas=2)
    img.alpha_composite(nome, (x - 3, y))
    y += nome.height + 26
    pr = preco_layer(cfg["new"], tam_preco, LARANJA, larg)
    img.alpha_composite(pr, (x - 4, y))
    vend = linha_vendas(cfg)
    if vend:
        v = text_layer(vend, TEXTO, 34, CINZA)
        if pr.width + 36 + v.width <= larg:
            img.alpha_composite(v, (x + pr.width + 36, y + pr.height - v.height - 6))
        else:
            img.alpha_composite(v, (x, y + pr.height + 18))
            y += v.height + 18
    return y + pr.height


def _ajusta(p, caixa_w, caixa_h):
    """Garante que o produto (já inclinado) caiba na caixa."""
    if p.width > caixa_w or p.height > caixa_h:
        p = ImageOps.contain(p, (caixa_w, caixa_h), Image.LANCZOS)
    return p


# ---------- feed ----------

def feed(cfg, out):
    larg = W - 2 * M
    cn = circulo_numero(numero_de(cfg), 150)
    yb = H - M - cn.height
    tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fim = texto_oferta(tmp, cfg, M, 0, larg)
    y0 = yb - 50 - fim                       # topo do bloco de texto

    topo, base = 120, y0 - 40                # espaço do produto
    p = _ajusta(produto(cfg["photo"], 820, base - topo), 900, base - topo)
    img = cena(W, H, None, 540, (topo + base) // 2, 0, 0, 720, prod=p)
    mk = marca(40)
    img.alpha_composite(mk, ((W - mk.width) // 2, 56))

    lb = text_layer("LINK NA BIO", GROSSA2, 40, BRANCO, tracking=0.12)
    st = seta(40)
    img.alpha_composite(lb, (M, yb + (cn.height - lb.height) // 2))
    img.alpha_composite(st, (M + lb.width + 22, yb + (cn.height - st.height) // 2))
    img.alpha_composite(cn, (W - M - cn.width, yb))
    texto_oferta(img, cfg, M, y0, larg)
    salvar(img, out)
    return img


# ---------- story ----------

def story(cfg, out):
    SW, SH = 1080, 1920
    larg = SW - 2 * M
    cn = circulo_numero(numero_de(cfg), 170)
    yb = 1720 - cn.height                    # acima da caixa de resposta do Instagram
    tmp = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    fim = texto_oferta(tmp, cfg, M, 0, larg, tam_nome=96, tam_preco=230)
    y0 = yb - 60 - fim

    topo, base = 320, y0 - 50
    p = _ajusta(produto(cfg["photo"], 880, base - topo), 940, base - topo)
    img = cena(SW, SH, None, 540, (topo + base) // 2, 0, 0, 820, prod=p)
    mk = marca(46)
    img.alpha_composite(mk, ((SW - mk.width) // 2, 230))

    lb = text_layer("LINK NA BIO", GROSSA2, 50, BRANCO, tracking=0.12)
    st = seta(50)
    dm = text_layer("ou responde o story que eu te mando o link", TEXTO, 32, CINZA)
    bloco_h = lb.height + 16 + dm.height
    yl = yb + (cn.height - bloco_h) // 2
    img.alpha_composite(lb, (M, yl))
    img.alpha_composite(st, (M + lb.width + 26, yl + (lb.height - st.height) // 2))
    img.alpha_composite(dm, (M, yl + lb.height + 16))
    img.alpha_composite(cn, (SW - M - cn.width, yb))
    texto_oferta(img, cfg, M, y0, larg, tam_nome=96, tam_preco=230)
    salvar(img, out)
    return img
