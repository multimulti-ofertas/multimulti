"""Publica no Instagram o que está agendado para agora.

  python -m robo.postar --tipo auto    # rotina: olha a hora em Cuiabá e segue config.ROTINA
  python -m robo.postar --tipo feed    # um post do feed (2 por dia)
  python -m robo.postar --tipo reel    # um Reels (2 por dia)
  python -m robo.postar --tipo story   # um story; os produtos do dia vão se revezando
  python -m robo.postar --tipo auto --teste   # só mostra o que faria, sem postar
"""
import argparse
import datetime as dt

from . import config, instagram
from .gerar import carregar, salvar, hoje


def ja_postado(x, tipo):
    return bool((x.get("postado") or {}).get(tipo))


def so_vitrine(x):
    return any(isinstance(v, dict) and v.get("pulado") for v in (x.get("postado") or {}).values())


def pendentes(lista, d, tipo):
    do_dia = sorted((x for x in lista if x["data"] == d and not so_vitrine(x)), key=lambda x: x["n"])
    if tipo == "feed":
        return [x for x in do_dia if x.get("agenda") == "feed" and x.get("feed") and not ja_postado(x, "feed")][:1]
    if tipo == "reel":
        return [x for x in do_dia if x.get("reel") and not ja_postado(x, "reel")][:1]
    # stories: os produtos do dia se revezam (o que apareceu menos vezes vai primeiro)
    com_story = [x for x in do_dia if x.get("story")]
    com_story.sort(key=lambda x: (int(x.get("stories") or 0), x["n"]))
    return com_story[:config.STORIES_POR_VEZ]


def hora_da_rotina(agora=None):
    """A rotina dispara uns minutos antes da hora cheia; arredonda para a hora mais próxima."""
    from .gerar import FUSO
    agora = agora or dt.datetime.now(FUSO)
    return (agora + dt.timedelta(minutes=30)).hour


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tipo", choices=["auto", "feed", "reel", "story"], required=True)
    ap.add_argument("--teste", action="store_true")
    ap.add_argument("--hora", type=int, help="só para teste: finge que é essa hora (0-23)")
    args = ap.parse_args()

    if not config.POSTAR_NO_INSTAGRAM and not args.teste:
        print("Postagem no Instagram desligada (config.POSTAR_NO_INSTAGRAM = False). Nada a fazer.")
        return

    if args.tipo == "auto":
        h = args.hora if args.hora is not None else hora_da_rotina()
        tipos = config.ROTINA.get(h, [])
        print(f"Rotina das {h:02d}h: {', '.join(tipos) or 'nada'}")
    else:
        tipos = [args.tipo]

    tentou = erros = 0
    for tipo in tipos:
        lista = carregar()
        alvos = pendentes(lista, hoje().isoformat(), tipo)
        if not alvos:
            print(f"Nada para postar ({tipo}) agora.")
            continue
        for alvo in alvos:
            tentou += 1
            url = f"{config.PAGES_URL}/{alvo[tipo]}"
            print(f"Postando {tipo} do nº {alvo['n']}: {alvo['titulo']}\n{url}")
            if tipo != "story":
                print(f"---\n{alvo['legenda']}")
            if args.teste:
                continue
            try:
                if tipo == "feed":
                    mid = instagram.postar_imagem(url, alvo["legenda"])
                elif tipo == "reel":
                    mid = instagram.postar_reels(url, alvo["legenda"])
                else:
                    mid = instagram.postar_story(url)
            except Exception as e:  # qualquer falha: registra e segue (o que já saiu fica marcado)
                print(f"[erro] {tipo} do nº {alvo['n']}: {e}")
                print(f"::error::{tipo} do nº {alvo['n']} falhou: {str(e)[:300]}")
                erros += 1
                continue
            agora = dt.datetime.utcnow().isoformat()
            alvo["postado"] = dict(alvo.get("postado") or {}, **{tipo: {"id": mid, "em": agora}})
            if tipo == "story":
                alvo["stories"] = int(alvo.get("stories") or 0) + 1
            salvar(lista)
            print(f"Publicado! id {mid}")
    if tentou and erros == tentou and not args.teste:
        raise SystemExit("Nenhuma publicação deu certo.")


if __name__ == "__main__":
    main()
