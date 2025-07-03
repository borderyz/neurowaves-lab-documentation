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



echo "[backup] ensuring Box CLI is configured…"
if ! box configure:environments:get >/dev/null 2>&1 ; then
  echo "[backup] Configuring Environment"
  /usr/local/bin/box configure:environments:add /opt/box_config.json
  echo "[backup] Environment Successfully configured"
fi
echo "[backup] Configuration found"
echo "[backup] uploading to Box…"

/usr/local/bin/box files:upload "$archive" -p "$BOX_FOLDER_ID"

echo "[backup] done $(date)"


status=$?
if [ $status -eq 0 ]; then
  subject="[MEG LAB] Moodle backup SUCCESS ($(date +%F\ %T))"
  body="Backup completed successfully.\nArchive: $archive is available on NYUBOX:://MEG/backup/moodle_backup"
else
  subject="[MEG LAB] Moodle backup FAILED ($(date +%F\ %T))"
  body="Backup script exited with status $status.\nCheck /var/log/backup.log."
fi

echo "[backup] sending e-mail notice…"

# --- build the message ---
printf "Subject:%s\nFrom:%s\nTo:%s\n\n%b" \
       "$subject" "$MAIL_FROM" "$MAIL_TO" "$body" \
  | msmtp --host=in-v3.mailjet.com \
          --port=587 \
          --auth=on \
          --tls=on --tls-starttls=on --tls-certcheck=off \
          --user="$MAILJET_USER" \
          --passwordeval="echo $MAILJET_PASS" \
          --from="$MAIL_FROM" \
          $MAIL_TO

echo "[backup] email sent $(date)"
exit $status
