# Railway wrapper: Apex API (apex-api) + stdio MCP server (apex-mcp) from serve/.
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /usr/local/bin/uv
WORKDIR /app
COPY engine /app/engine
COPY serve /app/serve
WORKDIR /app/serve
RUN uv sync --frozen --no-dev
ENV PATH=/app/serve/.venv/bin:$PATH APEX_API_HOST=:: APEX_API_PORT=8099
EXPOSE 8099
CMD ["apex-api"]
