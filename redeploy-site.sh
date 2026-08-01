#!/usr/bin/env bash
set -euo pipefail

cd /opt/selisah-portfolio-site

git fetch origin
git reset --hard origin/main

docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build
