"""Confere se o token do Instagram funciona (não posta nada).
Escreve o resultado também como aviso do GitHub (::notice:: / ::error::), para dar para ler sem abrir o registro."""
import os
import requests
from .instagram import BASE


def aviso(tipo, msg):
    print(msg)
    print(f"::{tipo}::{msg}".replace("\n", " "))


tok = (os.environ.get("IG_TOKEN") or "").strip()
uid = (os.environ.get("IG_USER_ID") or "").strip()
aviso("notice", f"IG_TOKEN configurado: {bool(tok)} | IG_USER_ID configurado: {bool(uid)}")
if not tok:
    aviso("error", "Falta o IGTOKEN nos Secrets.")
    raise SystemExit(1)
r = requests.get(f"{BASE}/me", params={"fields": "user_id,username,account_type,biography,website,followers_count,media_count",
                                       "access_token": tok}, timeout=30)
if r.status_code != 200:
    aviso("error", f"Instagram recusou o token ({r.status_code}): {r.text[:300]}")
    raise SystemExit(1)
d = r.json()
aviso("notice", f"Conta @{d.get('username', '?')} | tipo {d.get('account_type')} | id {d.get('user_id')} | "
                f"{d.get('followers_count')} seguidores | {d.get('media_count')} posts")
aviso("notice", f"Bio: {d.get('biography')!r} | Link da bio: {d.get('website')!r}")
if "multimulti-ofertas.github.io" not in (d.get("website") or "") + (d.get("biography") or ""):
    aviso("warning", "O link da vitrine não aparece na bio do Instagram (pode estar só nos 'links' extras).")
if uid and d.get("user_id") and str(d["user_id"]) != uid:
    aviso("warning", f"IGUSERID diferente do id da conta: {d['user_id']}")
lim = requests.get(f"{BASE}/{uid or d.get('user_id')}/content_publishing_limit",
                   params={"fields": "quota_usage,config", "access_token": tok}, timeout=30)
if lim.status_code == 200:
    aviso("notice", f"Permissão de publicar OK: {lim.text[:200]}")
else:
    aviso("error", f"Sem permissão de publicar ({lim.status_code}): {lim.text[:300]}")
    raise SystemExit(1)

# Página do Facebook
from . import facebook
if not facebook.configurado():
    aviso("warning", "Facebook: falta o secret FBPAGETOKEN (a Página não recebe posts).")
else:
    try:
        nome, pid, info = facebook.checar()
        aviso("notice", f"Facebook OK: Página {nome} | id {pid} | {info.get('followers_count')} seguidores")
        aviso("notice", f"Página: site {info.get('website')!r} | sobre {info.get('about')!r}")
    except Exception as e:
        aviso("error", f"Facebook recusou o token: {str(e)[:300]}")
        raise SystemExit(1)
