#!/usr/bin/env bash
#
# revert_deploy.sh — undo deployment performed by deploy.sh
# Usage: ./revert_deploy.sh <server-ip>

set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <server-ip>"
  exit 1
fi

SERVER_IP=$1
SSH_DEST=root@${SERVER_IP}
SERVICE_NAME=bootcamp
APP_DIR=/opt/bootcamp
DOMAIN=genai.tpq.io

echo "=== Reverting deployment on ${SERVER_IP} ==="
ssh ${SSH_DEST} << UNDO
set -euo pipefail

# Stop and disable the Gunicorn service
systemctl stop ${SERVICE_NAME}.service || true
systemctl disable ${SERVICE_NAME}.service || true
rm -f /etc/systemd/system/${SERVICE_NAME}.service
systemctl daemon-reload

# Remove nginx site configuration and restore default
rm -f /etc/nginx/sites-enabled/${SERVICE_NAME}
rm -f /etc/nginx/sites-available/${SERVICE_NAME}
ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default || true
nginx -t
systemctl reload nginx

# Revoke and delete the SSL certificate
certbot delete --noninteractive --cert-name ${DOMAIN} || true

# Remove application directory and virtualenv
rm -rf ${APP_DIR}

# (Optional) Remove installed packages:
# apt remove --purge -y python3-venv python3-pip nginx certbot python3-certbot-nginx || true
# apt autoremove -y || true

echo "=== Reversion complete on ${SERVER_IP} ==="
UNDO
