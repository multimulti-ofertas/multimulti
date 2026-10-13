"""Publica no Instagram o post agendado de hoje.

  python -m robo.postar --tipo feed    # 12h: imagem do produto principal
  python -m robo.postar --tipo reel    # 19h: Reels do segundo produto
  python -m robo.postar --tipo reel --teste   # só mostra o que faria, sem postar
"""
import argparse
import datetime as dt

from . import config, instagram
from .gerar import carregar, salvar, hoje


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tipo", choices=["feed", "reel"], required=True)
    ap.add_argument("--teste", action="store_true")
    args = ap.parse_args()

    d = hoje().isoformat()
    lista = carregar()
    alvo = None
    for x in lista:
        if x["data"] != d:
            continue
        if args.tipo == "reel" and x.get("reel") and not (x.get("postado") or {}).get("reel"):
            alvo = x
            break
        if args.tipo == "feed" and x.get("agenda") == "feed" and not (x.get("postado") or {}).get("feed"):
            alvo = x
            break
    if not alvo:
        print(f"Nada para postar ({args.tipo}) hoje.")
        return

    url = f"{config.PAGES_URL}/{alvo[args.tipo]}"
    print(f"Postando {args.tipo} do nº {alvo['n']}: {alvo['titulo']}\n{url}\n---\n{alvo['legenda']}")
    if args.teste:
        return
    if args.tipo == "feed":
        mid = instagram.postar_imagem(url, alvo["legenda"])
    else:
        mid = instagram.postar_reels(url, alvo["legenda"])
    alvo.setdefault("postado", {})
    alvo["postado"] = dict(alvo["postado"] or {}, **{args.tipo: {"id": mid, "em": dt.datetime.utcnow().isoformat()}})
    salvar(lista)
    print(f"Publicado! id {mid}")


if __name__ == "__main__":
    main()
