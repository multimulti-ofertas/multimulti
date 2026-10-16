"""Produtos vindos da planilha "Obter Link em Massa" do painel de afiliados da Shopee.

Enquanto a Open API não é liberada, coloque as planilhas (.csv) baixadas do painel na pasta
`ofertas/` do repositório. O robô lê todas, separa por tema, tira repetidos e usa o link de
afiliado que já vem pronto na planilha.

As fotos ficam em `ofertas/imagens.json` ({"itemId": "url da foto"}). Se faltar a foto de um
produto, o robô tenta pegar na página da Shopee; se não conseguir, pula o produto.
"""
import csv
import difflib
import json
import re
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "ofertas"
IMAGENS = PASTA / "imagens.json"

# Palavras que colocam o produto num tema (sem acento, minúsculas).
TEMAS = {
    "cuidado": [
        "barbe", "barba", "cabelo", "aparador", "lamina", "navalha", "tonico", "shampoo",
        "perfume", "body splash", "pomada", "pasta modeladora", "depil", "pelos", "gola higienica",
        "gillette", "minoxi", "grecin", "oneblade", "kemei", "sobrancelha", "sabonete", "facial",
        "protetor solar", "hidratante", "desodorante",
    ],
    "carro": [
        "carro", "automotiv", "veicular", "porta malas", "volante", "farol", "pneu", "moto ", "motocicl", "12v",
    ],
    "ferramentas": [
        "ferramenta", "chave", "parafusadeira", "furadeira", "alicate", "trena", "lanterna",
        "multimetro", "catraca", "nivel a laser", "cola ", "esmerilhadeira", "lixadeira", "serra ", "soquete",
    ],
    "estilo": [
        "camiseta", "camisa", "relogio", "tenis", "carteira", "bermuda", "oculos", "mochila", "meia",
        "cueca", "bone", "cadarc", "jaqueta", "couro", "sapato", "limpa tenis",
    ],
}
# Produtos com estas palavras nunca entram.
FORA = ["feminin", "lente", "lentes de contato", "palmilha", "salto alto", "aquario", "pet ", "cachorro",
        "gato", "infantil", "crianca", "bebe", "cilio", "unha", "maquiagem", "perler", "artesanato",
        "bijuteria", "micanga", "croche", "trico", "boneca", "brinquedo", "rolo modelador", "polygel", "manicure", "esmalte", "penteado", "massinha", "slime", "massa de modelar"]


