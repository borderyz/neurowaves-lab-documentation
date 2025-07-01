#!/usr/bin/env bash
set -euo pipefail

# ---- config from env ----
DB_CONTAINER_NAME=${DB_CONTAINER_NAME:?}
DB_NAME=${DB_NAME:?}
DB_USER=${DB_USER:?}
DB_PASS=${DB_PASS:?}
BOX_FOLDER_ID=${BOX_FOLDER_ID:?}

BACKUP_DIR=/backups
RETENTION_DAYS=7
# -------------------------

ts=$(date +%F_%H-%M)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

echo "[backup] dumping DB…"
docker exec "$DB_CONTAINER_NAME" \
  mariadb-dump -u"$DB_USER" -p"$DB_PASS" --single-transaction --quick "$DB_NAME" \
  > "$tmp/db.sql"

echo "[backup] syncing code + data…"
rsync -a --exclude='.git' /moodle/ "$tmp/moodle/"
rsync -a --exclude='{cache,localcache,sessions,temp,trashdir}' \
       /moodledata/ "$tmp/moodledata/"

archive="$BACKUP_DIR/moodle-full-$ts.tar.gz"
tar -C "$tmp" -czf "$archive" .

find "$BACKUP_DIR" -name 'moodle-full-*.tar.gz' -mtime +$RETENTION_DAYS -delete

echo "[backup] uploading to Box…"
/usr/local/bin/box configure:environments:add /opt/box_config.json
/usr/local/bin/box files:upload "$archive" -p "$BOX_FOLDER_ID"

echo "[backup] done $(date)"
