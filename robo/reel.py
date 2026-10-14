"""Reels 1080x1920, 30fps, 10s, no estilo cartão de oferta (DESIGN.md mydealz + laranja da marca).

Três momentos, em tom de conversa:
  1. (0–2,4s)  "Olha esse achado" / "por R$ 12,99" em letras grandes, com quem postou em cima
  2. (2,4–8s)  o cartão da oferta sobe: foto, nome, preço e vendas aparecem em sequência
  3. (8–10s)   "Gostou?" + botão "Link na bio · nº X" + "Salva pra não perder"
O conteúdo fica entre y=220 e y=1450 e longe da borda direita (botões do Instagram).

reel(cfg, saida.mp4)
cfg: photo, hook (lista de 2 linhas), title, new, numero, extra (opcional), badge, category
"""
import subprocess

from PIL import Image

from .arte import (CANVAS, CORPO, LARANJA, LARANJA_FORTE, LINHA, MEDIO, NEGRITO, PAD, TINTA,
                   BRANCO, autor, bloco, cartao, linha_preco, moldura_foto, numero_de, pilula,
                   subtitulo, text_layer, fit_layer, load_photo)

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


def _partes_cartao(cfg, cw):
    """Peças do cartão separadas, para entrarem uma de cada vez."""
    larg = cw - 2 * PAD
    au = autor(subtitulo(cfg))
    tit = bloco(cfg.get("title") or "", NEGRITO, 54, TINTA, larg, linhas=2)
    lp = linha_preco(cfg, 120, larg)
    foto = moldura_foto(cfg["photo"], larg, 640)
    alt = PAD + au.height + 30 + foto.height + 34 + tit.height + 30 + lp.height + PAD
    return au, foto, tit, lp, cartao(cw, alt)


def reel(cfg, out, segundos=10.0):
    numero = numero_de(cfg)
    linhas = (cfg.get("hook") or ["Olha esse achado", f"por {cfg['new']}"])[:2]
    # 1. gancho
    au_g = autor(subtitulo(cfg))
    h1 = fit_layer(linhas[0], NEGRITO, 120, TINTA, USO)
    h2 = fit_layer(linhas[1], NEGRITO, 120, LARANJA_FORTE, USO) if len(linhas) > 1 else None
    # 2. cartão
    cw = W - 2 * M
    au, foto, tit, lp, card = _partes_cartao(cfg, cw)
    cy = max(220, 840 - card.height // 2)
    # 3. chamada
    gostou = text_layer("Gostou?", NEGRITO, 130, TINTA)
    btn = pilula(f"Link na bio · nº {numero}", 64, LARANJA, BRANCO, icone="seta", padx=70, pady=40)
    perfil = text_layer("@multimulti.ofertas", MEDIO, 48, CORPO)
    salva = pilula("Salva pra não perder", 46, BRANCO, TINTA, borda=LINHA, padx=50, pady=30)

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
        img = Image.new("RGB", (W, H), CANVAS)
        if t < 2.4:  # 1. gancho
            _entra(img, au_g, M, 660, t / 0.3)
            _entra(img, h1, M - 4, 840, (t - 0.2) / 0.35, sobe=50)
            if h2 is not None:
                _entra(img, h2, M - 4, 840 + h1.height + 40, (t - 0.45) / 0.35, sobe=50)
        elif t < 8.0:  # 2. cartão da oferta
            lt = t - 2.4
            a = _ease(lt / 0.45)
            y0 = int(cy + 160 * (1 - a))
            c = card if a >= 1 else card.copy()
            if a < 1:
                c.putalpha(c.getchannel("A").point(lambda v: int(v * a)))
            img.paste(c, (M, y0), c)
            x0, y = M + PAD, y0 + PAD
            _entra(img, au, x0, y, (lt - 0.2) / 0.3, sobe=0)
            y += au.height + 30
            _entra(img, foto, x0, y, (lt - 0.3) / 0.4, sobe=20)
            y += foto.height + 34
            _entra(img, tit, x0, y, (lt - 0.9) / 0.35)
            y += tit.height + 30
            _entra(img, lp, x0, y, (lt - 1.4) / 0.35)
        else:  # 3. chamada
            lt = t - 8.0
            _entra(img, gostou, M - 4, 680, lt / 0.3, sobe=50)
            _entra(img, btn, M, 680 + gostou.height + 70, (lt - 0.15) / 0.3)
            yb = 680 + gostou.height + 70 + btn.height
            _entra(img, perfil, M + 6, yb + 40, (lt - 0.3) / 0.3)
            _entra(img, salva, M, yb + 40 + perfil.height + 70, (lt - 0.45) / 0.3)
        proc.stdin.write(img.tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg falhou ao gerar o Reels")
