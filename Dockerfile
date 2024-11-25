ARG NODE_VERSION=20
ARG N8N_VERSION=1.68.0
FROM n8nio/base:${NODE_VERSION}

ARG N8N_VERSION
RUN if [ -z "${N8N_VERSION}" ] ; then echo "The N8N_VERSION argument is missing!" ; exit 1; fi

LABEL org.opencontainers.image.title="n8n"
LABEL org.opencontainers.image.description="Workflow Automation Tool"
LABEL org.opencontainers.image.source="https://github.com/n8n-io/n8n"
LABEL org.opencontainers.image.url="https://n8n.io"
LABEL org.opencontainers.image.version=${N8N_VERSION}

ENV N8N_VERSION=${N8N_VERSION}
ENV NODE_ENV=production
ENV N8N_RELEASE_TYPE=stable

# Install nginx and setup directories with proper permissions
RUN apk add --no-cache nginx && \
    mkdir -p /run/nginx && \
    mkdir -p /tmp/nginx && \
    mkdir -p /var/lib/nginx && \
    mkdir -p /var/log/nginx && \
    mkdir -p /var/lib/nginx/tmp && \
    chown -R node:node /run/nginx && \
    chown -R node:node /tmp/nginx && \
    chown -R node:node /var/lib/nginx && \
    chown -R node:node /var/log/nginx && \
    chmod -R 755 /run/nginx && \
    chmod -R 755 /tmp/nginx && \
    chmod -R 755 /var/lib/nginx && \
    chmod -R 755 /var/log/nginx && \
    touch /tmp/nginx.conf && \
    chown node:node /tmp/nginx.conf

# Install n8n and dependencies
RUN set -eux; \
    npm install -g --omit=dev n8n@${N8N_VERSION} --ignore-scripts && \
    npm rebuild --prefix=/usr/local/lib/node_modules/n8n sqlite3 && \
    rm -rf /usr/local/lib/node_modules/n8n/node_modules/@n8n/chat && \
    rm -rf /usr/local/lib/node_modules/n8n/node_modules/n8n-design-system && \
    rm -rf /usr/local/lib/node_modules/n8n/node_modules/n8n-editor-ui/node_modules && \
    find /usr/local/lib/node_modules/n8n -type f -name "*.ts" -o -name "*.js.map" -o -name "*.vue" | xargs rm -f && \
    rm -rf /root/.npm

# Install serve for the frontend
RUN npm install -g serve

# Copy frontend files and build
COPY frontend /app/frontend
WORKDIR /app/frontend

# Install dependencies and build
RUN npm ci && \
    npm run build

WORKDIR /

COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

COPY n8n-nodes-n8nergonode-0.1.0.tgz /home/node/

RUN \
    mkdir .n8n && \
    chown node:node .n8n && \
    mkdir -p /home/node/.n8n/customnodes && \
    mkdir -p /home/node/.n8n/database && \
    mkdir -p /home/node/.n8n/python && \
    mkdir -p /home/node/.n8n/python/data && \
    chown -R node:node /home/node/.n8n

RUN \ 
    apk add sqlite && \
    sqlite3 /home/node/.n8n/database/onewaybike.db 'CREATE TABLE IF NOT EXISTS bikes (id INTEGER PRIMARY KEY, name TEXT);' && \
    chown node:node /home/node/.n8n/database/onewaybike.db && \ 
    chmod 664 /home/node/.n8n/database/onewaybike.db

RUN apk add python3
RUN apk add py3-pip
RUN apk add py3-requests
RUN apk add py3-pandas

# Copy files to persistent storage locations
COPY database/onewaybike.db /home/node/.n8n/database/onewaybike.db
COPY python/* /home/node/.n8n/python/
COPY python/data/* /home/node/.n8n/python/data/

RUN \ 
    corepack prepare pnpm@latest --activate && \
    COREPACK_ENABLE_NETWORK=1 COREPACK_YES=1 pnpm install --prefix '/home/node/.n8n/customnodes' '/home/node/n8n-nodes-n8nergonode-0.1.0.tgz'

# Setup the Task Runner Launcher
ARG TARGETPLATFORM
ARG LAUNCHER_VERSION=0.1.1
ENV N8N_RUNNERS_MODE=internal_launcher \
    N8N_RUNNERS_LAUNCHER_PATH=/usr/local/bin/task-runner-launcher
COPY n8n-task-runners.json /etc/n8n-task-runners.json

RUN \
    if [[ "$TARGETPLATFORM" = "linux/amd64" ]]; then export ARCH_NAME="x86_64"; \
    elif [[ "$TARGETPLATFORM" = "linux/arm64" ]]; then export ARCH_NAME="aarch64"; fi; \
    mkdir /launcher-temp && \
    cd /launcher-temp && \
    wget https://github.com/n8n-io/task-runner-launcher/releases/download/${LAUNCHER_VERSION}/task-runner-launcher-$ARCH_NAME-unknown-linux-musl.zip && \
    wget https://github.com/n8n-io/task-runner-launcher/releases/download/${LAUNCHER_VERSION}/task-runner-launcher-$ARCH_NAME-unknown-linux-musl.sha256 && \
    sha256sum -c task-runner-launcher-$ARCH_NAME-unknown-linux-musl.sha256 && \
    unzip -d $(dirname ${N8N_RUNNERS_LAUNCHER_PATH}) task-runner-launcher-$ARCH_NAME-unknown-linux-musl.zip task-runner-launcher && \
    cd - && \
    rm -r /launcher-temp && \
    chmod 4555 ${N8N_RUNNERS_LAUNCHER_PATH} && \
    addgroup -g 2000 task-runner && \
    adduser -D -u 2000 -g "Task Runner User" -G task-runner task-runner

ENV SHELL /bin/sh

# Make sure node user has access to the frontend build
RUN chown -R node:node /app/frontend

USER node

ENTRYPOINT ["tini", "--", "/docker-entrypoint.sh"]
