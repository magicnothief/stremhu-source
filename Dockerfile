# ---- Node.js Build Stage ----
FROM node:24-bookworm-slim AS node-build

WORKDIR /app
ARG APP_VERSION=0.0.0

# Build Client
WORKDIR /app/client
COPY client ./
RUN npm ci
RUN npm run build

# ---- Runtime Stage ----
FROM python:3.12-slim-bookworm AS runtime

ARG APP_VERSION=0.0.0

RUN apt-get update && apt-get upgrade -y && \
  apt-get install -y --no-install-recommends ca-certificates libstdc++6 \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./

RUN python -m venv /opt/venv && \
  /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy client build to server/client so that SPAStaticFiles can find it
COPY --from=node-build /app/client/dist ./server/client

# Copy server code
COPY server ./server

# Environment setup
ENV NODE_ENV=production
ENV VERSION=${APP_VERSION}
ENV PATH="/opt/venv/bin:${PATH}"
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
ENV SSL_CERT_DIR=/etc/ssl/certs

WORKDIR /app/server

EXPOSE 7070/tcp
EXPOSE 6881/tcp 6881/udp

CMD ["python", "run.py"]
