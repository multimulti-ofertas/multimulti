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

from . import config, facebook, instagram, texto
from .gerar import DOCS, carregar, salvar, hoje

PAUSA = DOCS / "pausa.json"   # se o Instagram bloquear, o robô para sozinho até a data gravada aqui


def em_pausa():
    import json
    if not PAUSA.exists():
        return None
    p = json.loads(PAUSA.read_text(encoding="utf-8"))
    return p if dt.datetime.utcnow().isoformat() < p.get("ate", "") else None


def pausar(horas, motivo):
    import json
    ate = (dt.datetime.utcnow() + dt.timedelta(hours=horas)).isoformat()
    PAUSA.write_text(json.dumps({"ate": ate, "motivo": motivo[:300]}, ensure_ascii=False), encoding="utf-8")
    print(f"::error::Instagram bloqueou ações: robô PAUSADO por {horas}h (até {ate} UTC). Motivo: {motivo[:200]}")


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
    # stories: cada produto do dia aparece UMA vez só (nunca repete; acabou, não posta mais story no dia)
    com_story = [x for x in do_dia if x.get("story") and not int(x.get("stories") or 0)]
    com_story.sort(key=lambda x: (int(x.get("stories") or 0), x["n"]))
    return com_story[:config.STORIES_POR_VEZ]


def hora_da_rotina(agora=None):
    """Hora atual em Cuiabá. O robô roda 4x por hora (xx:02, :17, :32, :47); o que é das 9h sai entre
    9h00 e 9h20 mesmo se o GitHub atrasar ou pular uma execução (plano() conta o que já saiu)."""
    from .gerar import FUSO
    agora = agora or dt.datetime.now(FUSO)
    return agora.hour


def rotina():
    return config.ROTINA_ANTIGA if hoje().isoformat() <= "2026-10-14" else config.ROTINA


def postou(x, tipo):
    """Saiu de verdade no Instagram (tem id). 'pulado' não conta."""
    v = (x.get("postado") or {}).get(tipo)
    return isinstance(v, dict) and bool(v.get("id"))


