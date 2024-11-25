FROM n8nio/n8n:1.68.0

USER root

COPY n8n-nodes-n8nergonode-0.1.0.tgz /home/node/

RUN \
	mkdir -p /home/node/.n8n/customnodes && \
	chown node:node .n8n/customnodes


RUN \ 
	mkdir /home/database && \
	apk add sqlite && \
	sqlite3 /home/database/onewaybike.db 'CREATE TABLE IF NOT EXISTS bikes (id INTEGER PRIMARY KEY, name TEXT);'
	
RUN \ 
	corepack prepare pnpm@latest --activate && \
	COREPACK_ENABLE_NETWORK=1 COREPACK_YES=1 pnpm install --prefix '/home/node/.n8n/customnodes' '/home/node/n8n-nodes-n8nergonode-0.1.0.tgz'

USER node

EXPOSE 5678
