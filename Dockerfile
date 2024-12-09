FROM n8nio/n8n:1.70.3

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
	mkdir /home/node/.n8n/customnodes && \
	chown node:node .n8n/customnodes && \
	mkdir /home/node/.n8n/binairydata && \
	chown node:node .n8n/binairydata && \
	mkdir /home/node/.n8n/python && \
	chown node:node .n8n/python && \
	mkdir /home/node/.n8n/database && \
	chown node:node .n8n/database

COPY n8n-nodes-n8nergonode-0.1.0.tgz /home/node/
COPY src/* /home/node/.n8n/python


RUN \ 
	apk add sqlite && \
	sqlite3 /home/node/.n8n/database/onewaybike.db 'CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY, name TEXT);' 
	
RUN chown node:node /home/node/.n8n/database
RUN chown node:node /home/node/.n8n/database/onewaybike.db
RUN chmod 0666 /home/node/.n8n/database/onewaybike.db
RUN \ 
	corepack prepare pnpm@latest --activate && \
	pnpm install --prefix '/home/node/.n8n/customnodes' '/home/node/n8n-nodes-n8nergonode-0.1.0.tgz'

# Setup the Task Runner Launcher
RUN npm install jsonwebtoken
ENV N8N_RUNNERS_MODE=internal_launcher \
    N8N_RUNNERS_LAUNCHER_PATH=/usr/local/bin/task-runner-launcher
COPY n8n-task-runners.json /etc/n8n-task-runners.json

	

USER node

EXPOSE 5678
