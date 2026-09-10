import sqlite3
import json
from pathlib import Path

db_path = Path(__file__).parent.parent / "data" / "dofus.db"
db_path.parent.mkdir(parents=True, exist_ok=True)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.executescript("""
CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, solomonk_id TEXT UNIQUE, name TEXT NOT NULL, type TEXT NOT NULL, level INTEGER NOT NULL DEFAULT 1, pods INTEGER DEFAULT 0, description TEXT, stats_json TEXT, icon_url TEXT);
CREATE TABLE IF NOT EXISTS recipes (id INTEGER PRIMARY KEY AUTOINCREMENT, result_item_id INTEGER NOT NULL, ingredient_name TEXT NOT NULL, ingredient_item_id INTEGER, quantity INTEGER NOT NULL, UNIQUE(result_item_id, ingredient_name));
CREATE TABLE IF NOT EXISTS drops (id INTEGER PRIMARY KEY AUTOINCREMENT, monster_name TEXT NOT NULL, item_name TEXT NOT NULL, item_id INTEGER, drop_rate REAL NOT NULL, prospecting_lock INTEGER DEFAULT 100);
CREATE VIRTUAL TABLE IF NOT EXISTS items_fts USING fts5(name, type, description, content='items', content_rowid='id');
""")

items = [
    (8252, 'gelano', 'Gelano', 'Ring', 60, 'A famous golden ring giving +1 AP.', json.dumps([{'stat': 'AP', 'min': 1, 'max': 1}]), 'gelano.png'),
    (2422, 'rubis', 'Rubis', 'Resource', 40, 'A polished red precious gemstone.', json.dumps([]), 'rubis.png'),
    (2425, 'gelee_bleue', 'Gelée Royale Bleue', 'Resource', 50, 'Royal jelly extracted from Blue Jellies.', json.dumps([]), 'jelly_blue.png'),
    (2426, 'gelee_menthe', 'Gelée Royale Menthe', 'Resource', 50, 'Mint flavored royal jelly.', json.dumps([]), 'jelly_mint.png')
]
cursor.executemany('INSERT OR REPLACE INTO items (id, solomonk_id, name, type, level, description, stats_json, icon_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', items)

recipes = [(8252, 'Rubis', 2422, 10), (8252, 'Gelée Royale Bleue', 2425, 100), (8252, 'Gelée Royale Menthe', 2426, 100)]
cursor.executemany('INSERT OR REPLACE INTO recipes (result_item_id, ingredient_name, ingredient_item_id, quantity) VALUES (?, ?, ?, ?)', recipes)

drops = [('Gélatine Bleue Royale', 'Gelée Royale Bleue', 2425, 1.5, 100), ('Gélatine Menthe Royale', 'Gelée Royale Menthe', 2426, 1.5, 100)]
cursor.executemany('INSERT OR REPLACE INTO drops (monster_name, item_name, item_id, drop_rate, prospecting_lock) VALUES (?, ?, ?, ?, ?)', drops)

try:
    cursor.execute("INSERT INTO items_fts(items_fts) VALUES('rebuild');")
except:
    pass

conn.commit()
conn.close()
print('✅ Database seeded successfully!')
