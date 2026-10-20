"""Publicação no Instagram pela API oficial (Instagram API com login do Instagram).

Precisa de IG_USER_ID e IG_TOKEN (token de longa duração, 60 dias).
A mídia precisa estar num link público (GitHub Pages).
"""
import os
import time

import requests

VERSAO = os.environ.get("IG_API_VERSION", "v23.0")
BASE = f"https://graph.instagram.com/{VERSAO}"


class InstagramErro(RuntimeError):
    pass


def _cred():
    uid, tok = (os.environ.get("IG_USER_ID") or "").strip(), (os.environ.get("IG_TOKEN") or "").strip()
    if not tok:
        raise InstagramErro("Falta o IGTOKEN nos Secrets do GitHub.")
    if not uid:  # descobre o ID da conta pelo próprio token
        r = requests.get(f"{BASE}/me", params={"fields": "user_id", "access_token": tok}, timeout=30)
        if r.status_code >= 400:
            raise InstagramErro(f"Token recusado: {r.text[:300]}")
        uid = str(r.json()["user_id"])
    return uid, tok


def _req(metodo, url, **kw):
    r = requests.request(metodo, url, timeout=60, **kw)
    if r.status_code >= 400:
        raise InstagramErro(f"{r.status_code}: {r.text[:500]}")
    return r.json()


def esperar_url(url, tentativas=20):
    """Espera o GitHub Pages publicar o arquivo."""
    for _ in range(tentativas):
        try:
            if requests.head(url, timeout=20, allow_redirects=True).status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(15)
    raise InstagramErro(f"Arquivo não ficou disponível: {url}")


def _esperar_container(cid, tok, limite=600):
    t0 = time.time()
    while time.time() - t0 < limite:
        st = _req("GET", f"{BASE}/{cid}", params={"fields": "status_code,status", "access_token": tok})
        code = st.get("status_code")
        if code == "FINISHED":
            return
        if code in ("ERROR", "EXPIRED"):
            raise InstagramErro(f"Instagram recusou a mídia: {st}")
        time.sleep(10)
    raise InstagramErro("Tempo esgotado processando a mídia no Instagram.")


def ja_no_ar(n, horas=36):
    """Id do post (feed ou Reels) do produto nº n que JÁ está no perfil (procura "nº n" na legenda dos
    últimos posts). Evita post repetido quando o Instagram publica mas devolve erro."""
    import datetime as dt
    import re
    uid, tok = _cred()
    r = _req("GET", f"{BASE}/{uid}/media", params={"fields": "id,caption,timestamp", "limit": 30,
                                                   "access_token": tok})
    limite = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=horas)
    for m in r.get("data", []):
        quando = dt.datetime.strptime(m["timestamp"], "%Y-%m-%dT%H:%M:%S%z")
        if quando >= limite and re.search(rf"nº {int(n)}\b", m.get("caption") or ""):
            return m["id"]
    return None


def bloqueado(erro):
    """O Instagram bloqueou a conta/app por excesso (não adianta tentar de novo agora)."""
    s = str(erro)
    return "2207051" in s or "action is blocked" in s or "request limit reached" in s.lower()


def _publicar(uid, tok, cid):
    return _req("POST", f"{BASE}/{uid}/media_publish", data={"creation_id": cid, "access_token": tok})["id"]


def postar_imagem(url_jpg, legenda):
    uid, tok = _cred()
    esperar_url(url_jpg)
    c = _req("POST", f"{BASE}/{uid}/media", data={"image_url": url_jpg, "caption": legenda, "access_token": tok})
    _esperar_container(c["id"], tok, limite=120)
    return _publicar(uid, tok, c["id"])


def postar_reels(url_mp4, legenda, capa_url=None):
    uid, tok = _cred()
    esperar_url(url_mp4)
    dados = {"media_type": "REELS", "video_url": url_mp4, "caption": legenda,
             "share_to_feed": "true", "access_token": tok,
             "thumb_offset": "4500"}  # capa = quadro dos 4,5s (produto + nome); o 1º quadro saía quase vazio
    if capa_url:
        dados["cover_url"] = capa_url
    c = _req("POST", f"{BASE}/{uid}/media", data=dados)
    _esperar_container(c["id"], tok)
    return _publicar(uid, tok, c["id"])


def postar_story(url_jpg):
    uid, tok = _cred()
    esperar_url(url_jpg)
    c = _req("POST", f"{BASE}/{uid}/media", data={"media_type": "STORIES", "image_url": url_jpg, "access_token": tok})
    _esperar_container(c["id"], tok, limite=120)
    return _publicar(uid, tok, c["id"])


def renovar_token():
    """Renova o token de longa duração (vale mais 60 dias). Retorna o token novo."""
    _, tok = _cred()
    d = _req("GET", "https://graph.instagram.com/refresh_access_token",
             params={"grant_type": "ig_refresh_token", "access_token": tok})
    return d["access_token"], d.get("expires_in")
