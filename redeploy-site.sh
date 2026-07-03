#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/opt/selisah-portfolio-site"
VENV="$PROJECT_DIR/venv"
SERVICE="selisah"
DOMAIN="selisah.duckdns.org"

echo "==> Pulling latest code..."
cd "$PROJECT_DIR"
git pull origin main

echo "==> Installing dependencies..."
"$VENV/bin/python" -m pip install -r requirements.txt

echo "==> Fixing SELinux labels on venv binaries..."
chcon -R -t bin_t "$VENV/bin"

echo "==> Restarting $SERVICE..."
systemctl restart "$SERVICE"

echo "==> Checking service status..."
systemctl is-active --quiet "$SERVICE"

echo "==> Health check..."
sleep 2
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://$DOMAIN/")
if [[ "$HTTP_CODE" == "200" ]]; then
  echo "Deployment successful! Site returned HTTP $HTTP_CODE"
else
  echo "WARNING: Site returned HTTP $HTTP_CODE (expected 200)"
  exit 1
fi
