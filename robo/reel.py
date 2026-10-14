"""Reels 1080x1920, 30fps, 10s: vitrine de produto premium no escuro.

Um só cenário contínuo (fundo quase preto com o brilho laranja), como um site de produto "2026":
  1. (0–2s)    a marca aparece e a chamada sobe: "ACHADO DO DIA" / "POR R$ 12,99"
  2. (2–6s)    o produto entra flutuando com o brilho crescendo; o nome aparece embaixo
  3. (6–8,3s)  o preço gigante em laranja + vendas
  4. (8,3–10s) "LINK NA BIO" + círculo com o número
O conteúdo fica entre y=220 e y=1450 e longe da borda direita (botões do Instagram).

reel(cfg, saida.mp4)
cfg: photo, hook (lista de 2 linhas), title, new, numero, extra, badge, category
"""
import math
import subprocess

from PIL import Image

from .arte import (BRANCO, CINZA, FUNDO, GROSSA, GROSSA2, LARANJA, LARANJA_CLARO, TEXTO, bloco,
                   brilho, chao, circulo_numero, fit_layer, linha_vendas, marca, numero_de,
                   preco_layer, produto, rotulo, seta, text_layer, titulo_caps)

W, H, FPS = 1080, 1920, 30
M = 72
USO = W - 2 * M - 60


def _ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def _entra(img, layer, x, y, t, sobe=40):
    a = _ease(t)
    if a <= 0.01:
        return
    lay = layer
    if a < 1:
        lay = layer.copy()
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    img.alpha_composite(lay, (int(x), int(y + sobe * (1 - a))))


def reel(cfg, out, segundos=10.0):
    numero = numero_de(cfg)
    linhas = cfg.get("hook") or ["Olha esse achado", f"por {cfg['new']}"]
    mk = marca(52)
    # 1. chamada
    h1 = fit_layer(linhas[0].upper(), GROSSA, 150, BRANCO, USO)
    h2 = fit_layer(linhas[1].upper(), GROSSA, 150, LARANJA, USO) if len(linhas) > 1 else None
    # 2. produto e nome
    prod = produto(cfg["photo"], 900, 760)
    rot = text_layer(rotulo(cfg), GROSSA2, 36, LARANJA, tracking=0.14)
    nome = bloco(titulo_caps(cfg.get("title") or ""), GROSSA, 92, BRANCO, USO, linhas=2)
    # 3. preço
    preco = preco_layer(cfg["new"], 330, LARANJA, USO)
    vend = linha_vendas(cfg)
    vend_l = text_layer(vend, TEXTO, 50, CINZA) if vend else None
    # 4. chamada final
    lb = text_layer("LINK NA BIO", GROSSA, 170, BRANCO, tracking=0.04)
    st = seta(110)
    cn = circulo_numero(numero, 300)
    arroba = text_layer("@multimulti.ofertas", TEXTO, 48, CINZA)

    # fundos prontos (o brilho é o mais caro de calcular)
    cy_prod = 760
    fundos = {}
    for k in range(0, 11):
        img = Image.new("RGBA", (W, H), FUNDO + (255,))
        r = 380 + 50 * k
        img.alpha_composite(brilho(W, H, W // 2, cy_prod, r, forca=0.55 + 0.03 * k))
        img.alpha_composite(brilho(W, H, W // 2, cy_prod, r * 0.45, LARANJA_CLARO, 0.3))
        fundos[k] = img
    piso = chao(W, H, W // 2, cy_prod + prod.height // 2 + 40, int(prod.width * 0.8), 80)

    n = int(segundos * FPS)
    proc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
         "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium",
         "-crf", "20", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out],
        stdin=subprocess.PIPE)

    for i in range(n):
        t = i / FPS
        k = 10 if t >= 2.0 else int(10 * _ease(t / 2.0))
        img = fundos[2 if t < 2.0 else k].copy()
        _entra(img, mk, (W - mk.width) // 2, 230, t / 0.4, sobe=0)
        if t < 2.0:  # 1. chamada
            y = 820
            _entra(img, h1, M - 4, y, (t - 0.2) / 0.35, sobe=70)
            if h2 is not None:
                _entra(img, h2, M - 4, y + h1.height + 36, (t - 0.45) / 0.35, sobe=70)
        else:
            lt = t - 2.0
            # produto flutuando (sobe e desce devagar)
            a = _ease(lt / 0.7)
            bob = 14 * math.sin(lt * 1.8)
            esc = 0.9 + 0.1 * a
            p = prod.resize((int(prod.width * esc), int(prod.height * esc)), Image.LANCZOS)
            if a < 1:
                p = p.copy()
                p.putalpha(p.getchannel("A").point(lambda v: int(v * a)))
            if t < 8.3:
                img.alpha_composite(piso)
                img.alpha_composite(p, ((W - p.width) // 2, int(cy_prod - p.height / 2 + 120 * (1 - a) + bob)))
            if t < 6.0:  # 2. nome
                y = 1230
                _entra(img, rot, M, y, (lt - 0.6) / 0.35)
                _entra(img, nome, M - 3, y + rot.height + 22, (lt - 0.8) / 0.35)
            elif t < 8.3:  # 3. preço
                lt3 = t - 6.0
                y = 1200
                _entra(img, preco, M - 6, y, lt3 / 0.35, sobe=60)
                if vend_l is not None:
                    _entra(img, vend_l, M, y + preco.height + 24, (lt3 - 0.35) / 0.35)
            else:  # 4. chamada final
                lt4 = t - 8.3
                _entra(img, lb, M - 4, 560, lt4 / 0.3, sobe=50)
                _entra(img, st, M, 560 + lb.height + 50, (lt4 - 0.15) / 0.3)
                pul = 1 + 0.025 * math.sin(lt4 * 8)
                c2 = cn.resize((int(cn.width * pul), int(cn.height * pul)), Image.LANCZOS)
                _entra(img, c2, W - M - 60 - c2.width, 560 + lb.height + 10, (lt4 - 0.25) / 0.3)
                _entra(img, arroba, M, 560 + lb.height + 50 + st.height + 60, (lt4 - 0.4) / 0.3)
        proc.stdin.write(img.convert("RGB").tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg falhou ao gerar o Reels")
