#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

: "${BACKUP_DIR:?BACKUP_DIR manquant}"
: "${PGDATABASE:?PGDATABASE manquant}"
: "${PGUSER:?PGUSER manquant}"

TIMESTAMP="$(date -u +'%Y-%m-%dT%H%M%SZ')"
DEST="${BACKUP_DIR}/database"
FILE="${DEST}/${PGDATABASE}-${TIMESTAMP}.dump"

mkdir -p "${DEST}"

echo "[backup] Début ${TIMESTAMP}"

# Le mot de passe doit être fourni via une méthode sûre (.pgpass / environnement protégé).
pg_dump \
  --format=custom \
  --file="${FILE}" \
  "${PGDATABASE}"

pg_restore --list "${FILE}" >/dev/null
sha256sum "${FILE}" > "${FILE}.sha256"

echo "[backup] OK ${FILE}"

# La rotation et la copie distante doivent être ajoutées après définition
# explicite de la politique de rétention et du stockage cible.
