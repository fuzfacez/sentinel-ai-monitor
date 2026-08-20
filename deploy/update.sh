#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/.."
git pull --ff-only
sudo docker compose up -d --build
sudo docker compose ps
