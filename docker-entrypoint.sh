#!/bin/sh

if [ -d /opt/custom-certificates ]; then
  echo "Trusting custom certificates from /opt/custom-certificates."
  export NODE_OPTIONS=--use-openssl-ca $NODE_OPTIONS
  export SSL_CERT_DIR=/opt/custom-certificates
  c_rehash /opt/custom-certificates
fi

echo "Starting initialization..."

# Create nginx configuration
cat > /tmp/nginx.conf << 'EOF'
worker_processes auto;
pid /tmp/nginx.pid;
daemon off;
error_log /dev/stderr debug;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    access_log /dev/stdout;
    error_log /dev/stderr debug;
    
    upstream frontend {
        server 127.0.0.1:3000;
    }
    
    upstream n8n {
        server 127.0.0.1:8080;
    }

    map $http_upgrade $connection_upgrade {
        default upgrade;
        ''      close;
    }
    
    server {
        listen 8081;
        server_name _;
        client_max_body_size 16M;
        
        # Frontend at root path
        location / {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection $connection_upgrade;
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # n8n at /n8n path
        location /n8n/ {
            proxy_pass http://n8n/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection $connection_upgrade;
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # WebSocket support
            proxy_buffering off;
            proxy_read_timeout 1800;
            proxy_send_timeout 1800;
            proxy_connect_timeout 75;
        }

        # Additional location for n8n webhooks
        location /n8n/webhook/ {
            proxy_pass http://n8n/webhook/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection $connection_upgrade;
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
EOF

echo "Created nginx configuration"

# Ensure nginx directories exist and have correct permissions
echo "Setting up nginx directories..."
mkdir -p /tmp/nginx
mkdir -p /var/lib/nginx/tmp
chown -R node:node /tmp/nginx
chown -R node:node /var/lib/nginx
chmod -R 755 /var/lib/nginx

# Start the frontend server in the background
echo "Starting frontend server..."
serve -s /app/frontend/build -p 3000 &

# Start n8n in the background
echo "Starting n8n..."
n8n start &

# Wait a moment for the services to start
sleep 5

# Test nginx configuration
echo "Testing nginx configuration..."
nginx -t -c /tmp/nginx.conf

# Start nginx in the foreground
echo "Starting nginx..."
exec nginx -c /tmp/nginx.conf
