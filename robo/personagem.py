"""Zé Multi: o personagem 2D que apresenta os Reels narrados.

aplicar(reel_mp4, voz_wav, tempos) pega o Reels pronto (robo/reel2.py) e monta a versão com o Zé:
o Zé na metade de cima (boca mexendo com a voz, piscando, sobrancelha no preço, cabeça balançando)
e o Reels original reduzido embaixo. Desenho vetorial (SVG → cairosvg), nítido em qualquer tamanho.
Se der qualquer erro, o Reels original fica como estava.
"""
import math
import random
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

from .arte import FUNDO, LARANJA

W, H, FPS = 1080, 1920, 30
TAM = 820                 # lado do desenho do Zé na tela
X_ZE, Y_ZE = (W - TAM) // 2, 40
Y_CORTE = 860             # onde termina a área do Zé
Y_REEL = 840              # topo do Reels reduzido
CORTE_REEL = (420, 1160)  # faixa do Reels original que vai embaixo (y, altura): produto, preço, legenda
ALT_REEL = 1060

_DEFS = """<defs>
<linearGradient id="skin" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#D99A72"/><stop offset="1" stop-color="#B97A55"/></linearGradient>
<linearGradient id="cap" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FF8A3D"/><stop offset="1" stop-color="#F0600F"/></linearGradient>
<linearGradient id="brim" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F26512"/><stop offset="1" stop-color="#C94C08"/></linearGradient>
<linearGradient id="tee" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2A2A30"/><stop offset="1" stop-color="#141417"/></linearGradient>
<radialGradient id="beardG" cx="0.5" cy="0.35" r="0.7"><stop offset="0" stop-color="#3A2B24"/><stop offset="1" stop-color="#1C1411"/></radialGradient>
<clipPath id="domo"><path d="M276 334 C262 150 638 150 624 334 Z"/></clipPath>
</defs>"""

_CORPO = """<g stroke="#15100E" stroke-width="7" stroke-linejoin="round" stroke-linecap="round">
<path d="M150 900 C150 760 220 700 330 676 L570 676 C680 700 750 760 750 900 Z" fill="url(#tee)"/>
<path d="M250 900 C255 820 270 780 290 760" fill="none" stroke="#3a3a42" stroke-width="5"/>
<path d="M650 900 C645 820 630 780 610 760" fill="none" stroke="#3a3a42" stroke-width="5"/>
<path d="M392 600 L392 684 C420 706 480 706 508 684 L508 600 Z" fill="#B0714D"/>
<path d="M366 680 C400 720 500 720 534 680" fill="none" stroke="#15100E" stroke-width="8"/>
<g transform="translate(450 742) rotate(-4)">
<path d="M-6 -12 L-6 10" stroke="#111" stroke-width="6"/>
<rect x="-62" y="2" width="56" height="40" rx="14" fill="#0E0E10"/>
<rect x="6" y="2" width="56" height="40" rx="14" fill="#0E0E10"/>
<path d="M-50 12 L-28 8" stroke="#FF6B1A" stroke-width="5"/><path d="M18 12 L40 8" stroke="#FF6B1A" stroke-width="5"/>
</g></g>"""

_CABECA = """<g stroke="#15100E" stroke-width="7" stroke-linejoin="round" stroke-linecap="round">
<path d="M272 420 C240 410 236 470 262 500 C274 512 290 508 294 500" fill="url(#skin)"/>
<path d="M628 420 C660 410 664 470 638 500 C626 512 610 508 606 500" fill="url(#skin)"/>
<path d="M288 330 C288 250 612 250 612 330 L612 470 C612 560 540 628 450 628 C360 628 288 560 288 470 Z" fill="url(#skin)"/>
<path d="M290 360 L290 470 L318 470 L318 360 Z" fill="#1C1411" stroke="none"/>
<path d="M610 360 L610 470 L582 470 L582 360 Z" fill="#1C1411" stroke="none"/>
<path d="M290 450 C292 520 320 600 380 640 C410 662 490 662 520 640 C580 600 608 520 610 450 C590 480 560 500 530 505 C510 520 390 520 370 505 C340 500 310 480 290 450 Z" fill="url(#beardG)"/>
<g transform="translate(450 548)">{boca}</g>
<path d="M372 520 C390 494 430 494 450 506 C470 494 510 494 528 520 C506 530 480 528 450 520 C420 528 394 530 372 520 Z" fill="#1C1411"/>
<path transform="translate(0 16)" d="M440 420 C436 450 420 470 426 482 C436 494 464 494 474 482 C480 470 464 450 460 420" fill="#C98763" stroke-width="6"/>
{olhos}
<g transform="translate(0 {y_sobr})" fill="#1C1411" stroke="none">
<path d="M334 372 C350 352 400 348 424 360 L420 374 C396 366 356 370 338 384 Z"/>
<path d="M566 372 C550 352 500 348 476 360 L480 374 C504 366 544 370 562 384 Z"/>
</g>
<path d="M292 330 C360 312 540 312 608 330 L608 372 C540 352 360 352 292 372 Z" fill="#000" opacity="0.18" stroke="none"/>
<path d="M276 334 C262 150 638 150 624 334 C560 316 340 316 276 334 Z" fill="url(#cap)"/>
<g clip-path="url(#domo)" fill="none" stroke="#C94C08" stroke-width="4">
<path d="M450 160 L450 330"/><path d="M372 180 C334 220 320 280 322 330"/><path d="M528 180 C566 220 580 280 578 330"/>
<path d="M300 270 C320 230 360 210 400 204" stroke="#FFB27A" stroke-width="8" opacity="0.55"/>
</g>
<circle cx="450" cy="196" r="11" fill="#F0600F"/>
<path d="M406 300 L406 236 L450 270 L494 236 L494 300" fill="none" stroke="#111" stroke-width="20" stroke-linejoin="miter" stroke-linecap="butt"/>
<path d="M262 334 C340 304 560 304 638 334 C652 362 600 384 450 384 C300 384 248 362 262 334 Z" fill="url(#brim)"/>
<path d="M290 344 C360 326 540 326 610 344" fill="none" stroke="#FF8A3D" stroke-width="5" opacity="0.7"/>
</g>"""


