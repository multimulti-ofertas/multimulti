"""Publica no Instagram e na Página do Facebook o que está agendado para agora.

  python -m robo.postar --tipo auto    # rotina: olha a hora em Cuiabá e segue config.ROTINA
  python -m robo.postar --tipo feed    # um post do feed (2 por dia)
  python -m robo.postar --tipo reel    # um Reels (2 por dia)
  python -m robo.postar --tipo story   # um story; os produtos do dia vão se revezando
  python -m robo.postar --tipo auto --teste   # só mostra o que faria, sem postar
  python -m robo.postar --tipo feed --so-facebook   # só põe na Página o que já saiu no Instagram hoje

Facebook: espelha o Instagram. Feed e Reels que já saíram no Instagram hoje e ainda não estão na Página
são postados lá (assim ela se atualiza sozinha se ficar para trás). Story vai junto com o do Instagram.
Sem o secret FBPAGETOKEN, o Facebook é pulado com um aviso.
"""
import argparse
import datetime as dt
import time

from . import config, facebook, instagram
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
    """A rotina dispara às xx:50 para a hora seguinte, mas o GitHub costuma atrasar 20-60 min.
    +10 min: 19:50 (no horário) → 20h; 20:40 (50 min de atraso) → continua 20h."""
    from .gerar import FUSO
    agora = agora or dt.datetime.now(FUSO)
    return (agora + dt.timedelta(minutes=10)).hour


def atrasados(lista, d, h, tipos):
    """Feed/Reels de horários anteriores de hoje que não saíram (o GitHub às vezes pula uma execução)."""
    extra = []
    for tipo in ("feed", "reel"):
        if tipo in tipos:
            continue
        previstos = sum(1 for hh, ts in config.ROTINA.items() if hh <= h and tipo in ts)
        feitos = sum(1 for x in lista if x["data"] == d and ja_postado(x, tipo))
        if feitos < previstos and pendentes(lista, d, tipo):
            print(f"Recuperando {tipo} atrasado ({feitos} de {previstos} previstos até agora).")
            extra.append(tipo)
    return extra


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tipo", choices=["auto", "feed", "reel", "story"], required=True)
    ap.add_argument("--teste", action="store_true")
    ap.add_argument("--hora", type=int, help="só para teste: finge que é essa hora (0-23)")
    ap.add_argument("--so-facebook", action="store_true",
                    help="não posta no Instagram; só põe na Página o que já saiu no Instagram hoje")
    args = ap.parse_args()

    if not config.POSTAR_NO_INSTAGRAM and not args.teste:
        print("Postagem no Instagram desligada (config.POSTAR_NO_INSTAGRAM = False). Nada a fazer.")
        return

    if args.tipo == "auto":
        h = args.hora if args.hora is not None else hora_da_rotina()
        tipos = list(config.ROTINA.get(h, []))
        tipos = atrasados(carregar(), hoje().isoformat(), h, tipos) + tipos
        print(f"Rotina das {h:02d}h: {', '.join(tipos) or 'nada'}")
    else:
        tipos = [args.tipo]

    tentou = erros = 0
    fb_ok = facebook.configurado()
    if not fb_ok:
        print("::warning::Facebook pulado: falta o secret FBPAGETOKEN.")
    for tipo in tipos:
        lista = carregar()
        d = hoje().isoformat()
        feitos_agora = []
        alvos = [] if args.so_facebook else pendentes(lista, d, tipo)
        if not alvos and not args.so_facebook:
            print(f"Nada para postar no Instagram ({tipo}) agora.")
        for alvo in alvos:
            tentou += 1
            url = f"{config.PAGES_URL}/{alvo[tipo]}"
            print(f"[instagram] {tipo} do nº {alvo['n']}: {alvo['titulo']}\n{url}")
            if tipo != "story":
                print(f"---\n{alvo['legenda']}")
            if args.teste:
                feitos_agora.append(alvo)
                continue
            def publicar():
                if tipo == "feed":
                    return instagram.postar_imagem(url, alvo["legenda"])
                if tipo == "reel":
                    return instagram.postar_reels(url, alvo["legenda"])
                return instagram.postar_story(url)
            try:
                try:
                    mid = publicar()
                except Exception as e1:  # o Instagram às vezes "perde" a mídia; tenta de novo 1 vez
                    print(f"[aviso] instagram {tipo} do nº {alvo['n']}: {str(e1)[:200]} — tentando de novo em 30s")
                    time.sleep(30)
                    mid = publicar()
            except Exception as e:  # qualquer falha: registra e segue (o que já saiu fica marcado)
                print(f"[erro] instagram {tipo} do nº {alvo['n']}: {e}")
                print(f"::error::Instagram: {tipo} do nº {alvo['n']} falhou: {str(e)[:300]}")
                erros += 1
                continue
            agora = dt.datetime.utcnow().isoformat()
            alvo["postado"] = dict(alvo.get("postado") or {}, **{tipo: {"id": mid, "em": agora}})
            if tipo == "story":
                alvo["stories"] = int(alvo.get("stories") or 0) + 1
            salvar(lista)
            feitos_agora.append(alvo)
            print(f"Publicado no Instagram! id {mid}")

        # Página do Facebook: espelha o que saiu no Instagram
        if not fb_ok and not args.teste:
            continue
        chave = f"fb_{tipo}"
        if tipo == "story":
            fb_alvos = feitos_agora
        else:
            fb_alvos = [x for x in lista if x["data"] == d and not so_vitrine(x) and x.get(tipo)
                        and (ja_postado(x, tipo) or x in feitos_agora) and not ja_postado(x, chave)]
            fb_alvos.sort(key=lambda x: x["n"])
        for alvo in fb_alvos:
            tentou += 1
            url = f"{config.PAGES_URL}/{alvo[tipo]}"
            print(f"[facebook] {tipo} do nº {alvo['n']}: {alvo['titulo']}")
            if args.teste:
                if tipo != "story":
                    print(f"---\n{facebook.legenda(alvo['legenda'], alvo['n'])}")
                continue
            try:
                if tipo == "feed":
                    mid = facebook.postar_imagem(url, facebook.legenda(alvo["legenda"], alvo["n"]))
                elif tipo == "reel":
                    mid = facebook.postar_reels(url, facebook.legenda(alvo["legenda"], alvo["n"]))
                else:
                    mid = facebook.postar_story(url)
            except Exception as e:
                print(f"[erro] facebook {tipo} do nº {alvo['n']}: {e}")
                print(f"::error::Facebook: {tipo} do nº {alvo['n']} falhou: {str(e)[:300]}")
                erros += 1
                continue
            agora = dt.datetime.utcnow().isoformat()
            alvo["postado"] = dict(alvo.get("postado") or {}, **{chave: {"id": mid, "em": agora}})
            salvar(lista)
            print(f"Publicado no Facebook! id {mid}")
    if tentou and erros == tentou and not args.teste:
        raise SystemExit("Nenhuma publicação deu certo.")

if __name__ == "__main__":
    main()
