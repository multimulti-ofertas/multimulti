"""Vídeo "Top 3 achados da semana" (todo sábado): os 3 mais vendidos dos últimos 7 dias, com a música
baixa para o João gravar a narração por cima no Instagram. Também gera o roteiro e a legenda.

  python -m robo.top3                 # semana terminando hoje (Cuiabá)
  python -m robo.top3 --data 2026-10-17

Saída em docs/semana/: top3.mp4, semana.json (roteiro + legenda) e a página index.html mostra tudo
em https://multimulti-ofertas.github.io/multimulti/semana/
"""
import argparse
import datetime as dt
import json
import math
import re
import subprocess
from pathlib import Path

from PIL import Image

from . import musica, planilha
from .arte import (BRANCO, CINZA, FUNDO, GROSSA, LARANJA, LARANJA_CLARO, TEXTO, TEXTO_B, bloco, brilho,
                   circulo_numero, fit_layer, marca, preco_layer, produto, seta, text_layer, titulo_caps)
from .gerar import DOCS, carregar, hoje

W, H, FPS, M = 1080, 1920, 30, 72
USO = W - 2 * M
INTRO, CENA, FIM = 3.0, 6.5, 3.5
PASTA = DOCS / "semana"


def _vendas(txt):
    t = (txt or "").lower().replace(".", "").replace(",", ".")
    m = re.search(r"([\d.]+)\s*(mil)?", t)
    if not m:
        return 0
    return int(float(m.group(1)) * (1000 if m.group(2) else 1))


def escolher(lista, d):
    """Os 3 mais vendidos postados nos últimos 7 dias (1 de cada tipo, com foto ainda guardada)."""
    desde = d - dt.timedelta(days=6)
    cand = [x for x in lista if desde <= dt.date.fromisoformat(x["data"]) <= d and x.get("feed")
            and (DOCS / x["feed"].replace("feed.jpg", "foto.jpg")).exists()]
    cand.sort(key=lambda x: (_vendas(x.get("vendidos")), -x["n"]), reverse=True)
    esc, tipos = [], set()
    for x in cand:
        tp = planilha.tipo(x["nome"])
        if tp and tp in tipos:
            continue
        tipos.add(tp)
        esc.append(x)
        if len(esc) == 3:
            break
    return esc


def _ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def _entra(img, lay, x, y, t, sobe=50):
    a = _ease(t)
    if a <= 0.01:
        return
    if a < 1:
        lay = lay.copy()
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    img.alpha_composite(lay, (int(x), int(y + sobe * (1 - a))))


