"""Artes no padrão MultiMulti (laranja/preto).

feed(cfg, saida)  -> 1080x1350
story(cfg, saida) -> 1080x1920

cfg: photo (caminho), category, badge, title, new, old (opcional), extra (opcional),
     cta ([linha1, linha2]), hook (story)
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageOps

W, H = 1080, 1350
OR = (255, 107, 26)
BK = (17, 17, 17)
WH = (255, 255, 255)
_FONTS = "/usr/share/fonts/truetype/dejavu/"
BOLD = os.path.join(_FONTS, "DejaVuSans-Bold.ttf")
COND = os.path.join(_FONTS, "DejaVuSansCondensed-Bold.ttf")


def text_layer(text, path, size, color, sx=1.0):
    f = ImageFont.truetype(path, size)
    l, t, r, b = f.getbbox(text)
    lay = Image.new("RGBA", (r - l + 4, b - t + 4), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((-l + 2, -t + 2), text, font=f, fill=color)
    if sx != 1.0:
        lay = lay.resize((max(1, int(lay.width * sx)), lay.height), Image.LANCZOS)
    return lay


def fit_layer(text, path, size, color, maxw, sx=1.0):
    """Texto numa linha, diminuindo a fonte até caber em maxw."""
    while size > 12:
        lay = text_layer(text, path, size, color, sx)
        if lay.width <= maxw:
            return lay
        size -= 4
    return text_layer(text, path, size, color, sx)


def wrap(text, path, size, maxw, sx=1.0):
    f = ImageFont.truetype(path, size)
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


def feed(cfg, out):
    img = Image.new("RGB", (W, H), OR)
    d = ImageDraw.Draw(img)

    # barra do topo
    d.rectangle([0, 0, W, 110], fill=BK)
    m1 = text_layer("MULTI", COND, 58, WH, 0.85)
    m2 = text_layer("MULTI", COND, 58, OR, 0.85)
    img.paste(m1, (48, 55 - m1.height // 2), m1)
    img.paste(m2, (48 + m1.width, 55 - m2.height // 2), m2)
    cat = text_layer(cfg["category"].upper(), BOLD, 26, OR)
    cw, ch = cat.width + 44, 52
    cx = W - 48 - cw
    d.rectangle([cx, 55 - ch // 2, cx + cw, 55 + ch // 2], outline=OR, width=4)
    img.paste(cat, (cx + 22, 55 - cat.height // 2), cat)

    # foto
    bx0, by0, bx1, by1 = 48, 150, W - 48, 830
    d.rectangle([bx0, by0, bx1, by1], fill=WH, outline=BK, width=8)
    ph = load_photo(cfg["photo"])
    iw, ih = bx1 - bx0 - 60, by1 - by0 - 130
    ph = ImageOps.contain(ph, (iw, ih), Image.LANCZOS)
    img.paste(ph, (bx0 + 30 + (iw - ph.width) // 2, by0 + 100 + (ih - ph.height) // 2))

    # selo
    bd = text_layer(cfg["badge"], COND, 44, WH, 0.85)
    d.rectangle([bx0 + 24, by0 + 24, bx0 + 24 + bd.width + 36, by0 + 24 + bd.height + 28], fill=BK)
    img.paste(bd, (bx0 + 42, by0 + 38), bd)

    # título
    y = 870
    for line in wrap(cfg["title"], BOLD, 40, W - 96, 0.92)[:2]:
        tl = text_layer(line, BOLD, 40, BK, 0.92)
        img.paste(tl, (48, y), tl)
        y += 54

    # preços
    y += 26
    if cfg.get("old"):
        old = text_layer("De " + cfg["old"], BOLD, 30, BK, 0.95)
        img.paste(old, (48, y), old)
        d.line([46, y + old.height // 2 + 1, 50 + old.width, y + old.height // 2 + 1], fill=BK, width=4)
        y += old.height + 14
    else:
        por = text_layer("POR APENAS", BOLD, 30, BK, 0.95)
        img.paste(por, (48, y), por)
        y += por.height + 14
    new = fit_layer(cfg["new"], COND, 150, BK, 640, 0.85)
    img.paste(new, (44, y), new)
    if cfg.get("extra"):
        ex = fit_layer(cfg["extra"], BOLD, 32, WH, 700, 0.95)
        img.paste(ex, (48, y + new.height + 16), ex)

    # caixa CTA
    cta = cfg.get("cta", ["LINK NA", "BIO"])
    l1 = text_layer(cta[0], BOLD, 28, WH)
    l2 = text_layer(cta[1], BOLD, 28, WH)
    bw = max(l1.width, l2.width) + 48
    bh = l1.height + l2.height + 48
    x0 = W - 48 - bw
    yc = y + new.height // 2 - bh // 2
    d.rectangle([x0, yc, x0 + bw, yc + bh], fill=BK)
    img.paste(l1, (x0 + (bw - l1.width) // 2, yc + 18), l1)
    img.paste(l2, (x0 + (bw - l2.width) // 2, yc + 18 + l1.height + 12), l2)

    if out.lower().endswith((".jpg", ".jpeg")):
        img.save(out, quality=92)
    else:
        img.save(out)
    return img


def stripes(w, h):
    img = Image.new("RGB", (w, h), BK)
    d = ImageDraw.Draw(img)
    for x in range(-h, w, 80):
        d.polygon([(x, h), (x + 26, h), (x + 26 + h, 0), (x + h, 0)], fill=(28, 28, 28))
    return img


def story(cfg, out):
    SW, SH = 1080, 1920
    tmp = out + ".tmp.png"
    fimg = feed(cfg, tmp)
    os.remove(tmp)

    img = stripes(SW, SH)
    d = ImageDraw.Draw(img)
    y = 230
    hk = fit_layer(cfg.get("hook", "ACHADINHO DO DIA"), COND, 84, OR, SW - 100, 0.85)
    img.paste(hk, ((SW - hk.width) // 2, y), hk)

    fw = 960
    f2 = fimg.resize((fw, int(fimg.height * fw / fimg.width)), Image.LANCZOS)
    fy = y + hk.height + 50
    d.rectangle([(SW - fw) // 2 - 6, fy - 6, (SW + fw) // 2 + 6, fy + f2.height + 6], fill=OR)
    img.paste(f2, ((SW - fw) // 2, fy))

    by = fy + f2.height + 50
    t = text_layer("TOQUE NO LINK", BOLD, 46, WH)
    img.paste(t, ((SW - t.width) // 2, by), t)
    ay = by + t.height + 18
    d.polygon([(SW // 2 - 34, ay), (SW // 2 + 34, ay), (SW // 2, ay + 38)], fill=OR)
    img.save(out)
    return img
