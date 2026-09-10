# 📂 Dofus Rétro Companion - Directory Audit

## 1. Active Project Structure (KEEP)

| Path | Size | Purpose |
| --- | --- | --- |
| `data\dofus.db` | 7232 KB | ✅ ACTIVE: The main SQLite database (11,716 items, 133 monsters, profiles). |

| Path | Size | Purpose |
| --- | --- | --- |
| `kimi\electron\backend\app.py` | 11.76 KB | ✅ ACTIVE: Flask REST API server (handles DB queries, profiles, farming). |

| Path | Size | Purpose |
| --- | --- | --- |
| `kimi\electron\backend\ingestion\ingest_monsters.py` | 1.68 KB | ✅ ACTIVE: Script to fetch 1,471 monsters from Moonbot API. |

| Path | Size | Purpose |
| --- | --- | --- |
| `kimi\electron\backend\ingestion\ingest_moonbot.py` | 4.43 KB | ✅ ACTIVE: Script to fetch 11,716 items from Moonbot API. |

| Path | Size | Purpose |
| --- | --- | --- |
| `kimi\electron\backend\ingestion\scrape_solomonk.py` | 5.48 KB | ✅ ACTIVE: Cloudflare-bypass scraper (currently blocked by Solomonk). |

| Path | Size | Purpose |
| --- | --- | --- |
| `kimi\electron\main.js` | 1.75 KB | ✅ ACTIVE: Electron main process (handles window creation, IPC resize, hotkeys). |

| Path | Size | Purpose |
| --- | --- | --- |
| `kimi\electron\overlay\index.html` | 27.38 KB | ✅ ACTIVE: The entire UI, CSS, and Frontend JavaScript. |

| Path | Size | Purpose |
| --- | --- | --- |
| `kimi\electron\package.json` | 0.18 KB | ✅ ACTIVE: Node.js manifest for Electron dependencies. |

| Path | Size | Purpose |
| --- | --- | --- |
| `kimi\electron\preload.js` | 0.29 KB | ✅ ACTIVE: Electron security bridge (exposes IPC to frontend). |

| Path | Size | Purpose |
| --- | --- | --- |
| `start_companion.bat` | 2.44 KB | ✅ ACTIVE: Unified launcher (starts Backend + Electron). |

## 2. Legacy / Duplicate Folders (DELETE)

These folders are remnants from early development or duplicated structures. They are **not** used by the active launcher.

- ❌ `backend`
- ❌ `electron`
- ❌ `agent`
- ❌ `gemini`
- ❌ `tests`
- ❌ `kimi\electron\data`
- ❌ `kimi\electron\dofus-data`
- ❌ `kimi\electron\agent`

## 3. Dependency Folders (DO NOT TOUCH)

- `kimi\electron\node_modules` (Electron/Node dependencies)
- `kimi\electron\backend\venv` (Python virtual environment)
- `kimi\electron\backend\__pycache__` (Python bytecode cache)

