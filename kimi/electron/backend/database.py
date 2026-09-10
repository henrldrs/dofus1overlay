import sqlite3
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/dofus.db'))

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    # Core Tables
    c.execute('''CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY, name TEXT, type TEXT, level INTEGER, stats_json TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS recipes (
        item_id INTEGER, ingredient_id INTEGER, quantity INTEGER,
        PRIMARY KEY (item_id, ingredient_id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS monsters (
        id INTEGER PRIMARY KEY, name TEXT, level INTEGER, family TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS drops (
        monster_id INTEGER, item_id INTEGER, chance REAL,
        PRIMARY KEY (monster_id, item_id)
    )''')
    
    # FTS5 for instant search
    c.execute('''CREATE VIRTUAL TABLE IF NOT EXISTS items_fts USING fts5(
        name, content='items', content_rowid='id'
    )''')
    
    # Triggers to keep FTS in sync
    c.execute('''CREATE TRIGGER IF NOT EXISTS items_ai AFTER INSERT ON items BEGIN
        INSERT INTO items_fts(rowid, name) VALUES (new.id, new.name);
    END''')
    c.execute('''CREATE TRIGGER IF NOT EXISTS items_ad AFTER DELETE ON items BEGIN
        INSERT INTO items_fts(items_fts, rowid, name) VALUES('delete', old.id, old.name);
    END''')
    
    conn.commit()
    conn.close()