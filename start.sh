#!/bin/sh
set -e

# Ensure nginx directories exist and have correct permissions
mkdir -p /tmp/client_temp /tmp/proxy_temp /tmp/fastcgi_temp /tmp/uwsgi_temp /tmp/scgi_temp
chown -R nginx:nginx /tmp/*
chmod -R 755 /tmp

# Ensure frontend files have correct permissions
chown -R nginx:nginx /usr/share/nginx/frontend
chmod -R 755 /usr/share/nginx/frontend

# Ensure n8n directories have correct permissions
chown -R node:node /home/node/.n8n
chmod -R 755 /home/node/.n8n
chown -R node:node /root/.n8n
chmod -R 755 /root/.n8n

# Start nginx with daemon off
/usr/sbin/nginx -g 'daemon off;' &

# Wait a moment for nginx to start
sleep 2

# Start n8n as node user with the full path
su-exec node /usr/local/bin/n8n start
