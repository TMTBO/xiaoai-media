SHELL := /bin/bash
.DEFAULT_GOAL := help

VENV      := .venv
PYTHON    := $(VENV)/bin/python
PIP       := $(VENV)/bin/pip
UVICORN   := $(VENV)/bin/uvicorn

# ── Help ───────────────────────────────────────────────────────────────────────
.PHONY: help
help:
	@echo ""
	@echo "  XiaoAI Media — Development Commands"
	@echo ""
	@echo "  Setup"
	@echo "    make install            Install all dependencies (backend venv + frontend npm)"
	@echo "    make install-backend    Create venv and install backend dependencies"
	@echo "    make install-frontend   Install frontend npm dependencies"
	@echo ""
	@echo "  Run"
	@echo "    make backend            Start FastAPI backend (hot reload, port 8000)"
	@echo "    make frontend           Start Vue dev server (port 5173)"
	@echo "    make dev                Start both backend and frontend concurrently"
	@echo ""
	@echo "  Docker"
	@echo "    make docker-build       Build Docker image locally"
	@echo "    make docker-run         Run Docker image with .env file"
	@echo ""
	@echo "  Utils"
	@echo "    make list-devices       List connected Xiaomi AI speaker devices"
	@echo "    make clean              Remove build artifacts and caches"
	@echo ""

# ── Setup ──────────────────────────────────────────────────────────────────────
.PHONY: install install-backend install-frontend

install: install-backend install-frontend

install-backend: $(VENV)
	# workaround: miservice's setup.py imports aiohttp/aiofiles at metadata-collection
	# time (upstream bug), so they must exist before `pip install -e` resolves deps.
	$(PIP) install aiohttp aiofiles
	$(PIP) install -e backend/

$(VENV):
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip

install-frontend:
	cd frontend && npm install

# ── Run ────────────────────────────────────────────────────────────────────────
.PHONY: backend frontend dev

backend: $(VENV)
	PYTHONPATH=backend/src $(UVICORN) xiaoai_media.api.main:app \
		--reload \
		--host 127.0.0.1 \
		--port 8000

frontend:
	cd frontend && npm run dev

dev:
	@echo "Starting backend and frontend..."
	@trap 'kill 0' INT; \
	PYTHONPATH=backend/src $(UVICORN) xiaoai_media.api.main:app \
		--reload --host 127.0.0.1 --port 8000 & \
	cd frontend && npm run dev & \
	wait

# ── Docker ─────────────────────────────────────────────────────────────────────
.PHONY: docker-build docker-run

IMAGE_TAG ?= xiaoai-media:local

docker-build:
	docker build --platform linux/amd64 -t $(IMAGE_TAG) .

docker-run:
	docker run --rm -p 8000:8000 --env-file .env $(IMAGE_TAG)

# ── Utils ──────────────────────────────────────────────────────────────────────
.PHONY: list-devices clean

list-devices: $(VENV)
	PYTHONPATH=backend/src $(PYTHON) -c "\
import asyncio; \
from xiaoai_media.client import XiaoAiClient; \
async def run(): \
    async with XiaoAiClient() as c: \
        for d in await c.list_devices(): print(d); \
asyncio.run(run())"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf frontend/dist frontend/.vite
