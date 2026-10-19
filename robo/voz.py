"""Narração dos Reels com voz de IA (grátis, sem conta em nenhum site).

Motores (config.VOZ):
  "piper" → Piper TTS, roda dentro do GitHub (voz pt_BR-faber-medium, código aberto). Não depende de site nenhum.
  "edge"  → voz neural da Microsoft pelo pacote edge-tts (mais natural, mas é um serviço não oficial: pode parar).
  None    → Reels sem narração (só música).

  python -m robo.voz --teste 53 54     # gera Reels de teste com as duas vozes em docs/teste-voz/
"""
import argparse
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from . import config

PIPER_VOZ = "pt_BR-faber-medium"
EDGE_VOZ = "pt-BR-AntonioNeural"
PASTA_VOZES = Path(os.environ.get("PIPER_DIR", Path.home() / ".piper"))
MAX_SEG = 9.3  # o Reels tem 10 s; a voz tem que caber

_UNI = ["zero", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez", "onze", "doze",
        "treze", "catorze", "quinze", "dezesseis", "dezessete", "dezoito", "dezenove"]
_DEZ = ["", "", "vinte", "trinta", "quarenta", "cinquenta", "sessenta", "setenta", "oitenta", "noventa"]
_CEM = ["", "cento", "duzentos", "trezentos", "quatrocentos", "quinhentos", "seiscentos", "setecentos",
        "oitocentos", "novecentos"]


def extenso(n):
    """Número inteiro (0–999.999) por extenso em português: 59 → "cinquenta e nove"."""
    n = int(n)
    if n < 20:
        return _UNI[n]
    if n < 100:
        d, u = divmod(n, 10)
        return _DEZ[d] + (f" e {_UNI[u]}" if u else "")
    if n == 100:
        return "cem"
    if n < 1000:
        c, r = divmod(n, 100)
        return _CEM[c] + (f" e {extenso(r)}" if r else "")
    m, r = divmod(n, 1000)
    mil = "mil" if m == 1 else f"{extenso(m)} mil"
    if not r:
        return mil
    return f"{mil} e {extenso(r)}" if (r < 100 or r % 100 == 0) else f"{mil} {extenso(r)}"


def preco_falado(preco_curto):
    """"R$ 59,99" → "cinquenta e nove e noventa e nove"; "R$ 18,00" → "dezoito reais"."""
    m = re.search(r"([\d.]+),(\d{2})", preco_curto or "")
    if not m:
        return preco_curto or ""
    reais, cent = int(m.group(1).replace(".", "")), int(m.group(2))
    if not cent:
        return f"{extenso(reais)} {'real' if reais == 1 else 'reais'}"
    return f"{extenso(reais)} e {extenso(cent)}"


def texto(item, curto=False):
    """O que a voz fala (cabe em ~9 s)."""
    abre = (item.get("gancho") or ["Olha esse achado"])[0].rstrip("!.")
    if "%" in abre:  # "68% OFF nesse achado" → fala melhor como frase
        abre = "Olha esse achado"
    titulo = item.get("titulo") or ""
    fim = f"Link na bio, número {extenso(item['n'])}."
    if curto:
        return f"{titulo}, por {preco_falado(item.get('preco_curto'))}. {fim}"
    return f"{abre}! {titulo}, por {preco_falado(item.get('preco_curto'))}. {fim}"


def _duracao(arq):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(arq)],
                       capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def _piper(fala, saida):
    modelo = PASTA_VOZES / f"{PIPER_VOZ}.onnx"
    if not modelo.exists():
        import requests
        PASTA_VOZES.mkdir(parents=True, exist_ok=True)
        base = "https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR/faber/medium/" + PIPER_VOZ
        for ext in (".onnx", ".onnx.json"):
            r = requests.get(base + ext, timeout=120)
            r.raise_for_status()
            (PASTA_VOZES / f"{PIPER_VOZ}{ext}").write_bytes(r.content)
    subprocess.run(["python", "-m", "piper", "-m", str(modelo), "-f", str(saida), "--", fala], check=True)


def _edge(fala, saida):
    subprocess.run(["edge-tts", "--voice", EDGE_VOZ, "--rate=+8%", "--text", fala, "--write-media", str(saida)],
                   check=True)


def narrar(item, saida, motor=None):
    """Gera a narração em `saida` (.wav). Devolve o caminho, ou None se não der (o Reels sai só com música)."""
    motor = motor if motor is not None else config.VOZ
    if not motor:
        return None
    fazer = {"piper": _piper, "edge": _edge}[motor]
    saida = Path(saida)
    with tempfile.TemporaryDirectory() as tmp:
        for curto in (False, True):
            bruto = Path(tmp) / ("voz.mp3" if motor == "edge" else "voz.wav")
            try:
                fazer(texto(item, curto), bruto)
            except Exception as e:
                print(f"::warning::narração ({motor}) falhou no nº {item.get('n')}: {str(e)[:150]}")
                return None
            dur = _duracao(bruto)
            if dur <= MAX_SEG or curto:
                ritmo = min(1.25, max(1.0, dur / MAX_SEG))  # se ainda passar, acelera um pouco (até 25%)
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(bruto),
                                "-af", f"atempo={ritmo:.3f},loudnorm=I=-16:TP=-1.5", "-ar", "44100", "-ac", "2",
                                str(saida)], check=True)
                return saida
    return None


def main():
    """Teste: gera Reels de produtos já existentes com as duas vozes, para ouvir antes de ligar."""
    import json
    from .gerar import DOCS
    from .reel import reel
    ap = argparse.ArgumentParser()
    ap.add_argument("--teste", nargs="+", type=int, required=True, help="números dos produtos")
    args = ap.parse_args()
    lista = json.loads((DOCS / "produtos.json").read_text(encoding="utf-8"))
    pasta = DOCS / "teste-voz"
    shutil.rmtree(pasta, ignore_errors=True)
    pasta.mkdir(parents=True)
    for n in args.teste:
        it = next(x for x in lista if x["n"] == n)
        foto = DOCS / "media" / str(n) / "foto.jpg"
        cfg = {"photo": str(foto), "hook": it.get("gancho"), "title": it["titulo"], "new": it["preco_curto"],
               "extra": f"{it.get('vendidos')} vendidos", "numero": n}
        for motor in ("piper", "edge"):
            v = narrar(it, pasta / f"{n}-{motor}.wav", motor)
            print(f"nº {n} {motor}: {texto(it)!r} → {v} ({_duracao(v) if v else 0:.1f}s)")
            if v:
                reel(dict(cfg, voz=str(v)), str(pasta / f"reel-{n}-{motor}.mp4"))


if __name__ == "__main__":
    main()
