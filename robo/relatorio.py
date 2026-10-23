"""Relatório de vendas: puxa as comissões da Shopee e salva TRANCADO com senha em docs/relatorio.json.

O repositório e a vitrine são públicos, então o arquivo vai criptografado (AES-GCM, chave tirada da
senha do secret RELATORIO_SENHA). Só abre em docs/painel.html, com a senha.

Os links novos levam duas marcas (subIds): o canal (ig, fb, web) e o nº do produto (n109).
Venda de link antigo, sem marca, entra como "sem marca" e é ligada ao produto pelo itemId.

Uso:
  python -m robo.relatorio           # puxa os últimos 30 dias e salva
  python -m robo.relatorio --testar  # só confere se a Shopee responde (mostra quantidades, nada de valor)
"""
import argparse
import base64
import datetime as dt
import json
import os
import time
from pathlib import Path
from zoneinfo import ZoneInfo

from . import shopee

RAIZ = Path(__file__).resolve().parent.parent
PRODUTOS = RAIZ / "docs" / "produtos.json"
SAIDA = RAIZ / "docs" / "relatorio.json"
FUSO = ZoneInfo("America/Cuiaba")
DIAS = 30
CANAIS = {"ig": "Instagram", "fb": "Facebook", "web": "Navegador", "": "Sem marca"}
CANCELADO = ("cancel", "unpaid", "invalid", "fail")

CONSULTA = """query($ini:Int64,$fim:Int64,$scroll:String){
  conversionReport(purchaseTimeStart:$ini, purchaseTimeEnd:$fim, limit:500, scrollId:$scroll){
    nodes{
      purchaseTime utmContent
      orders{ orderId orderStatus items{ itemId itemName qty actualAmount itemTotalCommission displayItemStatus } }
    }
    pageInfo{ hasNextPage scrollId }
  }
}"""


def conversoes(ini, fim):
    """Todas as conversões entre ini e fim (datetime). A Shopee pagina com scrollId."""
    out, scroll = [], None
    while True:
        d = shopee._chamar(CONSULTA, {"ini": int(ini.timestamp()), "fim": int(fim.timestamp()), "scroll": scroll})
        r = d["conversionReport"]
        out += r.get("nodes") or []
        info = r.get("pageInfo") or {}
        if not info.get("hasNextPage") or not info.get("scrollId"):
            return out
        scroll = info["scrollId"]
        time.sleep(1)


def _num(v):
    try:
        return float(v or 0)
    except (TypeError, ValueError):
        return 0.0


def marcas(utm):
    """utmContent vem como 'ig-n109---' (subId1-subId2-...). Devolve (canal, nº ou None)."""
    partes = (utm or "").split("-")
    canal = partes[0] if partes and partes[0] in CANAIS else ""
    n = next((int(p[1:]) for p in partes if p[:1] == "n" and p[1:].isdigit()), None)
    return canal, n


def montar(nodes, produtos):
    por_n = {x["n"]: x for x in produtos}
    por_item = {str(x["itemId"]): x for x in produtos}
    tot = {"pedidos": 0, "itens": 0, "vendido": 0.0, "comissao": 0.0, "cancelados": 0}
    canal_t, dia_t, papel_t, prod_t = {}, {}, {}, {}

    def soma(tab, chave, it):
        t = tab.setdefault(chave, {"itens": 0, "vendido": 0.0, "comissao": 0.0})
        t["itens"] += it[0]
        t["vendido"] += it[1]
        t["comissao"] += it[2]

    for c in nodes:
        canal, n = marcas(c.get("utmContent"))
        quando = dt.datetime.fromtimestamp(int(c.get("purchaseTime") or 0), FUSO).date().isoformat()
        for o in c.get("orders") or []:
            tot["pedidos"] += 1
            for i in o.get("items") or []:
                status = (i.get("displayItemStatus") or o.get("orderStatus") or "").lower()
                if any(s in status for s in CANCELADO):
                    tot["cancelados"] += 1
                    continue
                it = (int(_num(i.get("qty")) or 1), _num(i.get("actualAmount")), _num(i.get("itemTotalCommission")))
                tot["itens"] += it[0]
                tot["vendido"] += it[1]
                tot["comissao"] += it[2]
                # produto do post: pela marca nº; senão pelo itemId (link antigo, ou comprou outra coisa na loja)
                p = por_n.get(n) or por_item.get(str(i.get("itemId")))
                papel = (p.get("agenda") or "story") if p else "outro produto"
                soma(canal_t, CANAIS[canal], it)
                soma(dia_t, quando, it)
                soma(papel_t, {"feed": "Feed", "reel": "Reels", "story": "Só story"}.get(papel, "Outro produto"), it)
                chave = f"nº {p['n']} · {p['titulo']}" if p else (i.get("itemName") or "?")[:40]
                soma(prod_t, chave, it)

    def lista(tab, ordem="comissao"):
        return sorted(({"nome": k, **{a: round(b, 2) for a, b in v.items()}} for k, v in tab.items()),
                      key=lambda x: x[ordem], reverse=True)

    agora = dt.datetime.now(FUSO)
    return {
        "atualizado": agora.strftime("%d/%m/%Y %H:%M"),
        "periodo": f"últimos {DIAS} dias",
        "total": {k: round(v, 2) for k, v in tot.items()},
        "canais": lista(canal_t),
        "papeis": lista(papel_t),
        "dias": sorted(lista(dia_t), key=lambda x: x["nome"]),
        "produtos": lista(prod_t)[:20],
    }


def trancar(dados, senha):
    """AES-GCM com chave PBKDF2-SHA256 (o painel abre com WebCrypto no navegador)."""
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

    sal, iv, voltas = os.urandom(16), os.urandom(12), 250_000
    chave = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=sal, iterations=voltas).derive(senha.encode())
    cifra = AESGCM(chave).encrypt(iv, json.dumps(dados, ensure_ascii=False).encode(), None)
    b64 = lambda b: base64.b64encode(b).decode()
    return {"v": 1, "voltas": voltas, "sal": b64(sal), "iv": b64(iv), "dados": b64(cifra)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--testar", action="store_true")
    args = ap.parse_args()

    fim = dt.datetime.now(FUSO)
    try:
        nodes = conversoes(fim - dt.timedelta(days=DIAS), fim)
    except Exception as e:  # mostra o motivo nos avisos (o registro não abre de fora)
        print(f"::error::Relatório da Shopee falhou: {str(e)[:600]}")
        raise
    if args.testar:  # repositório público: o registro mostra só quantidades
        com_marca = sum(1 for c in nodes if marcas(c.get("utmContent"))[0])
        print(f"::notice::Shopee respondeu: {len(nodes)} conversões em {DIAS} dias ({com_marca} com marca de canal).")
        return
    senha = os.environ.get("RELATORIO_SENHA", "").strip()
    if not senha:
        print("::warning::Falta o secret RELATORIO_SENHA: sem senha o relatório não é salvo (o repositório é público).")
        return
    produtos = json.loads(PRODUTOS.read_text(encoding="utf-8"))
    SAIDA.write_text(json.dumps(trancar(montar(nodes, produtos), senha)), encoding="utf-8")
    print(f"::notice::Relatório salvo trancado ({len(nodes)} conversões em {DIAS} dias).")


if __name__ == "__main__":
    main()
