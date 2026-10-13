"""Publica no Instagram o que está agendado para agora.

  python -m robo.postar --tipo feed    # 12h: imagem do produto principal
  python -m robo.postar --tipo reel    # 18h e 21h: um Reels por vez (2 por dia)
  python -m robo.postar --tipo story   # 08h, 15h e 20h: stories dos produtos do dia
  python -m robo.postar --tipo story --teste   # só mostra o que faria, sem postar
"""
import argparse
import datetime as dt

from . import config, instagram
from .gerar import carregar, salvar, hoje


def ja_postado(x, tipo):
    return bool((x.get("postado") or {}).get(tipo))


def pendentes(lista, d, tipo):
    do_dia = sorted((x for x in lista if x["data"] == d), key=lambda x: x["n"])
    if tipo == "feed":
        return [x for x in do_dia if x.get("agenda") == "feed" and x.get("feed") and not ja_postado(x, "feed")][:1]
    if tipo == "reel":
        return [x for x in do_dia if x.get("reel") and not ja_postado(x, "reel")][:1]
    return [x for x in do_dia if x.get("story") and not ja_postado(x, "story")][:config.STORIES_POR_VEZ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tipo", choices=["feed", "reel", "story"], required=True)
    ap.add_argument("--teste", action="store_true")
    args = ap.parse_args()

    lista = carregar()
    alvos = pendentes(lista, hoje().isoformat(), args.tipo)
    if not alvos:
        print(f"Nada para postar ({args.tipo}) agora.")
        return

    erros = 0
    for alvo in alvos:
        url = f"{config.PAGES_URL}/{alvo[args.tipo]}"
        print(f"Postando {args.tipo} do nº {alvo['n']}: {alvo['titulo']}\n{url}")
        if args.tipo != "story":
            print(f"---\n{alvo['legenda']}")
        if args.teste:
            continue
        try:
            if args.tipo == "feed":
                mid = instagram.postar_imagem(url, alvo["legenda"])
            elif args.tipo == "reel":
                mid = instagram.postar_reels(url, alvo["legenda"])
            else:
                mid = instagram.postar_story(url)
        except instagram.InstagramErro as e:
            print(f"[erro] nº {alvo['n']}: {e}")
            erros += 1
            continue
        alvo["postado"] = dict(alvo.get("postado") or {}, **{args.tipo: {"id": mid, "em": dt.datetime.utcnow().isoformat()}})
        salvar(lista)
        print(f"Publicado! id {mid}")
    if erros == len(alvos) and not args.teste:
        raise SystemExit("Nenhuma publicação deu certo.")


if __name__ == "__main__":
    main()
