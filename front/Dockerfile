# ---- dev: hot-reloading Vite, the target of `make up` ----
FROM node:20-alpine AS dev
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev"]

# ---- build: emit static assets ----
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# ---- prod: nginx serving the SPA ----
FROM nginx:1.27-alpine AS prod
COPY --from=build /app/dist /usr/share/nginx/html
# The official nginx entrypoint expands only CLICKHOUSE_UPSTREAM. Restricting
# the filter preserves nginx's own $uri/$host variables in the template.
ENV NGINX_ENVSUBST_FILTER=^(CLICKHOUSE_UPSTREAM|APEX_API_UPSTREAM)$
# Defaulted HERE and not in 30-apex-console-config.sh: the image's own
# 20-envsubst-on-templates.sh runs FIRST, so a value exported by our script
# would arrive after the template was already rendered, leaving the literal
# ${APEX_API_UPSTREAM} in the served config and nginx refusing to start.
# A ClickHouse-mode deployment never sends a /v1 request; if one arrives
# anyway, this address refuses it immediately instead of breaking boot.
ENV APEX_API_UPSTREAM=http://127.0.0.1:1
COPY nginx.conf /etc/nginx/templates/default.conf.template
# Deployment configuration is written at container START, not baked into the
# bundle: Vite inlines every VITE_* reference, so an image built once would
# otherwise be pinned to one database, one user and one mode. The same script
# refuses to start when CLICKHOUSE_UPSTREAM is missing, which nginx would
# otherwise report only as "invalid URL prefix".
COPY docker-entrypoint.d/30-apex-console-config.sh /docker-entrypoint.d/
RUN chmod +x /docker-entrypoint.d/30-apex-console-config.sh
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
