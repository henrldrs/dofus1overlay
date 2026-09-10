import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "dofus.db"

def init_db(db_path=DB_PATH):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        level INTEGER NOT NULL,
        description TEXT,
        stats_json TEXT, -- JSON array of {stat, min, max}
        icon_url TEXT
    );

    CREATE TABLE IF NOT EXISTS recipes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        result_item_id INTEGER NOT NULL,
        ingredient_item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        FOREIGN KEY (result_item_id) REFERENCES items(id),
        FOREIGN KEY (ingredient_item_id) REFERENCES items(id)
    );

    CREATE TABLE IF NOT EXISTS drops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        monster_name TEXT NOT NULL,
        item_id INTEGER NOT NULL,
        drop_rate REAL NOT NULL,
        prospecting_lock INTEGER DEFAULT 100,
        FOREIGN KEY (item_id) REFERENCES items(id)
    );

    -- Full-Text Search Virtual Table
    CREATE VIRTUAL TABLE IF NOT EXISTS items_fts USING fts5(
        name,
        type,
        description,
        content='items',
        content_rowid='id'
    );

    -- Triggers to maintain FTS index sync
    CREATE TRIGGER IF NOT EXISTS items_ai AFTER INSERT ON items BEGIN
        INSERT INTO items_fts(rowid, name, type, description) 
        VALUES (new.id, new.name, new.type, new.description);
    END;

    CREATE TRIGGER IF NOT EXISTS items_ad AFTER DELETE ON items BEGIN
        INSERT INTO items_fts(items_fts, rowid, name, type, description) 
        VALUES('delete', old.id, old.name, old.type, old.description);
    END;
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database schema and FTS indexes initialized.")
