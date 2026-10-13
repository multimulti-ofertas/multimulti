"""Confere se o token do Instagram funciona (não posta nada)."""
import os
import requests
from .instagram import BASE

tok = os.environ.get("IG_TOKEN")
uid = os.environ.get("IG_USER_ID")
print("IG_TOKEN configurado:", bool(tok))
print("IG_USER_ID configurado:", bool(uid))
if not tok:
    raise SystemExit("Falta o IGTOKEN nos Secrets.")
r = requests.get(f"{BASE}/me", params={"fields": "user_id,username,account_type", "access_token": tok}, timeout=30)
print("Resposta do Instagram:", r.status_code)
if r.status_code != 200:
    raise SystemExit(r.text[:300])
d = r.json()
print("Conta:", "@" + d.get("username", "?"), "| tipo:", d.get("account_type"), "| id:", d.get("user_id"))
if uid and d.get("user_id") and str(d["user_id"]) != uid.strip():
    print("AVISO: IGUSERID diferente do id da conta:", d["user_id"])
lim = requests.get(f"{BASE}/{uid or d.get('user_id')}/content_publishing_limit",
                   params={"fields": "quota_usage,config", "access_token": tok}, timeout=30)
print("Permissão de publicar:", "OK" if lim.status_code == 200 else lim.text[:300])
