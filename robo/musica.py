"""Música dos Reels: trechos de 10s em robo/musicas/*.m4a (Coleção de Sons da Meta).

escolher(n) → caminho do trecho para o Reels nº n (vai alternando; dois Reels seguidos nunca repetem
quando há 2+ músicas). Sem nenhuma música na pasta, o Reels sai mudo como antes.
"""
from pathlib import Path

PASTA = Path(__file__).parent / "musicas"


def lista():
    return sorted(PASTA.glob("*.m4a"))


def escolher(n):
    ms = lista()
    if not ms:
        return None
    try:
        k = int(n)
    except (TypeError, ValueError):
        k = 0
    return ms[k % len(ms)]
