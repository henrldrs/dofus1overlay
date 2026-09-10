import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "dofus.db"

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY,
        solomonk_id TEXT UNIQUE,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        level INTEGER NOT NULL DEFAULT 1,
        pods INTEGER DEFAULT 0,
        description TEXT,
        stats_json TEXT,
        icon_url TEXT
    );
    CREATE TABLE IF NOT EXISTS recipes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        result_item_id INTEGER NOT NULL,
        ingredient_name TEXT NOT NULL,
        ingredient_item_id INTEGER,
        quantity INTEGER NOT NULL,
        FOREIGN KEY (result_item_id) REFERENCES items(id) ON DELETE CASCADE,
        FOREIGN KEY (ingredient_item_id) REFERENCES items(id) ON DELETE SET NULL,
        UNIQUE(result_item_id, ingredient_name)
    );
    CREATE TABLE IF NOT EXISTS drops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        monster_name TEXT NOT NULL,
        item_name TEXT NOT NULL,
        item_id INTEGER,
        drop_rate REAL NOT NULL,
        prospecting_lock INTEGER DEFAULT 100,
        FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE SET NULL
    );
    CREATE VIRTUAL TABLE IF NOT EXISTS items_fts USING fts5(
        name, type, description,
        content='items',
        content_rowid='id'
    );
    """)
    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_PATH}")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
