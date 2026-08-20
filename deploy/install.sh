#!/usr/bin/env bash
set -Eeuo pipefail

cd "$(dirname "$0")/.."

if [[ ! -f .env ]]; then
  echo "Ошибка: файл .env не найден. Выполните: cp deploy/server.env.example .env"
  exit 1
fi

if grep -q 'PASTE_' .env; then
  echo "Ошибка: замените все значения PASTE_... в .env"
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker не найден. Устанавливаю официальный пакет Ubuntu..."
  sudo apt-get update
  sudo apt-get install -y ca-certificates curl
  sudo install -m 0755 -d /etc/apt/keyrings
  sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  sudo chmod a+r /etc/apt/keyrings/docker.asc
  . /etc/os-release
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu ${UBUNTU_CODENAME:-$VERSION_CODENAME} stable" | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
  sudo apt-get update
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  sudo systemctl enable --now docker
fi

sudo docker compose up -d --build
sudo docker compose ps
echo
echo "Sentinel AI запущен. На своём компьютере создайте туннель:"
echo "ssh -N -L 8000:127.0.0.1:8000 USER@SERVER_IP"
echo "Затем откройте: http://localhost:8000/?token=ВАШ_ADMIN_TOKEN"
