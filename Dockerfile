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

RUN \
	mkdir -p /home/node/.n8n/customnodes && \
	chown node:node .n8n/customnodes && \ 
	mkdir -p /home/node/.n8n/binairydata && \
	chown node:node .n8n/binairydata

COPY n8n-nodes-n8nergonode-0.1.0.tgz /home/node/




RUN \ 
	mkdir /home/database && \
	apk add sqlite && \
	sqlite3 /home/database/onewaybike.db 'CREATE TABLE IF NOT EXISTS bikes (id INTEGER PRIMARY KEY, name TEXT);'
	
RUN \ 
	corepack prepare pnpm@latest --activate && \
	pnpm install --prefix '/home/node/.n8n/customnodes' '/home/node/n8n-nodes-n8nergonode-0.1.0.tgz'

# Setup the Task Runner Launcher

ENV N8N_RUNNERS_MODE=internal_launcher \
    N8N_RUNNERS_LAUNCHER_PATH=/usr/local/bin/task-runner-launcher
COPY n8n-task-runners.json /etc/n8n-task-runners.json

	

USER node

EXPOSE 5678