def plano(lista, d, h):
    """O que postar agora, pela CONTA do dia (não só pela hora): o GitHub atrasa ou pula execuções,
    e às vezes roda 2 vezes na mesma hora. Posta só o que falta até esta hora:
    feed/Reels 1 por vez; stories até 2 por vez (recupera hora perdida). Nunca passa do previsto."""
    tipos = []
    for tipo in ("feed", "reel", "story"):
        previstos = sum(1 for hh, ts in rotina().items() if hh <= h and tipo in ts)
        if tipo == "story":
            feitos = sum(int(x.get("stories") or 0) for x in lista if x["data"] == d)
        else:
            feitos = sum(1 for x in lista if x["data"] == d and postou(x, tipo))
        falta = previstos - feitos
        if falta > 0 and tipo != "story" and feitos < previstos - 1:
            print(f"Recuperando {tipo} atrasado ({feitos} de {previstos} previstos até agora).")
        tipos += [tipo] * max(0, min(falta, 2 if tipo == "story" else 1))
    return tipos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tipo", choices=["auto", "feed", "reel", "story"], required=True)
    ap.add_argument("--teste", action="store_true")
    ap.add_argument("--so-testar", action="store_true",
                    help="faz o teste antes de postar (perfil, limite, arquivo, legenda) e NÃO posta nada")
    ap.add_argument("--hora", type=int, help="só para teste: finge que é essa hora (0-23)")
    ap.add_argument("--so-facebook", action="store_true",
                    help="não posta no Instagram; só põe na Página o que já saiu no Instagram hoje")
    args = ap.parse_args()

    if args.so_testar:
        return so_testar(args)
    if not config.POSTAR_NO_INSTAGRAM and not args.teste:
        print("Postagem no Instagram desligada (config.POSTAR_NO_INSTAGRAM = False). Nada a fazer.")
        return
    if em_pausa() and not args.teste:
        print(f"::warning::Robô em pausa (Instagram bloqueou): {em_pausa()}")
        return

    if args.tipo == "auto":
        h = args.hora if args.hora is not None else hora_da_rotina()
        tipos = plano(carregar(), hoje().isoformat(), h)
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
                print(f"---\n{texto.com_publi(alvo['legenda'])}")
            if args.teste:
                feitos_agora.append(alvo)
                continue
            def publicar():
                if tipo == "feed":
                    return instagram.postar_imagem(url, texto.com_publi(alvo["legenda"]))
                if tipo == "reel":
                    return instagram.postar_reels(url, texto.com_publi(alvo["legenda"]))
                return instagram.postar_story(url)
            # feed/Reels: se já está no perfil (publicou mas deu erro antes), só registra — NUNCA posta de novo
            legenda = texto.com_publi(alvo["legenda"]) if tipo != "story" else None
            try:  # TESTE antes de postar (pedido do João): na dúvida, não posta
                ok, motivo, mid = instagram.checar_antes(tipo, alvo["n"], url, legenda)
            except Exception as e:
                print(f"::error::Teste antes do {tipo} do nº {alvo['n']} falhou (não postei): {str(e)[:200]}")
                erros += 1
                if instagram.bloqueado(e):
                    pausar(24, str(e))
                    raise SystemExit("Instagram bloqueou: robô pausado por 24h.")
                continue
            if mid:
                print(f"::warning::{tipo} do nº {alvo['n']} já estava no perfil (id {mid}); só registrei, não repostei.")
            elif not ok:
                print(f"::warning::Não postei o {tipo} do nº {alvo['n']}: {motivo}. Tenta de novo na próxima rodada.")
                continue
            else:
                try:
                    mid = publicar()
                except Exception as e:
                    print(f"[erro] instagram {tipo} do nº {alvo['n']}: {e}")
                    if tipo != "story":  # às vezes o Instagram publica e mesmo assim devolve erro
                        time.sleep(20)
                        try:
                            mid = instagram.ja_no_ar(alvo["n"])
                        except Exception:
                            mid = None
                    if not mid:
                        print(f"::error::Instagram: {tipo} do nº {alvo['n']} falhou: {str(e)[:300]}")
                        erros += 1
                        if instagram.bloqueado(e):
                            pausar(24, str(e))
                            salvar(lista)
                            raise SystemExit("Instagram bloqueou: robô pausado por 24h.")
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
                    print(f"---\n{facebook.legenda(texto.com_publi(alvo['legenda']), alvo['n'])}")
                continue
            try:
                if tipo == "feed":
                    mid = facebook.postar_imagem(url, facebook.legenda(texto.com_publi(alvo["legenda"]), alvo["n"]))
                elif tipo == "reel":
                    mid = facebook.postar_reels(url, facebook.legenda(texto.com_publi(alvo["legenda"]), alvo["n"]))
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

def so_testar(args):
    """Roda o teste de antes de postar para o que sairia agora, sem publicar nada."""
    lista, d = carregar(), hoje().isoformat()
    h = args.hora if args.hora is not None else hora_da_rotina()
    tipos = plano(lista, d, h) if args.tipo == "auto" else [args.tipo]
    print(f"::notice::Teste ({h:02d}h): sairia {', '.join(tipos) or 'nada'}. Postagem ligada: {config.POSTAR_NO_INSTAGRAM}. Pausa: {em_pausa()}")
    vistos = set()
    for tipo in tipos:
        for alvo in pendentes(lista, d, tipo):
            if (tipo, alvo["n"]) in vistos:
                continue
            vistos.add((tipo, alvo["n"]))
            url = f"{config.PAGES_URL}/{alvo[tipo]}"
            leg = texto.com_publi(alvo["legenda"]) if tipo != "story" else None
            try:
                ok, motivo, mid = instagram.checar_antes(tipo, alvo["n"], url, leg)
                print(f"::notice::{tipo} nº {alvo['n']} ({alvo['titulo']}): {'PODE POSTAR' if ok else 'NÃO POSTA'} — {motivo}{f' (id {mid})' if mid else ''}")
            except Exception as e:
                print(f"::error::{tipo} nº {alvo['n']}: teste falhou — {str(e)[:250]}")


if __name__ == "__main__":
    main()