def _boca(a, sorriso):
    """a: 0 fechada .. 1 bem aberta."""
    w, h = 58 + 16 * a, 6 + 58 * a
    if a < 0.06:
        s = sorriso
        return (f'<path d="M{-w} -4 C{-w/2} {4+6*s} {w/2} {4+6*s} {w} -4 C{w*0.6} {22+4*s} {-w*0.6} {22+4*s} {-w} -4 Z" '
                f'fill="#B5605A" stroke="#15100E" stroke-width="6"/>')
    d = f"M{-w} 0 C{-w*0.6} -6 {w*0.6} -6 {w} 0 C{w*0.7} {h} {-w*0.7} {h} {-w} 0 Z"
    lingua = f'<ellipse cx="0" cy="{h*0.95}" rx="{w*0.55}" ry="{h*0.38}" fill="#C2525A"/>' if h > 18 else ""
    return (f'<clipPath id="cb"><path d="{d}"/></clipPath><path d="{d}" fill="#4A1414" stroke="none"/>'
            f'<g clip-path="url(#cb)" stroke="none"><rect x="{-w}" y="-10" width="{2*w}" height="{10+min(14, h*0.32)}" '
            f'fill="#F4F1EC"/>{lingua}</g><path d="{d}" fill="none" stroke="#15100E" stroke-width="6"/>')


def _olhos(f):
    """f: 0 aberto .. 1 fechado (a pálpebra fica sempre um pouco baixa, olhar relaxado)."""
    y = -30 + 54 * (0.22 + 0.78 * f)
    out = []
    for x in (378, 522):
        out.append(f'<g transform="translate({x} 434)"><ellipse rx="34" ry="24" fill="#FFF"/>'
                   f'<circle r="15" fill="#5A3A22"/><circle r="7" fill="#111" stroke="none"/>'
                   f'<circle cx="-5" cy="-6" r="4" fill="#fff" stroke="none"/>'
                   f'<path d="M-40 -32 L40 -32 L40 {y} C20 {y-10} -20 {y-10} -40 {y} Z" fill="#C98763" stroke="none"/>'
                   f'<path d="M-36 {y-2} C-16 {y-11} 16 {y-11} 36 {y-2}" fill="none" stroke="#15100E" stroke-width="5"/></g>')
    return "".join(out)


def _svg(corpo):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="900" viewBox="0 0 900 900">{_DEFS}{corpo}</svg>'


def _png(svg, lado):
    import cairosvg
    from io import BytesIO
    return Image.open(BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=lado, output_height=lado))).convert("RGBA")


class Ze:
    """Camadas do Zé já desenhadas, guardadas por pose (boca/olhos/sobrancelha arredondados)."""

    def __init__(self, lado=TAM):
        self.lado = lado
        self.corpo = _png(_svg(_CORPO), lado)
        self.cache = {}

    def cabeca(self, boca, piscar, sobr, sorriso):
        k = (round(boca * 10), round(piscar * 2), round(sobr * 4), round(sorriso))
        if k not in self.cache:
            b, p, s, r = k[0] / 10, k[1] / 2, k[2] / 4, k[3]
            self.cache[k] = _png(_svg(_CABECA.format(boca=_boca(b, 0.7 + 0.3 * r), olhos=_olhos(p), y_sobr=30 - s * 14)),
                                 self.lado)
        return self.cache[k]

    def quadro(self, pose):
        img = Image.new("RGBA", (self.lado, self.lado), (0, 0, 0, 0))
        img.alpha_composite(self.corpo, (0, int(pose["respira"])))
        cab = self.cabeca(pose["boca"], pose["piscar"], pose["sobr"], pose["sorriso"])
        esc = self.lado / 900
        cab = cab.rotate(pose["rot"], resample=Image.BICUBIC, center=(450 * esc, 640 * esc),
                         translate=(0, pose["dy"] * esc))
        img.alpha_composite(cab)
        return img


