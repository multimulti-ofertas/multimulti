"""Teste: quais campos a API de afiliados da Shopee oferece (tem vídeo?) e se a página do produto entrega vídeo."""
import json
import requests
from . import shopee

q = """{ __type(name: "ProductOfferV2") { fields { name } } }"""
try:
    d = shopee._chamar(q)
    campos = [f["name"] for f in d["__type"]["fields"]]
    print("::notice::Campos da API:", ", ".join(campos))
    print("::notice::Tem vídeo na API:", any("video" in c.lower() for c in campos))
except Exception as e:
    print("::warning::introspecção falhou:", str(e)[:300])

try:
    p = shopee.buscar("compressor de ar portatil", limite=1)[0]
    url = f"https://shopee.com.br/api/v4/pdp/get_pc?item_id={p['itemId']}&shop_id={p['shopId']}"
    r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://shopee.com.br/"})
    print(f"::notice::Página do produto (api web): HTTP {r.status_code}, tem 'video' no corpo: {'video' in r.text.lower()}, {r.text[:150]!r}")
except Exception as e:
    print("::warning::página falhou:", str(e)[:300])
