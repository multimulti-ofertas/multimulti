"""Publicação na Página do Facebook "MultiMulti Ofertas" (Graph API da Meta).

Precisa do secret FBPAGETOKEN: token DA PÁGINA (não o do Instagram), com as permissões
pages_show_list, pages_read_engagement e pages_manage_posts. O token de Página tirado de um
token de usuário de longa duração não vence.
O token do Instagram (IGTOKEN) é de outro tipo (login do Instagram) e não consegue postar na Página.
"""
import os

import requests

from . import config

VERSAO = os.environ.get("FB_API_VERSION", "v23.0")
BASE = f"https://graph.facebook.com/{VERSAO}"


class FacebookErro(RuntimeError):
    pass


def configurado():
    return bool((os.environ.get("FB_PAGE_TOKEN") or "").strip())


def _req(metodo, url, **kw):
    r = requests.request(metodo, url, timeout=120, **kw)
    if r.status_code >= 400:
        raise FacebookErro(f"{r.status_code}: {r.text[:500]}")
    return r.json()


def _cred():
    tok = (os.environ.get("FB_PAGE_TOKEN") or "").strip()
    if not tok:
        raise FacebookErro("Falta o FBPAGETOKEN nos Secrets do GitHub.")
    pid = (os.environ.get("FB_PAGE_ID") or "").strip()
    if not pid:  # com token de Página, /me é a própria Página
        pid = str(_req("GET", f"{BASE}/me", params={"fields": "id", "access_token": tok})["id"])
    return pid, tok


def legenda(texto, n):
    """No Facebook o link é clicável: troca "Link na bio" pelo link direto do produto na vitrine
    e tira a linha do direct (o ManyChat só atende o Instagram)."""
    linhas = []
    for ln in (texto or "").splitlines():
        if ln.startswith("📩"):
            continue
        if ln.startswith("🛒"):
            ln = f"🛒 Link direto: {config.PAGES_URL}/?n={n}"
        linhas.append(ln)
    return "\n".join(linhas).replace("\n\n\n", "\n\n").strip()


def postar_imagem(url_jpg, texto):
    pid, tok = _cred()
    return _req("POST", f"{BASE}/{pid}/photos",
                data={"url": url_jpg, "message": texto, "access_token": tok})["id"]


def postar_reels(url_mp4, texto):
    """Reels da Página (3 etapas). Se a Página não aceitar Reels pela API, posta como vídeo normal."""
    pid, tok = _cred()
    try:
        ini = _req("POST", f"{BASE}/{pid}/video_reels", data={"upload_phase": "start", "access_token": tok})
        vid = ini["video_id"]
        _req("POST", f"https://rupload.facebook.com/video-upload/{VERSAO}/{vid}",
             headers={"Authorization": f"OAuth {tok}", "file_url": url_mp4})
        _req("POST", f"{BASE}/{pid}/video_reels",
             data={"upload_phase": "finish", "video_id": vid, "video_state": "PUBLISHED",
                   "description": texto, "access_token": tok})
        return vid
    except FacebookErro as e:
        print(f"[facebook] Reels não aceito ({e}); postando como vídeo.")
        return _req("POST", f"{BASE}/{pid}/videos",
                    data={"file_url": url_mp4, "description": texto, "access_token": tok})["id"]


def postar_story(url_jpg):
    pid, tok = _cred()
    foto = _req("POST", f"{BASE}/{pid}/photos",
                data={"url": url_jpg, "published": "false", "access_token": tok})["id"]
    d = _req("POST", f"{BASE}/{pid}/photo_stories", data={"photo_id": foto, "access_token": tok})
    return d.get("post_id") or d.get("id") or foto


def checar():
    """Retorna (nome da página, id) ou levanta erro."""
    pid, tok = _cred()
    d = _req("GET", f"{BASE}/{pid}", params={"fields": "id,name", "access_token": tok})
    return d.get("name"), d.get("id")

