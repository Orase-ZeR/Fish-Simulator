#===============================================================
#||               Script d'installation (batch)               ||
#===============================================================
#|| Fonction basiques : Détecte la présence de python et une  ||
#|| bonne version (>=3.11) ou jette une erreur.               ||
#||                                                           ||
#||         /!\ Tentera d'installer PIP si Absent             ||
#||                                                           ||
#|| Pas testé et pas forcément fonctionnel contrairement au   ||
#|| batch.                                                    ||
#||                                                           ||
#|| Si ça fonctionne pas s'assurer de la version (>=3.11) et  ||
#|| installer le ./requirements.txt                           ||
#===============================================================
#||                        Gaetan F.                          ||
#===============================================================

#!/usr/bin/env bash
set -euo pipefail

PY=""
for cand in python3.11 python3 python; do
  if command -v "$cand" >/dev/null 2>&1; then
    PY="$cand"
    break
  fi
done

if [ -z "${PY:-}" ]; then
  echo "ERREUR: Python non trouvé. Installez Python 3.11+ : https://www.python.org/downloads/"
  exit 1
fi

PYVER=$($PY --version 2>&1 | awk '{print $2}')
if [ -z "$PYVER" ]; then
  echo "ERREUR: Impossible de déterminer la version de Python via '$PY --version'."
  exit 1
fi

IFS='.' read -r MAJOR MINOR PATCH <<< "$PYVER"
MAJOR=${MAJOR:-0}
MINOR=${MINOR:-0}

echo "Python trouvé: $PY (version $PYVER)"

if [ "$MAJOR" -lt 3 ] || { [ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 11 ]; }; then
  echo "ERREUR: Python 3.11 ou supérieur requis (version trouvée: $PYVER)."
  exit 1
fi

if ! $PY -m pip --version >/dev/null 2>&1; then
  echo "pip introuvable pour $PY. Tentative d'installation via ensurepip..."
  if $PY -m ensurepip --upgrade >/dev/null 2>&1; then
    echo "ensurepip exécuté avec succès."
    $PY -m pip install --upgrade pip setuptools wheel
  else
    echo "ensurepip a échoué. Tentative d'installation via get-pip.py..."
    TMPFILE=""
    if command -v curl >/dev/null 2>&1; then
      TMPFILE=$(mktemp)
      trap 'rm -f "$TMPFILE"' EXIT
      curl -sS https://bootstrap.pypa.io/get-pip.py -o "$TMPFILE"
    elif command -v wget >/dev/null 2>&1; then
      TMPFILE=$(mktemp)
      trap 'rm -f "$TMPFILE"' EXIT
      wget -q -O "$TMPFILE" https://bootstrap.pypa.io/get-pip.py
    else
      echo "ERREUR: ni curl ni wget disponibles pour récupérer get-pip.py. Installez pip manuellement."
      exit 1
    fi

    if [ -n "${TMPFILE:-}" ]; then
      if $PY "$TMPFILE"; then
        echo "get-pip.py exécuté avec succès."
        $PY -m pip install --upgrade pip setuptools wheel
      else
        echo "ERREUR: L'exécution de get-pip.py a échoué."
        exit 1
      fi
    fi
  fi
fi

REQ="./requirements.txt"
if [ -f "$REQ" ]; then
  echo "Installation des dépendances depuis $REQ ..."
  if $PY -m pip install -r "$REQ"; then
    echo "Installation terminée avec succès."
    exit 0
  else
    echo "ERREUR: L'installation des dépendances a échoué."
    exit 1
  fi
else
  echo "ERREUR: requirements.txt introuvable dans le cd ($(pwd))."
  exit 1
fi