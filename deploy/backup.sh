#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/.."
set -a
. ./.env
set +a
mkdir -p backups
backup_file="backups/sentinel-$(date -u +%Y%m%d-%H%M%S).sql.gz"
sudo docker compose exec -T db pg_dump -U "${POSTGRES_USER:-sentinel}" "${POSTGRES_DB:-sentinel}" | gzip > "$backup_file"
find backups -type f -name 'sentinel-*.sql.gz' -mtime "+${BACKUP_RETENTION_DAYS:-14}" -delete
echo "Backup: $backup_file"
