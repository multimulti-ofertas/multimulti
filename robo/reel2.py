"""Reels v2 (com narração): legenda animada sincronizada com a voz, produto com zoom/balanço e "pancada"
no preço, etiqueta de preço que entra na hora em que a voz fala o preço e o cartão final (link na bio + nº).

reel_narrado(cfg, saida, voz_wav, tempos)
  cfg: photo, numero (como no reel.py)
  tempos: [{"id": gancho|nome|preco|prova|cta, "tela": texto, "ini": s, "fim": s}] (robo/voz.roteiro)
"""
import math
import re
import subprocess

from PIL import Image, ImageFilter

from . import musica
from .arte import (BRANCO, CINZA, FUNDO, GROSSA, LARANJA, LARANJA_CLARO, TEXTO, brilho, chao, circulo_numero,
                   fit_layer, marca, preco_layer, produto, seta, text_layer)

W, H, FPS, M = 1080, 1920, 30, 72
USO = W - 2 * M - 60          # longe dos botões do Instagram na direita
CY_PROD = 800                 # centro do produto
Y_PRECO = 1150                # etiqueta de preço
Y_LEGENDA = 1500              # centro da legenda (acima da faixa do nome/legenda do Instagram)


def _ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def _alpha(lay, a):
    if a >= 0.999:
        return lay
    lay = lay.copy()
    lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    return lay


def _sombra(lay, raio=10, forca=200):
    """Texto com sombra escura borrada (lê em cima de qualquer coisa)."""
    pad = raio * 3
    base = Image.new("RGBA", (lay.width + 2 * pad, lay.height + 2 * pad), (0, 0, 0, 0))
    sombra = Image.new("RGBA", lay.size, (0, 0, 0, 255))
    sombra.putalpha(lay.getchannel("A").point(lambda v: min(255, int(v * forca / 255 * 1.6))))
    base.alpha_composite(sombra, (pad, pad + 6))
    base = base.filter(ImageFilter.GaussianBlur(raio))
    base.alpha_composite(lay, (pad, pad))
    return base


def _blocos(texto, max_palavras=3, max_chars=16):
    """Divide a legenda em pedaços curtos (como os Reels com legenda que aparece aos poucos)."""
    texto = re.sub(r"R\$\s+", "R$\u00a0", texto)  # "R$ 40" nunca se separa
    ws, out, cur = texto.split(" "), [], []
    for w in ws:
        if cur and (len(cur) >= max_palavras or len(" ".join(cur + [w])) > max_chars):
            out.append(cur)
            cur = []
        cur.append(w)
    if cur:
        out.append(cur)
    return out


class Legenda:
    """Camadas prontas de cada pedaço, com a palavra falada em laranja."""

    def __init__(self, tempos):
        self.itens = []  # (ini, fim, [camadas por palavra destacada], tempos das palavras)
        for p in tempos:
            if p["id"] in ("preco", "cta"):  # preço e link já aparecem grandes na tela
                continue
            blocos = _blocos(p["tela"].replace(" · ", ", ").upper())
            total = sum(len(" ".join(b)) for b in blocos) or 1
            t = p["ini"]
            dur = p["fim"] - p["ini"]
            for b in blocos:
                d = dur * len(" ".join(b)) / total
                cams = [self._camada(b, k) for k in range(len(b))]
                pesos = [len(w) + 1 for w in b]
                marcos, acc = [], t
                for pz in pesos:
                    marcos.append(acc)
                    acc += d * pz / sum(pesos)
                self.itens.append((t, t + d, cams, marcos))
                t += d
        if self.itens:  # o 1º pedaço já aparece no 1º quadro (quem rola o feed sem som lê o gancho)
            ini, fim, cams, marcos = self.itens[0]
            self.itens[0] = (0.0, fim, cams, marcos)

    @staticmethod
    def _camada(palavras, destaque):
        tam = 112
        while True:
            partes = [text_layer(w, GROSSA, tam, LARANJA if i == destaque else BRANCO) for i, w in enumerate(palavras)]
            esp = int(tam * 0.22)
            larg = sum(p.width for p in partes) + esp * (len(partes) - 1)
            if larg <= USO or tam <= 60:
                break
            tam -= 6
        alt = max(p.height for p in partes)
        lay = Image.new("RGBA", (larg, alt), (0, 0, 0, 0))
        x = 0
        for p in partes:
            lay.alpha_composite(p, (x, alt - p.height))
            x += p.width + esp
        return _sombra(lay)

    def quadro(self, t):
        for ini, fim, cams, marcos in self.itens:
            if ini <= t < fim:
                k = max(i for i, m in enumerate(marcos) if m <= t) if t >= marcos[0] else 0
                pop = 1 + 0.12 * (1 - _ease((t - ini) / 0.12))  # cada pedaço entra com um "pulo"
                return cams[k], pop
        return None, 1.0


