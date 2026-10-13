"""Reels 1080x1920, 30fps, ~10s, sem música (a música entra pelo Instagram ou fica muda).

reel(cfg, saida.mp4)
cfg: photo, hook (lista de até 4 linhas), badge, new, old (opcional), extra, numero
"""
import math
import subprocess
from PIL import Image, ImageDraw
from .arte import text_layer, fit_layer, load_photo, stripes, BOLD, COND, OR, BK, WH

W, H, FPS = 1080, 1920, 30


def _ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def _pop(t):
    t = max(0.0, min(1.0, t))
    if t < 0.6:
        return _ease(t / 0.6) * 1.12
    return 1.12 - 0.12 * _ease((t - 0.6) / 0.4)


def _paste(img, layer, cx, cy, s):
    if s <= 0.01:
        return
    lay = layer.resize((max(1, int(layer.width * s)), max(1, int(layer.height * s))), Image.LANCZOS)
    img.paste(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)), lay)


def _box(layer, color, px=30, py=20):
    b = Image.new("RGBA", (layer.width + 2 * px, layer.height + 2 * py), color + (255,))
    b.paste(layer, (px, py), layer)
    return b


def reel(cfg, out, segundos=10.0):
    bg = stripes(W, H)
    m1 = text_layer("MULTI", COND, 54, WH, 0.85)
    m2 = text_layer("MULTI", COND, 54, OR, 0.85)

    hook = [fit_layer(l, COND, 120, c, W - 80, 0.85)
            for l, c in zip(cfg["hook"], [WH, OR, WH, OR])]
    badge = _box(text_layer(cfg["badge"], COND, 70, BK, 0.85), OR)
    old = None
    if cfg.get("old"):
        old = text_layer("DE " + cfg["old"], BOLD, 64, WH)
        ImageDraw.Draw(old).line([0, old.height // 2 + 2, old.width, old.height // 2 + 2], fill=OR, width=8)
    por = text_layer("POR APENAS", BOLD, 50, WH)
    new = fit_layer(cfg["new"], COND, 230, OR, W - 80, 0.85)
    extra = _box(fit_layer(cfg.get("extra", ""), BOLD, 50, BK, W - 160), OR, 25, 17) if cfg.get("extra") else None
    cta1 = text_layer("LINK NA BIO", COND, 130, OR, 0.85)
    cta2 = text_layer(f"PRODUTO Nº {cfg['numero']}", BOLD, 64, WH)
    cta3 = text_layer("@multimulti.ofertas", BOLD, 44, (200, 200, 200))

    ph = load_photo(cfg["photo"])
    ph.thumbnail((900, 900), Image.LANCZOS)
    card = Image.new("RGB", (ph.width + 60, ph.height + 60), WH)
    card.paste(ph, (30, 30))
    ImageDraw.Draw(card).rectangle([0, 0, card.width - 1, card.height - 1], outline=OR, width=10)
    card = card.convert("RGBA")
    small = card.resize((int(card.width * 0.5), int(card.height * 0.5)), Image.LANCZOS)

    n = int(segundos * FPS)
    proc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
         "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium",
         "-crf", "21", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out],
        stdin=subprocess.PIPE)

    for i in range(n):
        t = i / FPS
        img = bg.copy()
        x = (W - m1.width - m2.width) // 2
        img.paste(m1, (x, 150), m1)
        img.paste(m2, (x + m1.width, 150), m2)
        if t < 2.2:  # gancho
            y0 = 900 - (len(hook) - 1) * 82
            for k, hl in enumerate(hook):
                _paste(img, hl, W / 2, y0 + k * 165, _pop((t - 0.15 * k) / 0.45))
        elif t < 5.4:  # produto
            lt = t - 2.2
            s = _pop(lt / 0.4) * (1.0 + 0.06 * (lt / 3.2))
            _paste(img, card, W / 2, 900, s * min(1.0, 940 / card.width))
            _paste(img, badge, 300, 470, _pop((lt - 0.5) / 0.35))
        elif t < 8.2:  # preço
            lt = t - 5.4
            img.paste(small, ((W - small.width) // 2, 300), small)
            base = 300 + small.height + 70
            if old is not None:
                a = _ease(lt / 0.3)
                _paste(img, old, W / 2, base + 40 - 20 * (1 - a), a)
            if lt > 0.4:
                _paste(img, por, W / 2, base + 140, _ease((lt - 0.4) / 0.25))
            if lt > 0.6:
                _paste(img, new, W / 2, base + 300, _pop((lt - 0.6) / 0.4))
            if extra is not None and lt > 1.3:
                _paste(img, extra, W / 2, base + 500, _pop((lt - 1.3) / 0.35))
        else:  # chamada
            lt = t - 8.2
            pulse = 1 + 0.04 * math.sin(lt * 10)
            _paste(img, cta1, W / 2, 760, _pop(lt / 0.4) * pulse)
            _paste(img, cta2, W / 2, 920, _ease((lt - 0.3) / 0.3))
            _paste(img, cta3, W / 2, 1020, _ease((lt - 0.5) / 0.3))
            if lt > 0.6:
                ay = 1110 + int(12 * math.sin(lt * 8))
                ImageDraw.Draw(img).polygon([(W // 2 - 40, ay), (W // 2 + 40, ay), (W // 2, ay + 46)], fill=OR)
        proc.stdin.write(img.tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg falhou ao gerar o Reels")
