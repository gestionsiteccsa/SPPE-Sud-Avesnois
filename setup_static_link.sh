#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 <dossier-du-domaine> <racine-application>"
  echo "Exemple: $0 ~/bddpe.fr ~/bdd_pe"
  exit 1
}

if [ "$#" -ne 2 ]; then
  usage
fi

DOCROOT="${1/#\~/$HOME}"
APP_ROOT="${2/#\~/$HOME}"

if [ ! -d "$DOCROOT" ]; then
  echo "ERREUR: le dossier du domaine n'existe pas: $DOCROOT"
  exit 1
fi

if [ ! -d "$APP_ROOT" ]; then
  echo "ERREUR: la racine de l'application n'existe pas: $APP_ROOT"
  exit 1
fi

STATIC_TARGET="$APP_ROOT/staticfiles"
if [ ! -d "$STATIC_TARGET" ]; then
  echo "ERREUR: $STATIC_TARGET n'existe pas. Lancer d'abord: python manage.py collectstatic --noinput"
  exit 1
fi

LINK="$DOCROOT/static"
if [ -e "$LINK" ] && [ ! -L "$LINK" ]; then
  echo "ERREUR: un element existe deja dans $LINK mais ce n'est pas un lien symbolique."
  exit 1
fi

if [ -L "$LINK" ]; then
  CURRENT=$(readlink "$LINK")
  if [ "$CURRENT" = "$STATIC_TARGET" ]; then
    echo "Le lien existe deja et pointe correctement vers $STATIC_TARGET"
  else
    echo "Le lien pointe vers $CURRENT, remplacement par $STATIC_TARGET"
    ln -sfn "$STATIC_TARGET" "$LINK"
  fi
else
  echo "Creation du lien $LINK -> $STATIC_TARGET"
  ln -s "$STATIC_TARGET" "$LINK"
fi

if [ -f "$LINK/css/tailwind.css" ] && [ -f "$LINK/css/app.min.css" ] && [ -f "$LINK/js/bundle.min.js" ]; then
  echo "OK: les principaux assets sont accessibles via le lien."
else
  echo "ATTENTION: certains assets sont absents dans $LINK. Verifier le collectstatic."
  exit 1
fi

echo "Termine. Recharger le site avec Ctrl+F5."