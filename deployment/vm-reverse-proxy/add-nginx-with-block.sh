#!/bin/bash

set -e

echo "=== Installing Nginx ==="
sudo apt update
sudo apt install -y nginx

echo "=== Creating Nginx reverse proxy config for API ==="

NGINX_CONF="/etc/nginx/sites-available/api"

sudo bash -c "cat > $NGINX_CONF" <<EOF
server {
    listen 80;
    server_name _;

    # Block the /api/v1/auth/register endpoint
    location /api/v1/auth/register {
        return 403;
    }

    # Forward all other requests to your API
    location / {
        proxy_pass http://127.0.0.1:8000;

        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

echo "=== Enabling config ==="
sudo ln -sf /etc/nginx/sites-available/api /etc/nginx/sites-enabled/api

echo "=== Removing default site if exists ==="
sudo rm -f /etc/nginx/sites-enabled/default

echo "=== Testing Nginx configuration ==="
sudo nginx -t

echo "=== Reloading Nginx ==="
sudo systemctl reload nginx

echo "=== Done! Nginx reverse proxy is active with /api/v1/auth/register blocked. ==="