def reel_narrado(cfg, out, voz_wav, tempos):
    numero = cfg["numero"]
    fim_fala = tempos[-1]["fim"]
    total = max(10.0, round(fim_fala + 1.0, 2))
    t_preco = next((p["ini"] for p in tempos if p["id"] == "preco"), 3.0)
    t_cta = next((p["ini"] for p in tempos if p["id"] == "cta"), total - 2.0)

    mk = marca(52)
    prod = produto(cfg["photo"], 880, 720, angulo=0)
    preco = _sombra(preco_layer(cfg["new"], 230, LARANJA, USO))
    lb = text_layer("LINK NA BIO", GROSSA, 170, BRANCO, tracking=0.04)
    st = seta(110)
    cn = circulo_numero(numero, 280)
    arroba = text_layer("@multimulti.ofertas", TEXTO, 48, CINZA)
    leg = Legenda(tempos)

    fundo = Image.new("RGBA", (W, H), FUNDO + (255,))
    fundo.alpha_composite(brilho(W, H, W // 2, CY_PROD, 760, forca=0.72))
    fundo.alpha_composite(brilho(W, H, W // 2, CY_PROD, 330, LARANJA_CLARO, 0.32))
    piso = chao(W, H, W // 2, CY_PROD + prod.height // 2 + 30, int(prod.width * 0.75), 80)

    som = musica.escolher(numero)
    musica_in = ["-stream_loop", "-1", "-i", str(som)] if som else \
        ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"]
    filtro = (f"[1:a]volume=0.20,afade=t=out:st={total - 1.2:.2f}:d=1.2[m];"
              f"[2:a]apad[v];[m][v]amix=inputs=2:duration=first:normalize=0[a]")
    proc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", *musica_in, "-i", str(voz_wav), "-filter_complex", filtro,
         "-map", "0:v", "-map", "[a]", "-t", f"{total:.2f}", "-c:v", "libx264", "-pix_fmt", "yuv420p",
         "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out],
        stdin=subprocess.PIPE)

    for i in range(int(total * FPS)):
        t = i / FPS
        img = fundo.copy()
        img.alpha_composite(mk, ((W - mk.width) // 2, 290))
        fim_card = _ease((t - t_cta) / 0.45) if t >= t_cta else 0.0

        # produto: entra com "pancada", aproxima devagar, balança, pulsa no preço e encolhe no final
        esc = 1.0 + 0.25 * (1 - _ease(t / 0.35)) + 0.06 * (t / total)
        if t >= t_preco:
            esc += 0.09 * math.exp(-(t - t_preco) * 7)
        esc *= 1 - 0.42 * fim_card
        ang = 2.2 * math.sin(t * 1.4)
        p = prod.resize((max(1, int(prod.width * esc)), max(1, int(prod.height * esc))), Image.BILINEAR)
        p = p.rotate(ang, resample=Image.BICUBIC, expand=True)
        p = _alpha(p, min(1.0, t / 0.12))
        cy = CY_PROD + 10 * math.sin(t * 1.9) - 190 * fim_card
        if fim_card < 0.5:
            img.alpha_composite(_alpha(piso, 1 - fim_card * 2))
        img.alpha_composite(p, (int((W - p.width) / 2), int(cy - p.height / 2)))

        # etiqueta de preço (entra quando a voz fala o preço)
        if t_preco <= t < t_cta + 0.3:
            a = _ease((t - t_preco) / 0.22) * (1 - _ease((t - t_cta) / 0.3) if t > t_cta else 1)
            s = 1 + 0.35 * (1 - _ease((t - t_preco) / 0.22))
            pr = preco.resize((int(preco.width * s), int(preco.height * s)), Image.BILINEAR) if s > 1.001 else preco
            img.alpha_composite(_alpha(pr, a), (int((W - pr.width) / 2), int(Y_PRECO - (pr.height - preco.height) / 2)))

        # legenda
        cam, pop = leg.quadro(t)
        if cam is not None and t < t_cta:
            c = cam.resize((int(cam.width * pop), int(cam.height * pop)), Image.BILINEAR) if pop > 1.001 else cam
            img.alpha_composite(c, (int((W - c.width) / 2), int(Y_LEGENDA - c.height / 2)))

        # cartão final
        if fim_card > 0:
            lt = t - t_cta
            y0 = 1010
            img.alpha_composite(_alpha(lb, _ease(lt / 0.3)), ((W - lb.width) // 2, int(y0 + 40 * (1 - _ease(lt / 0.3)))))
            y1 = y0 + lb.height + 50
            pul = 1 + 0.03 * math.sin(lt * 8)
            c2 = cn.resize((int(cn.width * pul), int(cn.height * pul)), Image.LANCZOS)
            a2 = _ease((lt - 0.15) / 0.3)
            img.alpha_composite(_alpha(st, a2), (W // 2 - st.width - 40, y1 + (cn.height - st.height) // 2))
            img.alpha_composite(_alpha(c2, a2), (W // 2 + 20, y1 + (cn.height - c2.height) // 2))
            img.alpha_composite(_alpha(arroba, _ease((lt - 0.3) / 0.3)), ((W - arroba.width) // 2, y1 + cn.height + 50))
        proc.stdin.write(img.convert("RGB").tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg falhou ao gerar o Reels narrado")
    return total