def _volume(voz_wav, n):
    """Volume da voz por quadro, de 0 a 1 (abre a boca rápido e fecha um pouco mais devagar)."""
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(voz_wav), "-af", "highpass=f=250,lowpass=f=3200",
                                   "-ac", "1", "-ar", "16000", "-f", "s16le", "-"])
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    spf = 16000 // FPS
    db = np.array([20 * np.log10(np.sqrt(np.mean(a[i * spf:(i + 1) * spf] ** 2) if len(a[i * spf:(i + 1) * spf]) else 0)
                                 + 1e-6) for i in range(n)])
    lo, hi = np.percentile(db, 25), np.percentile(db, 98)
    lv = np.clip((db - lo - 3) / max(1.0, hi - lo - 3), 0, 1)
    out, v = np.zeros(n), 0.0
    for i in range(n):
        v = lv[i] if lv[i] > v else v * 0.55 + lv[i] * 0.45
        out[i] = v
    return out


def poses(voz_wav, total, t_preco, t_cta, semente=7):
    n = int(total * FPS)
    vol = _volume(voz_wav, n)
    rnd = random.Random(semente)
    piscadas, t = {}, 0.8
    while t < total:  # piscada de 4 quadros, a cada 2–4 s
        f = int(t * FPS)
        for j, v in enumerate((0.5, 1.0, 1.0, 0.5)):
            piscadas[f + j] = v
        t += rnd.uniform(2.2, 4.0)
    out = []
    for i in range(n):
        t, b = i / FPS, float(vol[i])
        sobr = 0.35 * b + (0.9 * math.exp(-(t - t_preco) * 2.5) if t >= t_preco else 0)
        dy = -6 * b + 3 * math.sin(t * 2.0)
        if t_preco <= t < t_preco + 0.5:  # reação no preço: cabeça vai pra trás
            dy -= 10 * math.sin((t - t_preco) / 0.5 * math.pi)
        out.append({"boca": b, "piscar": piscadas.get(i, 0.0), "sobr": min(1.0, sobr),
                    "rot": 2.2 * math.sin(t * 1.3) + 3.0 * b * math.sin(t * 7.0), "dy": dy,
                    "respira": 2.5 * math.sin(t * 1.6), "sorriso": 1.0 if t >= t_cta else 0.0})
    return out


def _fundo():
    """Quase preto com o brilho laranja atrás do Zé, e o degradê que esconde a emenda com o Reels."""
    y, x = np.mgrid[0:H, 0:W]
    g = (np.clip(1 - np.sqrt((x - 540) ** 2 + ((y - 470) * 1.1) ** 2) / 520, 0, 1) ** 1.8 * 0.55)[..., None]
    img = np.array(FUNDO, float) * (1 - g) + np.array(LARANJA, float) * g
    fundo = Image.fromarray(img.astype(np.uint8)).convert("RGBA")
    dg = np.zeros((220, W, 4), np.uint8)
    dg[..., :3] = FUNDO
    dg[..., 3] = (255 * np.clip((np.arange(220) - 20) / 180, 0, 1) ** 1.4)[:, None]
    return fundo, Image.fromarray(dg, "RGBA")


def _duracao(arq):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", str(arq)]))


def aplicar(reel_mp4, voz_wav, tempos):
    """Troca reel_mp4 pela versão com o Zé. Devolve True se deu certo."""
    reel_mp4 = Path(reel_mp4)
    total = _duracao(reel_mp4)
    t_preco = next((p["ini"] for p in tempos if p["id"] == "preco"), 3.0)
    t_cta = next((p["ini"] for p in tempos if p["id"] == "cta"), total - 2.0)
    lista = poses(voz_wav, total, t_preco, t_cta)
    ze = Ze()
    fundo, degrade = _fundo()
    y0, alt = CORTE_REEL
    larg_reel = round(W * ALT_REEL / alt / 2) * 2
    x_reel = (W - larg_reel) // 2
    with tempfile.TemporaryDirectory() as tmp:
        saida = Path(tmp) / "reel.mp4"
        dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(reel_mp4), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                               stdout=subprocess.PIPE)
        enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                                "-r", str(FPS), "-i", "-", "-i", str(reel_mp4), "-map", "0:v", "-map", "1:a",
                                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "20",
                                "-c:a", "copy", "-shortest", "-movflags", "+faststart", str(saida)], stdin=subprocess.PIPE)
        i = 0
        while True:
            buf = dec.stdout.read(W * H * 3)
            if len(buf) < W * H * 3:
                break
            orig = Image.frombytes("RGB", (W, H), buf)
            img = fundo.copy()
            img.alpha_composite(ze.quadro(lista[min(i, len(lista) - 1)]), (X_ZE, Y_ZE))
            img.alpha_composite(degrade, (0, Y_CORTE - 180))
            baixo = orig.crop((0, y0, W, y0 + alt)).resize((larg_reel, ALT_REEL), Image.LANCZOS)
            img.paste(baixo, (x_reel, Y_REEL))
            enc.stdin.write(img.convert("RGB").tobytes())
            i += 1
        enc.stdin.close()
        dec.wait()
        if enc.wait() != 0 or i == 0:
            raise RuntimeError("ffmpeg falhou ao montar o Reels com o Zé")
        saida.replace(reel_mp4)
    return True
