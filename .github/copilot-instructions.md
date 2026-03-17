# XiaoAI Media — Copilot Instructions

## Project Overview
Full-stack application for managing Xiaomi AI speakers.
- **Backend**: Python + FastAPI, located in `backend/`, packaged with `pyproject.toml`.
- **Frontend**: Vue 3 + TypeScript + Vite + Element Plus, located in `frontend/`.

---

## Backend Conventions

### Dependency Management
- All Python dependencies are declared in `backend/pyproject.toml`. Never add `pip install <pkg>` for project dependencies to the Makefile.
- The Makefile `install-backend` target may install build-time prerequisites (e.g. `aiohttp aiofiles`) only as a workaround for upstream packages whose `setup.py` imports dependencies at metadata-collection time. Document such workarounds with a comment.

### Configuration (`config.py`)
- All env-var fields must be **optional** at startup (`_optional()`). Never raise at import time for missing credentials — the user may configure them from the frontend Settings page.
- Sensitive fields (`MI_PASS`, `MI_PASS_TOKEN`) should have no default; empty string is fine.

### Config API (`routes/config.py`)
- Sensitive fields are **masked** in GET responses: return `"***"` when the value is set, `""` when empty.
- `_write_env_file` must be followed by syncing values into `os.environ`, then `importlib.reload(config)`, so changes take effect immediately without restarting the server.

### Logging
- Every module that calls external services must use `logging.getLogger(__name__)`.
- Log before and after each external call: include operation name, key parameters (not secrets), and the result/error.

### Route modules
- Each route file handles one domain (`devices`, `tts`, `volume`, `command`, `config`).
- Use `XiaoAiClient` as an async context manager (`async with XiaoAiClient() as client`) — never share a client instance across requests.

---

## Frontend Conventions

### API Layer (`src/api/index.ts`)
- All request/response shapes are typed via exported interfaces (`Device`, `Config`, etc.).
- Keep interfaces in sync with backend Pydantic models whenever a field is added or removed.

### Composables
- Reusable stateful logic that is used by more than one component must be extracted into `src/composables/`.  
  Example: `useDevices.ts` — device list loading with loading/error state.

### Device Selection
- Any field that accepts a device ID **must** use an `<el-select>` populated from the device list API, with a refresh button (`<el-icon><Refresh /></el-icon>`).  
  Never use a plain `<el-input>` for device ID.

### Sensitive Fields in Settings
- Password fields: always clear on load (never echo back to the form).
- Token fields (e.g. `MI_PASS_TOKEN`): show the masked sentinel `"***"` from the API so the user knows the field is already set.  
  When saving, skip the field if the value is empty **or** still equals `"***"` (treat as "no change").

### Path Aliases
- Always use the `@/` alias for imports within `src/`. Never use relative `../` paths across more than one level.

---

## Makefile
- Targets: `install`, `install-backend`, `install-frontend`, `backend`, `frontend`, `dev`, `docker-build`, `docker-run`, `list-devices`, `clean`.
- Do not add new targets without a corresponding entry in the `help` target.
