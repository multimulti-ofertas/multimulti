"""Reels 1080x1920, 30fps, 10s, sem música (a música entra pelo Instagram ou fica muda).

Quatro telas cheias, cada uma com uma coisa grande (taste-skill: nada de tela quase vazia):
  1. gancho em letras enormes sobre laranja
  2. o produto grande sobre branco, com o nome
  3. o cartaz de preço sobre laranja
  4. "Link na bio · nº X" sobre preto
O conteúdo fica entre y=220 e y=1450 e longe da borda direita, fora da área que o Instagram
cobre com a legenda e os botões.

reel(cfg, saida.mp4)
cfg: photo, hook (lista de até 3 linhas), new, numero, extra (opcional), title (opcional)
"""
import math
import subprocess

from PIL import Image, ImageDraw, ImageOps

from .arte import (BK, DISPLAY, OR, TEXTO, WH, bloco, fit_layer, load_photo, marca,
                   preco_layer, text_layer)

W, H, FPS = 1080, 1920, 30
M = 72
USO = W - 2 * M - 80  # largura útil (fica longe dos botões da direita)


def _ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def _entra(img, layer, x, y, t, sobe=40):
    """Entrada: sobe alguns pixels e aparece (só transparência e posição)."""
    a = _ease(t)
    if a <= 0.01:
        return
    lay = layer
    if a < 1:
        lay = layer.copy()
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    img.paste(lay, (int(x), int(y + sobe * (1 - a))), lay)


def reel(cfg, out, segundos=10.0):
    numero = cfg.get("numero", "")
    # 1. gancho
    linhas = [l.upper() for l in cfg["hook"][:3]]
    tam_fonte = 230  # todas as linhas do mesmo tamanho
    while tam_fonte > 60 and any(text_layer(l, DISPLAY, tam_fonte, BK).width > USO for l in linhas):
        tam_fonte -= 6
    hook = [text_layer(l, DISPLAY, tam_fonte, BK) for l in linhas]
    # 2. produto
    ph = load_photo(cfg["photo"])
    ph = ImageOps.contain(ph, (W - 2 * M, 860), Image.LANCZOS)
    titulo = bloco(cfg.get("title") or "", TEXTO, 64, BK, USO, linhas=2) if cfg.get("title") else None
    mk_claro = marca(52, fundo_claro=True)
    mk_escuro = marca(52, fundo_claro=False)
    # 3. preço
    preco = preco_layer(cfg["new"], 520, BK, USO)
    extra = fit_layer(cfg["extra"].replace("⭐ ", "nota "), TEXTO, 56, BK, USO) if cfg.get("extra") else None
    # 4. chamada
    c1 = fit_layer("Link na bio", DISPLAY, 230, WH, USO)
    c2 = fit_layer(f"nº {numero}", DISPLAY, 420, OR, USO)
    c3 = text_layer("@multimulti.ofertas", TEXTO, 52, (210, 210, 210))

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
        if t < 2.0:  # 1. gancho
            img = Image.new("RGB", (W, H), OR)
            alt = sum(h.height for h in hook) + 40 * (len(hook) - 1)
            y = 820 - alt // 2
            for k, hl in enumerate(hook):
                _entra(img, hl, M - 6, y, (t - 0.12 * k) / 0.35, sobe=60)
                y += hl.height + 40
        elif t < 5.2:  # 2. produto
            lt = t - 2.0
            img = Image.new("RGB", (W, H), WH)
            img.paste(mk_claro, (M, 230), mk_claro)
            z = 1.0 + 0.06 * (lt / 3.2)  # zoom lento na foto
            fz = ph.resize((int(ph.width * z), int(ph.height * z)), Image.LANCZOS)
            img.paste(fz, ((W - fz.width) // 2, 340 + (900 - fz.height) // 2))
            if titulo is not None:
                _entra(img, titulo, M, 1300, (lt - 0.3) / 0.4)
        elif t < 8.0:  # 3. preço
            lt = t - 5.2
            img = Image.new("RGB", (W, H), OR)
            yp = 820 - preco.height // 2
            _entra(img, preco, M - 10, yp, lt / 0.4, sobe=80)
            if extra is not None:
                _entra(img, extra, M, yp + preco.height + 60, (lt - 0.5) / 0.35)
        else:  # 4. chamada
            lt = t - 8.0
            img = Image.new("RGB", (W, H), BK)
            img.paste(mk_escuro, (M, 230), mk_escuro)
            _entra(img, c1, M - 6, 520, lt / 0.3)
            pulso = 1 + 0.03 * math.sin(lt * 9) if lt > 0.5 else 1
            c2p = c2.resize((int(c2.width * pulso), int(c2.height * pulso)), Image.LANCZOS)
            _entra(img, c2p, M - 10, 520 + c1.height + 60, (lt - 0.15) / 0.3)
            _entra(img, c3, M, 520 + c1.height + 60 + c2.height + 70, (lt - 0.35) / 0.3)
        proc.stdin.write(img.tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg falhou ao gerar o Reels")
