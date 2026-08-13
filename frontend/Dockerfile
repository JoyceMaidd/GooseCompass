# Multi-stage: 1. build, 2. Nginx serving

# Stage 1: Build
FROM node:18-alpine AS builder
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci --legacy-peer-deps
COPY frontend/ ./
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine
COPY nginx.conf /etc/nginx/nginx.conf.template
RUN apk add --no-cache gettext
COPY --from=builder /build/dist /usr/share/nginx/html
EXPOSE 3000
CMD ["sh", "-c", "envsubst < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf && nginx -g 'daemon off;'"]
