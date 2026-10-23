"""Cliente da Shopee Affiliate Open API (Brasil).

Precisa das variáveis SHOPEE_APP_ID e SHOPEE_SECRET (pegue no painel de afiliados → Open API).
Documentação: https://affiliate.shopee.com.br/open_api
"""
import hashlib
import json
import os
import time

import requests

ENDPOINT = os.environ.get("SHOPEE_ENDPOINT", "https://open-api.affiliate.shopee.com.br/graphql")

# sortType: 1 relevância, 2 mais vendidos, 3 maior preço, 4 menor preço, 5 maior comissão
CAMPOS = """
  itemId shopId productName imageUrl priceMin priceMax priceDiscountRate
  sales ratingStar commissionRate offerLink productLink shopName
"""


class ShopeeErro(RuntimeError):
    pass


def _chamar(query, variables=None):
    app_id = os.environ.get("SHOPEE_APP_ID")
    secret = os.environ.get("SHOPEE_SECRET")
    if not app_id or not secret:
        raise ShopeeErro("Faltam SHOPEE_APP_ID / SHOPEE_SECRET nos Secrets do GitHub.")
    payload = json.dumps({"query": query, "variables": variables or {}}, separators=(",", ":"))
    ts = str(int(time.time()))
    assinatura = hashlib.sha256((app_id + ts + payload + secret).encode()).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"SHA256 Credential={app_id}, Timestamp={ts}, Signature={assinatura}",
    }
    r = requests.post(ENDPOINT, data=payload, headers=headers, timeout=30)
    r.raise_for_status()
    dados = r.json()
    if dados.get("errors"):
        raise ShopeeErro(f"Shopee respondeu erro: {dados['errors']}")
    return dados["data"]


def buscar(palavra, limite=30, ordem=2, pagina=1):
    q = f"""query($kw:String,$sort:Int,$page:Int,$limit:Int){{
      productOfferV2(keyword:$kw, sortType:$sort, page:$page, limit:$limit){{
        nodes{{ {CAMPOS} }}
        pageInfo{{ page limit hasNextPage }}
      }}
    }}"""
    d = _chamar(q, {"kw": palavra, "sort": ordem, "page": pagina, "limit": limite})
    return d["productOfferV2"]["nodes"] or []


def link_curto(url_produto, sub_ids=None):
    q = """mutation($url:String!,$subs:[String]){
      generateShortLink(input:{originUrl:$url, subIds:$subs}){ shortLink }
    }"""
    d = _chamar(q, {"url": url_produto, "subs": sub_ids or ["instagram"]})
    return d["generateShortLink"]["shortLink"]


CANAIS = ("ig", "fb", "web")  # de onde a pessoa abriu a vitrine: Instagram, Facebook ou navegador comum


def links_por_canal(url_produto, n):
    """Um link curto por canal, marcado com o canal e o nº do produto (subIds).
    O relatório da Shopee devolve essas marcas, e assim dá pra saber o que vendeu e por onde."""
    return {c: link_curto(url_produto, [c, f"n{n}"]) for c in CANAIS}
