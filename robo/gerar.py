"""Gera as ofertas do dia: busca na Shopee, escolhe, cria artes/Reels/legendas e atualiza a vitrine.

Uso:
  python -m robo.gerar            # de verdade (precisa SHOPEE_APP_ID / SHOPEE_SECRET)
  python -m robo.gerar --demo     # teste com produtos de mentira, sem internet
"""
import argparse
import datetime as dt
import io
import json
import math
import os
import random
import shutil
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw

from . import config, texto
from .arte import feed, story
from .reel import reel

RAIZ = Path(__file__).resolve().parent.parent
DOCS = RAIZ / "docs"
MIDIA = DOCS / "media"
PRODUTOS = DOCS / "produtos.json"
FUSO = ZoneInfo("America/Cuiaba")


def hoje():
    return dt.datetime.now(FUSO).date()


def carregar():
    if PRODUTOS.exists():
        return json.loads(PRODUTOS.read_text(encoding="utf-8"))
    return []


def salvar(lista):
    PRODUTOS.write_text(json.dumps(lista, ensure_ascii=False, indent=1), encoding="utf-8")


def categoria_do_dia(d):
    return config.CALENDARIO[d.weekday()]


def palavras_do_dia(cat, rnd):
    if cat == "top":
        return [(c, rnd.choice(p)) for c, p in config.PALAVRAS.items()]
    return [(cat, w) for w in rnd.sample(config.PALAVRAS[cat], k=min(3, len(config.PALAVRAS[cat])))]


def pontuar(p):
    pct = float(p.get("priceDiscountRate") or 0)
    vendas = float(p.get("sales") or 0)
    nota = float(p.get("ratingStar") or 0)
    comissao = float(p.get("commissionRate") or 0)
    return pct + 10 * math.log10(vendas + 1) + (nota - 4.5) * 20 + comissao * 50


def passa_filtro(p):
    return (float(p.get("ratingStar") or 0) >= config.NOTA_MINIMA
            and int(p.get("sales") or 0) >= config.VENDAS_MINIMAS
            and float(p.get("priceDiscountRate") or 0) >= config.DESCONTO_MINIMO
            and p.get("imageUrl") and p.get("priceMin"))


def ja_usados(lista, d):
    limite = d - dt.timedelta(days=config.NAO_REPETIR_DIAS)
    return {str(x["itemId"]) for x in lista if dt.date.fromisoformat(x["data"]) >= limite}


def escolher(candidatos, usados, qtd):
    vistos, nomes, esc = set(), set(), []
    for cat, p in sorted(candidatos, key=lambda cp: pontuar(cp[1]), reverse=True):
        iid = str(p["itemId"])
        chave_nome = texto.titulo_curto(p["productName"])[:22].lower()
        if iid in usados or iid in vistos or chave_nome in nomes or not passa_filtro(p):
            continue
        vistos.add(iid)
        nomes.add(chave_nome)
        esc.append((cat, p))
        if len(esc) >= qtd:
            break
    return esc


# ---------- fontes de produtos ----------

def candidatos_shopee(cat_dia, rnd):
    from . import shopee
    out = []
    for cat, kw in palavras_do_dia(cat_dia, rnd):
        try:
            for p in shopee.buscar(kw, limite=40, ordem=2):
                out.append((cat, p))
        except Exception as e:
            print(f"[aviso] busca '{kw}' falhou: {e}")
    return out


def baixar_imagem(url, destino):
    if url.startswith("demo:"):
        _imagem_demo(url[5:], destino)
        return
    import requests
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    Image.open(io.BytesIO(r.content)).convert("RGB").save(destino)


def _imagem_demo(semente, destino):
    rnd = random.Random(semente)
    im = Image.new("RGB", (800, 800), "white")
    d = ImageDraw.Draw(im)
    cor = tuple(rnd.randint(30, 200) for _ in range(3))
    d.rounded_rectangle([170, 220, 630, 620], 60, fill=cor)
    d.ellipse([300, 120, 500, 320], fill=tuple(min(255, c + 50) for c in cor))
    im.save(destino)


def candidatos_demo(cat_dia, rnd):
    nomes = {
        "carro": ["Suporte Celular Veicular Magnético Para Painel", "Aspirador Automotivo Portátil 120W",
                  "Organizador Porta Malas Dobrável", "Câmera Veicular Full HD Wi-Fi"],
        "ferramentas": ["Jogo De Chaves Catraca 46 Peças", "Parafusadeira Furadeira 21V Com Maleta",
                        "Trena A Laser 40 Metros", "Lanterna Tática Recarregável LED"],
        "cuidado": ["Aparador De Pelos Masculino 3 Em 1", "Kit Barba Óleo Balm E Pente",
                    "Pomada Modeladora Efeito Matte 150g", "Máquina De Cortar Cabelo Sem Fio"],
        "estilo": ["Kit 3 Camisetas Básicas Masculinas Algodão", "Relógio Masculino Aço Inoxidável",
                   "Carteira Masculina Couro Slim", "Óculos De Sol Masculino Polarizado"],
    }
    cats = list(nomes) if cat_dia == "top" else [cat_dia]
    out, i = [], 0
    for c in cats:
        for nome in nomes[c]:
            i += 1
            preco = round(rnd.uniform(19, 189), 2)
            out.append((c, {
                "itemId": f"demo{c}{i}", "shopId": 1, "productName": "[DEMO] " + nome,
                "imageUrl": f"demo:{c}{i}", "priceMin": str(preco), "priceMax": str(preco),
                "priceDiscountRate": rnd.choice([12, 25, 38, 45, 52]), "sales": rnd.choice([350, 1200, 5400, 18000]),
                "ratingStar": rnd.choice([4.7, 4.8, 4.9]), "commissionRate": "0.1",
                "offerLink": "https://s.shopee.com.br/demo", "productLink": "https://shopee.com.br/",
            }))
    return out


