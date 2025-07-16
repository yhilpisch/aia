#!/usr/bin/env bash
#
# deploy.sh — automated deployment of the Algorithmic Trading Bootcamp landing page
# Usage: ./deploy.sh <server-ip>

set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <server-ip>"
  exit 1
fi

SERVER_IP=$1
SSH_DEST=root@${SERVER_IP}
APP_DIR=/opt/bootcamp
SERVICE_NAME=bootcamp

echo "=== Installing system packages on ${SERVER_IP} ==="
ssh ${SSH_DEST} << 'INSTALL_PACKAGES'
apt update
apt install -y python3 python3-venv python3-pip nginx
INSTALL_PACKAGES

echo "=== Syncing application files to ${SSH_DEST}:${APP_DIR} ==="
rsync -avz --exclude '__pycache__' --exclude '.git' --exclude '.ipynb_checkpoints/' ./ ${SSH_DEST}:${APP_DIR}/

echo "=== Configuring application on remote host ==="
ssh ${SSH_DEST} << REMOTE_SETUP
set -euo pipefail
cd ${APP_DIR}

# Create & activate virtual environment, install dependencies
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt gunicorn
deactivate

# systemd service for Gunicorn
cat > /etc/systemd/system/${SERVICE_NAME}.service << 'SERVICE_EOF'
[Unit]
Description=Gunicorn instance to serve Algorithmic Trading Bootcamp
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=${APP_DIR}
Environment="PATH=${APP_DIR}/venv/bin"
ExecStart=${APP_DIR}/venv/bin/gunicorn --workers 3 --bind unix:${APP_DIR}/${SERVICE_NAME}.sock app:app

[Install]
WantedBy=multi-user.target
SERVICE_EOF

systemctl daemon-reload
systemctl enable ${SERVICE_NAME}.service
systemctl restart ${SERVICE_NAME}.service

# nginx site configuration
cat > /etc/nginx/sites-available/${SERVICE_NAME} << 'NGINX_EOF'
server {
    listen 80;
    server_name _;
    root ${APP_DIR};

    location / {
        proxy_pass http://unix:${APP_DIR}/${SERVICE_NAME}.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /tpq_logo_bic.png { try_files \$uri =404; }
    location /genai_bootcamp.png { try_files \$uri =404; }
}
NGINX_EOF

ln -sf /etc/nginx/sites-available/${SERVICE_NAME} /etc/nginx/sites-enabled/${SERVICE_NAME}
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

# ensure proper file ownership
chown -R www-data:www-data ${APP_DIR}
REMOTE_SETUP

echo "=== Deployment to ${SERVER_IP} completed. ==="
