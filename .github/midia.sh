#!/usr/bin/env bash
# Mídias (fotos, artes, Reels) ficam no ramo "midia", fora do main, para o histórico não crescer.
# O ramo "midia" tem UM commit só e é recriado do zero a cada envio (só os últimos 10 dias).
#   bash .github/midia.sh baixar   -> coloca o conteúdo do ramo em docs/media
#   bash .github/midia.sh enviar   -> recria o ramo "midia" com o docs/media atual
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

case "${1:-}" in
  baixar)
    mkdir -p docs/media
    if git fetch -q --depth=1 origin midia 2>/dev/null; then
      git archive FETCH_HEAD | tar -x -C docs/media
      echo "Mídias baixadas: $(ls docs/media | wc -l) pastas"
    else
      echo "::warning::Ramo midia não existe ainda (docs/media vazio)"
    fi
    ;;
  enviar)
    idx="$(mktemp -u)"
    GIT_INDEX_FILE="$idx" git --work-tree=docs/media add -A -f .
    arvore="$(GIT_INDEX_FILE="$idx" git write-tree)"
    rm -f "$idx"
    commit="$(git -c user.name=robo-multimulti -c user.email=robo@users.noreply.github.com \
      commit-tree "$arvore" -m "Mídias $(TZ=America/Cuiaba date '+%F %H:%M')")"
    git push -q -f origin "$commit:refs/heads/midia"
    echo "Ramo midia recriado: $(ls docs/media | wc -l) pastas"
    ;;
  *) echo "uso: midia.sh baixar|enviar" >&2; exit 2 ;;
esac
