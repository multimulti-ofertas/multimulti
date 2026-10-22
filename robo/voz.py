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


# ---------- roteiro em partes (Reels v2: legenda animada sincronizada) ----------

GANCHOS = {
    "carro": ["Todo dono de carro precisa disso", "Olha o que eu achei pro seu carro", "Seu carro merece esse achado"],
    "ferramentas": ["Quem curte ferramenta vai querer", "Esse achado resolve na hora", "Ferramenta boa e barata existe"],
    "cuidado": ["Achado pra quem se cuida", "Homem que se cuida vai gostar", "Olha esse achado de cuidado"],
    "estilo": ["Achado de estilo baratinho", "Estilo gastando pouco", "Olha esse achado de estilo"],
}


def _valor(preco_curto):
    m = re.search(r"([\d.]+),(\d{2})", preco_curto or "")
    return float(m.group(1).replace(".", "") + "." + m.group(2)) if m else 0.0


def gancho(item):
    v, n = _valor(item.get("preco_curto")), int(item.get("n") or 0)
    if 0 < v < 50 and n % 2 == 0:  # metade dos Reels baratos abre pelo preço
        teto = int(v // 10 + 1) * 10
        return f"Menos de {extenso(teto)} reais nisso aqui?", f"Menos de R$ {teto} nisso aqui?"
    lista = GANCHOS.get(item.get("categoria"), ["Olha esse achado"])
    g = lista[n % len(lista)]
    return g + "!", g + "!"


def _vendas_falado(txt):
    """"+1,3 mil" → "mais de mil e trezentos"; "+914" → "mais de novecentos"."""
    t = (txt or "").replace("+", "").strip().lower()
    m = re.match(r"([\d.,]+)\s*(mil)?", t)
    if not m:
        return None
    num = float(m.group(1).replace(".", "").replace(",", "."))
    num = int(num * 1000) if m.group(2) else int(num)
    if num < 100:
        return None
    redondo = (num // 1000) * 1000 if num >= 1000 else (num // 100) * 100
    if num >= 1000 and num % 1000 >= 100 and num < 10000:
        redondo = (num // 100) * 100
    return f"mais de {extenso(redondo)}"


def partes(item):
    """Lista de (id, fala, legenda) na ordem do vídeo."""
    g_fala, g_tela = gancho(item)
    out = [("gancho", g_fala, g_tela),
           ("nome", item.get("titulo") or "", item.get("titulo") or ""),
           ("preco", f"Por {preco_falado(item.get('preco_curto'))}.", f"Por {item.get('preco_curto')}")]
    vf = _vendas_falado(item.get("vendidos"))
    if vf:
        fala = f"{vf.capitalize()} vendidos"
        tela = f"{item.get('vendidos')} vendidos"
        if item.get("nota"):
            a, b = str(item["nota"]).split(".") if "." in str(item["nota"]) else (str(item["nota"]), "0")
            fala += f", nota {extenso(int(a))}{' vírgula ' + extenso(int(b)) if int(b) else ''}"
            tela += f" · nota {str(item['nota']).replace('.', ',')}"
        out.append(("prova", fala + ".", tela))
    out.append(("cta", f"Link na bio, número {extenso(item['n'])}.", f"Link na bio · nº {item['n']}"))
    return out


def _tts(fala, saida):
    subprocess.run(["edge-tts", "--voice", EDGE_VOZ, "--rate=+10%", "--text", fala, "--write-media", str(saida)],
                   check=True, capture_output=True)


def roteiro(item, saida, max_seg=13.5, pausa=0.12, atraso=0.25):
    """Gera a narração em partes e devolve (wav, [{"id","tela","ini","fim"}]) com os tempos de cada parte
    no vídeo. Se passar de max_seg, tira a "prova" (vendas/nota). Falha → (None, [])."""
    if config.VOZ != "edge":
        return None, []
    saida = Path(saida)
    with tempfile.TemporaryDirectory() as tmp:
        try:
            lst = partes(item)
            arqs = []
            for i, (pid, fala, tela) in enumerate(lst):
                a = Path(tmp) / f"{i}.mp3"
                _tts(fala, a)
                arqs.append((pid, tela, a, _duracao(a)))
            if sum(d for *_, d in arqs) + pausa * len(arqs) > max_seg:
                arqs = [x for x in arqs if x[0] != "prova"]
            tempos, t = [], atraso
            entradas, filtros = [], []
            for i, (pid, tela, a, d) in enumerate(arqs):
                tempos.append({"id": pid, "tela": tela, "ini": round(t, 3), "fim": round(t + d, 3)})
                entradas += ["-i", str(a)]
                filtros.append(f"[{i}:a]aresample=44100,apad=pad_dur={pausa}[s{i}]")
                t += d + pausa
            cadeia = ";".join(filtros) + ";" + "".join(f"[s{i}]" for i in range(len(arqs))) + \
                f"concat=n={len(arqs)}:v=0:a=1,adelay={int(atraso*1000)}|{int(atraso*1000)},loudnorm=I=-16:TP=-1.5[a]"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *entradas, "-filter_complex", cadeia,
                            "-map", "[a]", "-ar", "44100", "-ac", "2", str(saida)], check=True)
            return saida, tempos
        except Exception as e:
            print(f"::warning::narração falhou no nº {item.get('n')}: {str(e)[:200]}")
            return None, []


def main():
    """Teste: gera Reels v2 (voz + legenda) de produtos já existentes em docs/teste-voz/, para ver antes de ligar."""
    import json
    from .gerar import DOCS
    from .reel2 import reel_narrado
    ap = argparse.ArgumentParser()
    ap.add_argument("--teste", nargs="+", type=int, required=True, help="números dos produtos")
    args = ap.parse_args()
    lista = json.loads((DOCS / "produtos.json").read_text(encoding="utf-8"))
    pasta = DOCS / "teste-voz"
    shutil.rmtree(pasta, ignore_errors=True)
    pasta.mkdir(parents=True)
    for n in args.teste:
        it = next(x for x in lista if x["n"] == n)
        v, tempos = roteiro(it, pasta / f"{n}.wav")
        print(f"nº {n}: {tempos}")
        if v:
            cfg = {"photo": str(DOCS / "media" / str(n) / "foto.jpg"), "numero": n, "new": it["preco_curto"]}
            reel_narrado(cfg, str(pasta / f"reel-{n}.mp4"), v, tempos)
            if config.PERSONAGEM:
                from .personagem import aplicar
                aplicar(pasta / f"reel-{n}.mp4", v, tempos)
            v.unlink()


if __name__ == "__main__":
    main()