def sem_acento(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", t.lower()).strip()


def tema(nome):
    n = sem_acento(nome)
    if any(re.search(r"\b" + re.escape(w), n) for w in FORA):  # começo de palavra: "trico" não pega "elétrico"
        return None
    pontos = {c: sum(bool(re.search(r"\b" + re.escape(w), n)) for w in ws) for c, ws in TEMAS.items()}
    melhor = max(pontos, key=pontos.get)
    return melhor if pontos[melhor] else None


_RUIDO = re.compile(r"\b(kit|profissional|masculin[oa]s?|eletric[oa]|de|da|do|para|com|e|em|o|a)\b")


def chave_parecida(nome):
    """Texto simplificado para achar o mesmo produto vendido por lojas diferentes."""
    n = re.sub(r"[^a-z0-9 ]", " ", sem_acento(nome))
    return re.sub(r"\s+", " ", _RUIDO.sub(" ", n)).strip()[:70]


def parecido(a, b):
    """Mesmo produto (ou quase) com outro nome: texto parecido ou começo igual."""
    if difflib.SequenceMatcher(None, a, b).ratio() >= 0.72:
        return True
    pa, pb = a.split(), b.split()
    if pa[:2] == pb[:2] and len(pa) >= 2:  # ex.: "gola higienica...", "mini barbeador..."
        return True
    sa, sb = set(pa), set(pb)
    return len(sa & sb) / max(1, len(sa | sb)) >= 0.5


# Tipos de produto: no mesmo dia entra no máximo 1 de cada tipo (variedade).
TIPOS = ["nariz", "cadarc", "tonico", "gola higienica", "navalha", "lamina", "shampoo",
         "depil", "maquina", "aparador", "barbeador", "aparelho de barbear", "tenis", "compressor",
         "catraca", "soquete", "jogo de chave", "chave de fenda", "chaves de fenda", "precisao", "parafusadeira", "furadeira", "alicate", "trena", "lanterna",
         "camis", "relogio", "carteira", "perfume", "bone", "oculos", "mochila", "cueca", "bermuda", "meia", "par de meia", "pares de meia",
         "sabonete", "suporte", "aspirador", "carregador", "camera", "volante", "farol", "bolsa", "pochete"]


def tipo(nome):
    """Tipo = palavra de TIPOS que aparece PRIMEIRO no nome ("Tênis ... cadarço" é tênis;
    "Cadarço ... para tênis" é cadarço). "nariz" sempre ganha (aparador de nariz ≠ máquina de cabelo)."""
    n = sem_acento(nome)
    if re.search(r"\bnariz", n):
        return "nariz"
    achados = [(m.start(), i, t) for i, t in enumerate(TIPOS)
               for m in [re.search(r"\b" + re.escape(t), n)] if m]
    if not achados:
        return None
    t = min(achados)[2]
    return MESMO_TIPO.get(t, t)


MESMO_TIPO = {"soquete": "catraca", "jogo de chave": "catraca", "pochete": "bolsa", "mochila": "bolsa",
              "aparador": "maquina", "barbeador": "maquina",
              "chave de fenda": "chave de precisao", "chaves de fenda": "chave de precisao", "precisao": "chave de precisao"}


def _numero(txt):
    return float(re.sub(r"[^\d,\.]", "", txt or "0").replace(".", "").replace(",", ".") or 0)


def _vendas(txt):
    t = sem_acento(txt).replace("+", "")
    m = re.search(r"([\d\.,]+)\s*(mil|k)?", t)
    if not m:
        return 0
    v = float(m.group(1).replace(".", "").replace(",", "."))
    return int(v * 1000) if m.group(2) else int(v)


def carregar_imagens():
    if IMAGENS.exists():
        return json.loads(IMAGENS.read_text(encoding="utf-8"))
    return {}


def ler():
    """Lê todas as planilhas e devolve produtos no mesmo formato da API."""
    produtos = {}
    imagens = carregar_imagens()
    for arq in sorted(PASTA.glob("*.csv")):
        with open(arq, encoding="utf-8-sig", newline="") as f:
            for lin in csv.DictReader(f):
                iid = (lin.get("Item Id") or "").strip()
                nome = (lin.get("Item Name") or "").strip()
                if not iid or not nome or not lin.get("Offer Link"):
                    continue
                link_prod = (lin.get("Product Link") or "").strip()
                m = re.search(r"/product/(\d+)/(\d+)", link_prod)
                preco = _numero(lin.get("Price"))
                produtos[iid] = {
                    "itemId": iid,
                    "shopId": m.group(1) if m else "",
                    "productName": nome,
                    "imageUrl": imagens.get(iid),
                    "priceMin": str(preco),
                    "priceMax": str(preco),
                    "priceDiscountRate": 0,
                    "sales": _vendas(lin.get("Sales")),
                    "ratingStar": None,
                    "commissionRate": str(_numero(lin.get("Commission Rate")) / 100),
                    "offerLink": lin["Offer Link"].strip(),
                    "productLink": link_prod,
                    "shopName": (lin.get("Nome da loja") or "").strip(),
                    "fonte": "planilha",
                }
    return list(produtos.values())


def candidatos(cat_dia):
    """Produtos do tema do dia primeiro; os outros temas entram depois, se faltar."""
    do_tema, outros = [], []
    for p in ler():
        c = tema(p["productName"])
        if not c:
            continue
        if cat_dia == "top" or c == cat_dia:
            do_tema.append((c, p))
        else:
            outros.append((c, p))
    return do_tema, outros


def foto_da_pagina(p):
    """Tenta achar a foto principal na página do produto (pode falhar: a Shopee bloqueia robôs)."""
    import requests
    if not p.get("productLink"):
        return None
    try:
        r = requests.get(p["productLink"], timeout=20, headers={
            "User-Agent": "Mozilla/5.0 (compatible; facebookexternalhit/1.1)"})
        m = re.search(r'property="og:image"\s+content="([^"]+)"', r.text) or \
            re.search(r'content="([^"]+)"\s+property="og:image"', r.text)
        return m.group(1) if m else None
    except Exception:
        return None
