# Railway wrapper: front/ prod target (nginx SPA). front/Dockerfile expects front/ as context;
# Railway builds from the repo root, so this mirrors its build + prod stages with front/ paths.
FROM node:20-alpine AS build
WORKDIR /app
COPY front/package.json front/package-lock.json ./
RUN npm ci
COPY front/ .
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
ENV NGINX_ENVSUBST_FILTER=^(CLICKHOUSE_UPSTREAM|APEX_API_UPSTREAM)$
ENV APEX_API_UPSTREAM=http://127.0.0.1:1
ENV CLICKHOUSE_UPSTREAM=http://127.0.0.1:1
COPY front/nginx.conf /etc/nginx/templates/default.conf.template
COPY front/docker-entrypoint.d/30-apex-console-config.sh /docker-entrypoint.d/
RUN chmod +x /docker-entrypoint.d/30-apex-console-config.sh
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
