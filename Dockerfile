# Build React frontend
FROM node:18 AS frontend-builder
WORKDIR /app
COPY frontend/ ./
RUN npm install
RUN npm run build

# Final image
FROM n8nio/n8n:1.68.0

USER root

ARG TARGETPLATFORM
ARG LAUNCHER_VERSION=0.1.1
ARG COREPACK_YES=1
ARG COREPACK_ENABLE_NETWORK=1

ENV N8N_CUSTOM_EXTENSIONS=/home/node/.n8n/customnodes
ENV N8N_COMMUNITY_PACKAGES_ENABLED=true
ENV N8N_COMMUNITY_PACKAGES_ENABLED=true
ENV N8N_COMMUNITY_PACKAGES_REGISTRY=https://registry.npmjs.org
ENV N8N_BINARY_DATA_STORAGE_PATH=/home/node/.n8n/binairydata
ENV DB_SQLITE_VACUUM_ON_STARTUP=true
ENV TINI_SUBREAPER=true

# Install nginx and su-exec using apk
RUN apk add --no-cache nginx su-exec

# Set up n8n directories and permissions
RUN mkdir -p /home/node/.n8n/customnodes && \
    mkdir -p /home/node/.n8n/binairydata && \
    chown -R node:node /home/node && \
    chmod -R 755 /home/node/.n8n

COPY n8n-nodes-n8nergonode-0.1.0.tgz /home/node/

RUN \ 
    mkdir /home/database && \
    apk add sqlite && \
    sqlite3 /home/database/qwikwinsservice.db 'CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY, name TEXT);' && \
    chown -R node:node /home/database

RUN \ 
    corepack prepare pnpm@latest --activate && \
    pnpm install --prefix '/home/node/.n8n/customnodes' '/home/node/n8n-nodes-n8nergonode-0.1.0.tgz' && \
    chown -R node:node /home/node/.n8n/customnodes

# Setup the Task Runner Launcher
RUN npm install jsonwebtoken
ENV N8N_RUNNERS_MODE=internal_launcher \
    N8N_RUNNERS_LAUNCHER_PATH=/usr/local/bin/task-runner-launcher
COPY n8n-task-runners.json /etc/n8n-task-runners.json

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create directory for frontend files and nginx temp directories
RUN mkdir -p /usr/share/nginx/frontend && \
    mkdir -p /tmp/client_temp /tmp/proxy_temp /tmp/fastcgi_temp /tmp/uwsgi_temp /tmp/scgi_temp && \
    chown -R nginx:nginx /tmp/* && \
    chmod -R 755 /tmp

# Copy built React frontend
COPY --from=frontend-builder /app/build /usr/share/nginx/frontend

# Copy and set up start script
COPY start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh

# Ensure n8n can write to its config directory
RUN mkdir -p /root/.n8n && \
    chown -R node:node /root/.n8n && \
    chmod -R 755 /root/.n8n

USER root
ENTRYPOINT ["tini", "-s", "--"]
CMD ["/usr/local/bin/start.sh"]

EXPOSE 80
