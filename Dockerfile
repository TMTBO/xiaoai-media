# ── Stage 1: Build Vue frontend ──────────────────────────────────────────────
FROM node:20-slim AS frontend-builder

WORKDIR /build/frontend

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

COPY frontend/ ./
RUN npm run build:prod

# ── Stage 2: Python runtime ───────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Install Python dependencies
COPY backend/pyproject.toml ./
RUN pip install --no-cache-dir -e . || true
COPY backend/ ./backend/
RUN pip install --no-cache-dir -e backend/

# Copy built frontend into static/ so FastAPI can serve it
COPY --from=frontend-builder /build/frontend/dist ./static/

# Runtime environment defaults (real values come from --env-file or -e flags)
ENV MI_REGION=cn \
    MI_USER="" \
    MI_PASS="" \
    MI_DID=""

EXPOSE 8000

USER appuser

CMD ["uvicorn", "xiaoai_media.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
