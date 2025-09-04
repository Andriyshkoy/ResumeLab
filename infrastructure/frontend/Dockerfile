FROM node:20-alpine AS build
WORKDIR /app
COPY frontend/package*.json frontend/tsconfig*.json frontend/vite.config.ts ./
COPY frontend/index.html ./index.html
COPY frontend/src ./src
COPY frontend/public ./public

ARG VITE_API_BASE_URL=""
ARG VITE_AUTH_STORAGE="local"
ARG VITE_POLL_INTERVAL_MS="1000"
ARG VITE_POLL_TIMEOUT_MS="60000"
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
ENV VITE_AUTH_STORAGE=${VITE_AUTH_STORAGE}
ENV VITE_POLL_INTERVAL_MS=${VITE_POLL_INTERVAL_MS}
ENV VITE_POLL_TIMEOUT_MS=${VITE_POLL_TIMEOUT_MS}

RUN npm ci --no-audit --no-fund && npm run build

FROM alpine:3.20
WORKDIR /app
COPY --from=build /app/dist /app/dist
# Shared volume target for nginx
VOLUME ["/dist"]
# Populate shared volume with built assets and exit successfully
CMD sh -c "mkdir -p /dist && cp -r /app/dist/* /dist/ && touch /dist/.ready"
