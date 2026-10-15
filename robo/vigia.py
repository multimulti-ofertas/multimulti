"""Vigia diário: confere se está tudo funcionando e FALHA (o GitHub manda e-mail) se algo quebrou.

Confere: token do Instagram, token da Página, vitrine no ar, ofertas de hoje geradas, posts de ontem
(Instagram e Facebook), stories ou produtos repetidos, robôs que falharam nas últimas 24h e quantos dias de produtos ainda restam.
Os resultados aparecem como avisos (annotations) na execução "Vigia diário".
"""
import datetime as dt
import os

import requests

from . import config, facebook, planilha
from .gerar import carregar, escolher, ja_usados, hoje
from .instagram import BASE

problemas = []


def ok(msg):
    print(f"::notice::✅ {msg}")


def atencao(msg):
    print(f"::warning::⚠️ {msg}")


def erro(msg):
    print(f"::error::❌ {msg}")
    problemas.append(msg)


def instagram():
    tok = (os.environ.get("IG_TOKEN") or "").strip()
    if not tok:
        return erro("Falta o secret IGTOKEN.")
    r = requests.get(f"{BASE}/me", params={"fields": "user_id,username", "access_token": tok}, timeout=30)
    if r.status_code != 200:
        return erro(f"Instagram recusou o token ({r.status_code}): {r.text[:200]}")
    uid = r.json().get("user_id")
    lim = requests.get(f"{BASE}/{uid}/content_publishing_limit",
                       params={"fields": "quota_usage", "access_token": tok}, timeout=30)
    if lim.status_code != 200:
        return erro(f"Instagram sem permissão de publicar ({lim.status_code}). A Meta pode ter bloqueado: "
                    "confirme a conta no perfil pessoal e rode o Vigia de novo.")
    ok(f"Instagram @{r.json().get('username')} funcionando")
    if not (os.environ.get("GH_PAT") or "").strip():
        atencao("Sem o secret GH_PAT: o token do Instagram não se renova sozinho.")


def pagina():
    if not facebook.configurado():
        return erro("Falta o secret FBPAGETOKEN (a Página do Facebook não recebe posts).")
    try:
        nome, _, _ = facebook.checar()
        ok(f"Página do Facebook {nome} funcionando")
    except Exception as e:
        erro(f"Página do Facebook recusou o token: {str(e)[:200]}")


def vitrine():
    try:
        r = requests.get(f"{config.PAGES_URL}/produtos.json", timeout=30)
        if r.status_code == 200 and r.json():
            ok("Vitrine no ar")
        else:
            erro(f"Vitrine fora do ar ou vazia ({r.status_code}).")
    except Exception as e:
        erro(f"Vitrine não respondeu: {e}")


def posts():
    lista = carregar()
    d = hoje()
    if not any(x["data"] == d.isoformat() for x in lista):
        erro(f"As ofertas de hoje ({d:%d/%m}) não foram geradas.")
    ontem = (d - dt.timedelta(days=1)).isoformat()
    do_dia = [x for x in lista if x["data"] == ontem]
    if not do_dia:
        return
    conta = {k: sum(1 for x in do_dia if (x.get("postado") or {}).get(k))
             for k in ("feed", "reel", "fb_feed", "fb_reel")}
    falta = [f"{k} {v}/2" for k, v in conta.items() if v < 2]
    if falta:
        atencao(f"Ontem saiu menos que o previsto: {', '.join(falta)}")
    else:
        ok("Ontem: 2 feeds e 2 Reels no Instagram e no Facebook")
    repetidos = [f"nº {x['n']}" for x in do_dia if int(x.get("stories") or 0) > 1
                 and ontem > "2026-10-15"]  # até 15/out repetir era a regra antiga (já corrigida)
    if repetidos:
        erro(f"Story repetido ontem: {', '.join(repetidos)}")
    else:
        ok(f"Ontem: {sum(1 for x in do_dia if x.get('stories'))} stories, nenhum repetido")


def repetidos():
    """Produto que já apareceu em outro dia (nunca pode repetir)."""
    vistos, dup = {}, []
    for x in sorted(carregar(), key=lambda x: x["n"]):
        iid = str(x.get("itemId"))
        if iid in vistos:
            dup.append(f"nº {x['n']} = nº {vistos[iid]}")
        vistos.setdefault(iid, x["n"])
    if dup:
        erro(f"Produto repetido: {', '.join(dup[:5])}")
    else:
        ok("Nenhum produto repetido")


def falhas():
    tok, repo = os.environ.get("GITHUB_TOKEN"), os.environ.get("GITHUB_REPOSITORY")
    if not tok or not repo:
        return
    desde = (dt.datetime.utcnow() - dt.timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")
    r = requests.get(f"https://api.github.com/repos/{repo}/actions/runs",
                     params={"created": f">={desde}", "per_page": 100},
                     headers={"Authorization": f"Bearer {tok}"}, timeout=30)
    if r.status_code != 200:
        return atencao(f"Não consegui ler as execuções ({r.status_code}).")
    ultima = {}  # só conta como problema se a execução MAIS RECENTE de cada robô falhou
    for x in sorted(r.json().get("workflow_runs", []), key=lambda x: x["created_at"]):
        if x["name"] != "Vigia diário" and x["status"] == "completed":
            ultima[x["name"]] = x["conclusion"]
    nomes = sorted(n for n, c in ultima.items() if c == "failure")
    if nomes:
        erro(f"Robôs com falha na última execução: {', '.join(nomes)}")
    else:
        ok("Todos os robôs funcionaram na última execução")


def estoque():
    if os.environ.get("SHOPEE_APP_ID"):
        return ok("Produtos vêm da API da Shopee (sem planilha para acabar)")
    lista = carregar()
    usados = ja_usados(lista, hoje())
    temas = {}
    total = []
    for c in ("carro", "ferramentas", "cuidado", "estilo"):
        do_tema, _ = planilha.candidatos(c)
        bons = escolher(do_tema, usados)
        temas[c] = len(bons)
        total += [p["itemId"] for _, p in bons]
    dias = len(set(total)) // config.PRODUTOS_POR_DIA
    resumo = " · ".join(f"{k} {v}" for k, v in temas.items())
    if dias < 2:
        erro(f"Produtos acabando: só {dias} dia(s) ({resumo}). Mande planilha nova.")
    elif dias < 4:
        atencao(f"Produtos para {dias} dias ({resumo}). Bom mandar planilha nova.")
    else:
        ok(f"Produtos para ~{dias} dias ({resumo})")


for etapa in (instagram, pagina, vitrine, posts, repetidos, falhas, estoque):
    try:
        etapa()
    except Exception as e:
        erro(f"{etapa.__name__}: {e}")

if problemas:
    raise SystemExit(f"{len(problemas)} problema(s) encontrado(s).")
print("Tudo certo.")
