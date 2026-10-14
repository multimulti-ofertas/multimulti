"""Reels 1080x1920, 30fps, 10s, no estilo cartão de oferta (DESIGN.md mydealz + laranja da marca).

Três momentos sobre laranja, em tom de conversa:
  1. (0–2,4s)  "Olha esse achado" / "por R$ 12,99" em letras grandes, com a categoria em cima
  2. (2,4–8s)  o cartão da oferta sobe: foto, selo do número, nome, preço e vendas
  3. (8–10s)   "Gostou?" + botão "Link na bio · nº X" + "Salva pra não perder"
O conteúdo fica entre y=220 e y=1450 e longe da borda direita (botões do Instagram).

reel(cfg, saida.mp4)
cfg: photo, hook (lista de 2 linhas), title, new, numero, extra (opcional), badge, category
"""
import subprocess

from PIL import Image, ImageDraw

from .arte import (BRANCO, FORTE, LARANJA, LARANJA_FORTE, MEDIO, PAD, R_MD, TINTA, cartao_liso,
                   fit_layer, miolo_cartao, numero_de, pilula, text_layer)

W, H, FPS = 1080, 1920, 30
M = 64
USO = W - 2 * M - 60  # largura útil, longe dos botões da direita


def _ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def _entra(img, layer, x, y, t, sobe=40):
    """Entrada: sobe alguns pixels e aparece."""
    a = _ease(t)
    if a <= 0.01:
        return
    lay = layer
    if a < 1:
        lay = layer.copy()
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    img.paste(lay, (int(x), int(y + sobe * (1 - a))), lay)


def _cartao_pronto(cfg, cw, ch):
    """O cartão inteiro (foto, título, preço, selo) numa camada só, para deslizar junto."""
    base = Image.new("RGB", (cw + 60, ch + 60), LARANJA)
    card = cartao_liso(cw, ch)
    base.paste(card, (30, 30), card)
    miolo_cartao(base, cfg, 30 + PAD, 30 + PAD, cw - 2 * PAD, 30 + ch - PAD,
                 tam_tit=54, tam_preco=140, selo=190)
    lay = base.convert("RGBA")
    # tudo que é laranja de fundo fora do cartão vira transparente
    m = Image.new("L", lay.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([30, 30, 30 + cw - 1, 30 + ch - 1], radius=R_MD + 8, fill=255)
    ImageDraw.Draw(m).ellipse([30 + cw - PAD - 190 + 24 - 2, 30 + PAD - 24 - 2, 30 + cw - PAD + 24 + 2, 30 + PAD - 24 + 190 + 2], fill=255)
    lay.putalpha(m)
    return lay


def reel(cfg, out, segundos=10.0):
    numero = numero_de(cfg)
    linhas = (cfg.get("hook") or ["Olha esse achado", f"por {cfg['new']}"])[:2]
    # 1. gancho
    cat = (cfg.get("category") or "").strip()
    pc = pilula(cat, 40, BRANCO, LARANJA_FORTE, padx=40, pady=18) if cat and cat.lower() != "achado" else None
    h1 = fit_layer(linhas[0], FORTE, 130, BRANCO, USO)
    h2 = fit_layer(linhas[1], FORTE, 130, TINTA, USO) if len(linhas) > 1 else None
    # 2. cartão
    cw, ch = W - 2 * M, 1180
    card = _cartao_pronto(cfg, cw, ch)
    cy = 260
    # 3. chamada
    gostou = text_layer("Gostou?", FORTE, 150, BRANCO)
    btn = pilula(f"Link na bio · nº {numero}", 64, BRANCO, LARANJA_FORTE, icone="seta", padx=70, pady=40)
    perfil = text_layer("@multimulti.ofertas", MEDIO, 50, BRANCO)
    salva = pilula("Salva pra não perder", 46, None, BRANCO, borda=BRANCO, padx=50, pady=30)

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
        img = Image.new("RGB", (W, H), LARANJA)
        if t < 2.4:  # 1. gancho
            y = 700
            if pc is not None:
                _entra(img, pc, M, y - pc.height - 50, t / 0.3)
            _entra(img, h1, M - 4, y, (t - 0.15) / 0.35, sobe=60)
            if h2 is not None:
                _entra(img, h2, M - 4, y + h1.height + 44, (t - 0.4) / 0.35, sobe=60)
        elif t < 8.0:  # 2. cartão da oferta sobe
            lt = t - 2.4
            _entra(img, card, M - 30, cy - 30, lt / 0.5, sobe=220)
        else:  # 3. chamada
            lt = t - 8.0
            _entra(img, gostou, M - 4, 640, lt / 0.3, sobe=50)
            yb = 640 + gostou.height + 80
            _entra(img, btn, M, yb, (lt - 0.15) / 0.3)
            yb += btn.height
            _entra(img, perfil, M + 6, yb + 44, (lt - 0.3) / 0.3)
            _entra(img, salva, M, yb + 44 + perfil.height + 70, (lt - 0.45) / 0.3)
        proc.stdin.write(img.tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg falhou ao gerar o Reels")
