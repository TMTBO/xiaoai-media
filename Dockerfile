# ── Stage 1: Build Vue frontend ──────────────────────────────────────────────
FROM node:20-slim AS frontend-builder

WORKDIR /build/frontend

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

COPY frontend/ ./
RUN npm run build:prod

# ── Stage 2: Python runtime ───────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Install gosu for safe user switching
RUN apt-get update && apt-get install -y --no-install-recommends \
    gosu \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user with HOME=/data
RUN groupadd -r appuser && useradd -r -g appuser -d /data appuser

# Create data directory and set ownership
RUN mkdir -p /data && chown -R appuser:appuser /data

WORKDIR /app

# Install Python dependencies
COPY backend/pyproject.toml ./
RUN pip install --no-cache-dir -e . || true
COPY backend/ ./backend/
RUN pip install --no-cache-dir -e backend/

# Copy built frontend into static/ so FastAPI can serve it
COPY --from=frontend-builder /build/frontend/dist ./static/

# Copy run script
COPY backend/run.py ./

# Ensure appuser can read /app directory (but not write)
RUN chown -R root:root /app && chmod -R 755 /app

# Copy entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Set HOME to data directory (affects Path.home() used by config.py)
ENV HOME=/data

# Expose port
EXPOSE 8000

# Volume for persistent data (playlists, config, etc.)
VOLUME ["/data"]

# Start as root to fix permissions, then switch to appuser
ENTRYPOINT ["docker-entrypoint.sh"]

CMD ["python", "run.py"]
