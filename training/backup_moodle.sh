#!/usr/bin/env bash
set -euo pipefail

### 1. Config – edit to taste ###############################################
source "$(dirname "$0")/.backupenv"   # loads vars if present
CONTAINER_DB="${CONTAINER_DB:-training-db-1}"          # from `docker compose ps`
BACKUP_DIR="$(pwd)/backups"
RETENTION_DAYS=7                      # keep last 7 daily files
MYSQL_ROOT_PW="${MYSQL_ROOT_PW:?Need MYSQL_ROOT_PW}"           # match compose
DB_NAME="moodle"
CODE_DIR="$(pwd)/moodle"
DATA_DIR="$(pwd)/moodledata"
BOX_FOLDER_ID="${BOX_FOLDER_ID:?Need BOX_FOLDER_ID}"

###########################################################################

timestamp=$(date +%F_%H-%M)
tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT

echo "[INFO] Dumping database…"
docker exec "$CONTAINER_DB" \
  mariadb-dump -u root -p"$MYSQL_ROOT_PW" --single-transaction --quick "$DB_NAME" \
  > "$tmp_dir/db.sql"

echo "[INFO] Copying code & config…"
rsync -a --delete \
  --exclude='.git' "$CODE_DIR/" "$tmp_dir/moodle/"

echo "[INFO] Copying moodledata (excluding caches)…"
rsync -a \
  --exclude='cache' --exclude='localcache' --exclude='sessions' \
  --exclude='temp'  --exclude='trashdir' \
  "$DATA_DIR/" "$tmp_dir/moodledata/"

echo "version: $(date)" > "$tmp_dir/README.txt"
docker exec "$CONTAINER_DB" mariadb -u root -p"$MYSQL_ROOT_PW" -e \
  "SELECT VERSION();" >> "$tmp_dir/README.txt"

mkdir -p "$BACKUP_DIR"
archive="$BACKUP_DIR/moodle-full-$timestamp.tar.gz"
echo "[INFO] Creating $archive …"
tar -C "$tmp_dir" -czf "$archive" .

echo "[INFO] Pruning backups >$RETENTION_DAYS days old…"
find "$BACKUP_DIR" -name 'moodle-full-*.tar.gz' -mtime +"$RETENTION_DAYS" -delete
echo "[DONE] Backup stored at $archive"

echo "[INFO] Uploading to BOX"

box files:upload "$archive" --parent-id $BOX_FOLDER_ID

echo "[DONE] Backup uploaded to BOX"