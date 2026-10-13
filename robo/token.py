"""Renova o token do Instagram e imprime o novo (o workflow salva nos Secrets)."""
from . import instagram

if __name__ == "__main__":
    novo, expira = instagram.renovar_token()
    print(f"::add-mask::{novo}")
    with open("novo_token.txt", "w") as f:
        f.write(novo)
    print(f"Token renovado. Expira em {int(expira or 0) // 86400} dias.")