def video(itens, saida, som):
    total = INTRO + CENA * len(itens) + FIM
    fundo = Image.new("RGBA", (W, H), FUNDO + (255,))
    fundo.alpha_composite(brilho(W, H, W // 2, 860, 620, forca=0.7))
    fundo.alpha_composite(brilho(W, H, W // 2, 860, 260, LARANJA_CLARO, 0.3))
    mk = marca(52)
    i1 = fit_layer(f"TOP {len(itens)}", GROSSA, 330, LARANJA, USO)
    i2 = fit_layer("ACHADOS DA SEMANA", GROSSA, 140, BRANCO, USO)
    i3 = text_layer("que mais vendem na Shopee", TEXTO_B, 52, CINZA)
    cenas = []
    for pos, x in zip(range(len(itens), 0, -1), reversed(itens)):  # #3, #2, #1
        cenas.append(dict(
            pos=text_layer(f"#{pos}", GROSSA, 190, LARANJA),
            prod=produto(str(DOCS / x["feed"].replace("feed.jpg", "foto.jpg")), 800, 580),
            nome=bloco(titulo_caps(x["titulo"]), GROSSA, 96, BRANCO, USO, linhas=2),
            preco=preco_layer(x["preco_curto"], 210, LARANJA, USO - 260),
            vend=text_layer(f"{x['vendidos']} vendidos" if x.get("vendidos") else "", TEXTO, 46, CINZA),
            num=circulo_numero(x["n"], 210)))
    f1 = fit_layer("CURTIU ALGUM?", GROSSA, 150, BRANCO, USO)
    f2 = fit_layer("LINK NA BIO", GROSSA, 170, LARANJA, USO)
    f3 = bloco("Digita o número do produto na vitrine. Ou manda EU QUERO no direct.", TEXTO_B, 52, BRANCO, USO, linhas=3)
    arroba = text_layer("@multimulti.ofertas", TEXTO, 46, CINZA)
    st = seta(120)

    audio = ["-stream_loop", "-1", "-i", str(som)] if som else ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"]
    proc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", *audio, "-map", "0:v", "-map", "1:a", "-t", str(total),
         "-af", f"volume=0.35,afade=t=out:st={total - 1.5}:d=1.5",   # música baixa: a voz entra por cima
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "21",
         "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(saida)],
        stdin=subprocess.PIPE)
    for i in range(int(total * FPS)):
        t = i / FPS
        img = fundo.copy()
        img.alpha_composite(mk, ((W - mk.width) // 2, 290))
        if t < INTRO:
            _entra(img, i1, (W - i1.width) // 2, 640, t / 0.3 + 0.5, 80)
            _entra(img, i2, (W - i2.width) // 2, 640 + i1.height + 10, (t - 0.2) / 0.3)
            _entra(img, i3, (W - i3.width) // 2, 640 + i1.height + i2.height + 50, (t - 0.45) / 0.3)
        elif t < INTRO + CENA * len(cenas):
            k = int((t - INTRO) // CENA)
            c, lt = cenas[k], t - INTRO - k * CENA
            a, bob = _ease(lt / 0.5), 12 * math.sin(lt * 1.8)
            p = c["prod"]
            if a < 1:
                p = p.copy()
                p.putalpha(p.getchannel("A").point(lambda v: int(v * a)))
            img.alpha_composite(p, ((W - p.width) // 2, int(880 - p.height / 2 + 100 * (1 - a) + bob)))
            _entra(img, c["pos"], M - 6, 340, lt / 0.3, 0)
            y = 1200
            _entra(img, c["nome"], M - 3, y, (lt - 0.4) / 0.3)
            y2 = y + c["nome"].height + 20
            _entra(img, c["preco"], M - 6, y2, (lt - 0.8) / 0.3)
            _entra(img, c["vend"], M, y2 + c["preco"].height + 16, (lt - 1.1) / 0.3)
            _entra(img, c["num"], W - M - c["num"].width, y2 + 10, (lt - 1.2) / 0.3)
        else:
            lt = t - INTRO - CENA * len(cenas)
            _entra(img, f1, M - 4, 640, lt / 0.3)
            _entra(img, f2, M - 4, 640 + f1.height + 20, (lt - 0.2) / 0.3)
            _entra(img, st, M, 640 + f1.height + f2.height + 60, (lt - 0.35) / 0.3)
            _entra(img, f3, M, 640 + f1.height + f2.height + 230, (lt - 0.5) / 0.3)
            _entra(img, arroba, M, 640 + f1.height + f2.height + 230 + f3.height + 60, (lt - 0.7) / 0.3)
        proc.stdin.write(img.convert("RGB").tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg falhou ao gerar o Top 3")
    return total


def _reais(preco_curto):
    """"R$ 12,99" -> "12,99"."""
    return re.sub(r"^\s*R\$\s*", "", preco_curto or "")


def roteiro(itens):
    n = len(itens)
    linhas = [{"de": 0, "ate": INTRO, "tela": f"TOP {n} ACHADOS",
               "fala": f"Os {n} achados pra homem que mais tão vendendo na Shopee essa semana."}]
    t = INTRO
    for pos, x in zip(range(n, 0, -1), reversed(itens)):
        abre = "E o número 1" if pos == 1 else f"Número {pos}"
        vend = f" Mais de {x['vendidos'].lstrip('+')} vendidos." if x.get("vendidos") else ""
        linhas.append({"de": t, "ate": t + CENA, "tela": f"#{pos} {x['titulo']}",
                       "fala": f"{abre}: {x['titulo'].lower()}, por {_reais(x['preco_curto'])}.{vend}"})
        t += CENA
    linhas.append({"de": t, "ate": t + FIM, "tela": "LINK NA BIO",
                   "fala": "Curtiu algum? Link na bio, é só digitar o número."})
    return linhas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", help="AAAA-MM-DD (padrão: hoje em Cuiabá)")
    args = ap.parse_args()
    d = dt.date.fromisoformat(args.data) if args.data else hoje()
    itens = escolher(carregar(), d)
    if len(itens) < 3:
        raise SystemExit(f"Só {len(itens)} produto(s) com foto nos últimos 7 dias; preciso de 3.")
    PASTA.mkdir(parents=True, exist_ok=True)
    som = musica.escolher(d.isocalendar()[1])
    total = video(itens, PASTA / "top3.mp4", som)
    info = {
        "data": d.isoformat(),
        "duracao": round(total),
        "musica": som.stem if som else None,
        "produtos": [{"n": x["n"], "titulo": x["titulo"], "preco": x["preco_curto"], "vendidos": x.get("vendidos")} for x in itens],
        "roteiro": roteiro(itens),
        "legenda": (f"Top 3 achados da semana 🔥 Qual você levaria? Comenta o número 👇\n\n"
                    f"🛒 Link na bio → digita o nº do produto\n\n"
                    f"#achadosmasculinos #achadinhosshopee #shopee #achadinhos #multimulti #publi"),
    }
    (PASTA / "semana.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Top 3 de {d:%d/%m}: " + " · ".join(f"nº {x['n']} {x['titulo']}" for x in itens))


if __name__ == "__main__":
    main()
