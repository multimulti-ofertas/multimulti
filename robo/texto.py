"""Títulos, preços e legendas."""
import json
import os
import re

import requests

from . import config

_LIXO = re.compile(
    r"\b(promo(ção|cao)?|oferta|envio (imediato|rapido|rápido)|pronta entrega|frete gr[aá]tis|"
    r"lan[cç]amento|novo|nova|original|top|barato|imperd[ií]vel|\d+% off)\b",
    re.I,
)


def preco(valor):
    v = float(valor)
    s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return "R$ " + s


def vendidos(n):
    n = int(n or 0)
    if n >= 1000:
        k = n / 1000
        return f"+{k:.0f} mil" if k >= 10 else f"+{k:.1f} mil".replace(".", ",").replace(",0 mil", " mil")
    return f"+{n}"


def titulo_curto(nome, limite=60):
    t = re.sub(r"[\[\(【].*?[\]\)】]", " ", nome)
    t = _LIXO.sub(" ", t)
    t = re.sub(r"[|/*#!]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip(" -–,.")
    letras = [c for c in t if c.isalpha()]
    if letras and sum(c.isupper() for c in letras) / len(letras) > 0.6:
        t = t.lower().capitalize()
    if len(t) > limite:
        t = t[:limite].rsplit(" ", 1)[0]
    return t.strip(" -–,.")


def dados_basicos(p):
    pmin = float(p["priceMin"])
    pmax = float(p.get("priceMax") or pmin)
    pct = int(round(float(p.get("priceDiscountRate") or 0)))
    return {
        "preco": ("a partir de " if pmax > pmin * 1.02 else "") + preco(pmin),
        "preco_curto": preco(pmin),
        "pct": pct,
        "nota": round(float(p.get("ratingStar") or 0), 1),
        "vendidos": vendidos(p.get("sales")),
    }


def legenda_padrao(item):
    cat = item["categoria"]
    emoji = config.EMOJI.get(cat, "🔥")
    linhas = [f"{emoji} {item['titulo']}", ""]
    if item["pct"] >= 1:
        linhas.append(f"🔥 {item['pct']}% OFF → por {item['preco']}")
    else:
        linhas.append(f"💰 Por {item['preco']}")
    linhas.append(f"⭐ Nota {item['nota']} · {item['vendidos']} vendidos na Shopee")
    linhas += ["", f"🛒 Link na bio → produto nº {item['n']}", "",
               "Marca aquele amigo que precisa disso 👇", "",
               "Preço sujeito a alteração.", "",
               f"{config.HASHTAGS_FIXAS} {config.HASHTAGS.get(cat, '')}".strip()]
    return "\n".join(linhas)


def gancho_padrao(item):
    cat = config.SELO.get(item["categoria"], "ACHADINHO").upper()
    if item["pct"] >= 15:
        return [f"{item['pct']}% OFF", f"EM {cat}", f"POR {item['preco_curto']}?!"]
    return ["ACHADINHO", f"DE {cat}", f"POR {item['preco_curto']}?!"]


def com_ia(item):
    """Se houver ANTHROPIC_API_KEY, pede título, gancho e legenda melhores ao Claude.
    Sem a chave (ou se der erro), usa os textos padrão."""
    item["legenda"] = legenda_padrao(item)
    item["gancho"] = gancho_padrao(item)
    chave = os.environ.get("ANTHROPIC_API_KEY")
    if not chave:
        return item
    prompt = (
        "Você escreve posts do Instagram @multimulti.ofertas (achadinhos masculinos da Shopee, público "
        "brasileiro, tom direto e animado, sem exagero nem promessas falsas). Use SÓ os dados abaixo; "
        "não invente características, medidas ou preços.\n\n"
        f"Produto (nome na Shopee): {item['nome']}\n"
        f"Preço: {item['preco']} | Desconto: {item['pct']}% | Nota: {item['nota']} | Vendidos: {item['vendidos']}\n"
        f"Número na vitrine: {item['n']}\n\n"
        "Responda APENAS um JSON com as chaves:\n"
        '"titulo": nome curto e claro do produto (máx 55 caracteres),\n'
        '"gancho": lista de 3 linhas curtas em MAIÚSCULAS para abrir o Reels (máx 16 caracteres cada),\n'
        '"legenda": legenda completa com emoji no início, 1 frase de benefício, preço e % OFF, '
        f'a linha "🛒 Link na bio → produto nº {item["n"]}", um CTA de marcar amigo, '
        '"Preço sujeito a alteração." e no fim as hashtags: '
        f'{config.HASHTAGS_FIXAS} {config.HASHTAGS.get(item["categoria"], "")} + 1 hashtag do produto.'
    )
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": chave, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5-5"), "max_tokens": 800,
                  "messages": [{"role": "user", "content": prompt}]},
            timeout=60,
        )
        r.raise_for_status()
        txt = r.json()["content"][0]["text"]
        js = json.loads(txt[txt.find("{"): txt.rfind("}") + 1])
        if js.get("titulo"):
            item["titulo"] = js["titulo"][:60]
        if isinstance(js.get("gancho"), list) and js["gancho"]:
            item["gancho"] = [str(x)[:18] for x in js["gancho"][:3]]
        if js.get("legenda") and f"nº {item['n']}" in js["legenda"]:
            item["legenda"] = js["legenda"]
    except Exception as e:  # sem IA, segue com o padrão
        print(f"[aviso] IA indisponível, usando texto padrão: {e}")
    return item
