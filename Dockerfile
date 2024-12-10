FROM n8nio/n8n:1.70.3

USER root

ARG TARGETPLATFORM
ARG LAUNCHER_VERSION=0.1.1v
ARG COREPACK_YES=1
ARG COREPACK_ENABLE_NETWORK=1

ENV N8N_CUSTOM_EXTENSIONS=/home/node/.n8n/customnodes
ENV N8N_COMMUNITY_PACKAGES_ENABLED=true
ENV N8N_COMMUNITY_PACKAGES_REGISTRY=https://registry.npmjs.org
ENV N8N_BINARY_DATA_STORAGE_PATH=/home/node/.n8n/binairydata
ENV DB_SQLITE_VACUUM_ON_STARTUP=true
ENV TINI_SUBREAPER=true

# Install required packages
RUN apk add --no-cache su-exec
RUN apk add --update python3 py3-pip python3-dev

# Create necessary directories and set permissions
RUN \
    mkdir -p /home/node/.n8n/customnodes && \
    mkdir -p /home/node/.n8n/binairydata && \
    mkdir -p /home/node/.n8n/python && \
    mkdir -p /home/node/.n8n/database && \
    chown -R node:node /home/node/.n8n && \
    chmod -R 755 /home/node/.n8n

# Create symbolic link from /root/.n8n to /home/node/.n8n
RUN rm -rf /root/.n8n && \
    ln -s /home/node/.n8n /root/.n8n

RUN \ 
apk add sqlite && \
sqlite3 /home/node/.n8n/database/onewaybike.db 'CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY, name TEXT);' 
RUN chown node:node /home/node/.n8n/database
RUN chown node:node /home/node/.n8n/database/onewaybike.db
RUN chmod 0666 /home/node/.n8n/database/onewaybike.db


# Create and activate virtual environment
RUN python3 -m venv /home/node/.n8n/python/venv
ENV PATH="/home/node/.n8n/python/venv/bin:$PATH"

# Copy Python files and requirements
COPY ./src /home/node/.n8n/python/
COPY requirements.txt /home/node/.n8n/python/

# Install Python dependencies in virtual environment
RUN . /home/node/.n8n/python/venv/bin/activate && \
    pip3 install --no-cache-dir -r /home/node/.n8n/python/requirements.txt

# Copy and install n8n custom node
COPY n8n-nodes-n8nergonode-0.1.0.tgz /home/node/

# Install n8n custom node
RUN \ 
    corepack prepare pnpm@latest --activate && \
    pnpm install --prefix '/home/node/.n8n/customnodes' '/home/node/n8n-nodes-n8nergonode-0.1.0.tgz' && \
    chown -R node:node /home/node/.n8n/customnodes

# Setup the Task Runner Launcher
RUN npm install jsonwebtoken
ENV N8N_RUNNERS_MODE=internal_launcher \
    N8N_RUNNERS_LAUNCHER_PATH=/usr/local/bin/task-runner-launcher
COPY n8n-task-runners.json /etc/n8n-task-runners.json

# Expose both n8n and Python API ports
EXPOSE 5678 8000

USER root