# ---------- montagem ----------

def montar(cat, p, n, d, papel, demo):
    pasta = MIDIA / str(n)
    pasta.mkdir(parents=True, exist_ok=True)
    foto = pasta / "foto.jpg"
    baixar_imagem(p["imageUrl"], foto)

    link = p.get("offerLink")
    if not link and not demo:
        from . import shopee
        link = shopee.link_curto(p["productLink"])

    item = {
        "n": n, "data": d.isoformat(), "categoria": cat, "itemId": str(p["itemId"]),
        "nome": p["productName"], "titulo": texto.titulo_curto(p["productName"]),
        "link": link, "imagem": p["imageUrl"] if not demo else f"media/{n}/foto.jpg",
        "agenda": papel, "postado": None,
    }
    item.update(texto.dados_basicos(p))
    texto.com_ia(item)

    selo = f"{item['pct']}% OFF" if item["pct"] >= 15 else config.SELO.get(cat, "ACHADO").upper()
    extra = f"⭐ {item['nota']} · {item['vendidos']} vendidos"
    cfg = {
        "photo": str(foto), "category": config.SELO.get(cat, "Achado"), "badge": selo,
        "title": item["titulo"], "new": item["preco_curto"], "extra": extra.replace("⭐ ", "Nota "),
        "cta": ["LINK NA BIO", f"Nº {n}"], "hook": " · ".join(item["gancho"][:2]),
    }
    feed(cfg, str(pasta / "feed.jpg"))
    story(cfg, str(pasta / "story.png"))
    item["feed"] = f"media/{n}/feed.jpg"
    item["story"] = f"media/{n}/story.png"
    if papel == "reel":
        reel(dict(cfg, hook=item["gancho"], numero=n, extra=extra.replace("⭐ ", "NOTA ").upper()),
             str(pasta / "reel.mp4"))
        item["reel"] = f"media/{n}/reel.mp4"
    return item


def limpar_midia(lista, d):
    limite = d - dt.timedelta(days=config.GUARDAR_MIDIA_DIAS)
    for x in lista:
        if dt.date.fromisoformat(x["data"]) < limite:
            shutil.rmtree(MIDIA / str(x["n"]), ignore_errors=True)
            for k in ("feed", "story", "reel"):
                x.pop(k, None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--data", help="AAAA-MM-DD (padrão: hoje em Cuiabá)")
    args = ap.parse_args()

    if not args.demo and not os.environ.get("SHOPEE_APP_ID"):
        print("Shopee ainda não configurada (falta SHOPEE_APP_ID). Pulando hoje.")
        return
    d = dt.date.fromisoformat(args.data) if args.data else hoje()
    lista = carregar()
    if any(x["data"] == d.isoformat() for x in lista):
        print(f"Ofertas de {d} já foram geradas. Nada a fazer.")
        return

    rnd = random.Random(d.toordinal())
    cat = categoria_do_dia(d)
    print(f"Dia {d} → tema: {cat}")
    cands = candidatos_demo(cat, rnd) if args.demo else candidatos_shopee(cat, rnd)
    print(f"{len(cands)} candidatos encontrados")
    escolhidos = escolher(cands, ja_usados(lista, d), config.PRODUTOS_POR_DIA)
    if not escolhidos:
        raise SystemExit("Nenhum produto passou nos filtros hoje. Veja robo/config.py.")

    prox = max([x["n"] for x in lista], default=0) + 1
    papeis = ["feed", "reel"] + [None] * 10
    if len(escolhidos) == 1:
        papeis = ["feed"]
    novos = []
    for i, (c, p) in enumerate(escolhidos):
        item = montar(c, p, prox + i, d, papeis[i], args.demo)
        novos.append(item)
        print(f"  nº {item['n']}: {item['titulo']} ({item['preco']}, {item['pct']}% OFF) [{item['agenda'] or 'vitrine'}]")
    if len(escolhidos) == 1:  # só 1 produto: ele também vira Reels
        it = novos[0]
        pasta = MIDIA / str(it["n"])
        cfg = {"photo": str(pasta / "foto.jpg"), "hook": it["gancho"], "badge": f"{it['pct']}% OFF",
               "new": it["preco_curto"], "extra": f"NOTA {it['nota']} · {it['vendidos']} VENDIDOS", "numero": it["n"]}
        reel(cfg, str(pasta / "reel.mp4"))
        it["reel"] = f"media/{it['n']}/reel.mp4"

    lista = novos[::-1] + lista
    limpar_midia(lista, d)
    salvar(lista)
    print("Pronto. Vitrine atualizada.")


if __name__ == "__main__":
    main()
