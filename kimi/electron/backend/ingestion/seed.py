import sqlite3
import json
from db.database import get_db, init_db

def import_sample_dataset():
    init_db()
    conn = get_db()
    cursor = conn.cursor()

    sample_items = [
        (8252, "gelano", "Gelano", "Ring", 60, "A famous golden ring giving +1 AP.", json.dumps([{"stat": "AP", "min": 1, "max": 1}]), "gelano.png"),
        (2422, "rubis", "Rubis", "Resource", 40, "A polished red precious gemstone.", json.dumps([]), "rubis.png"),
        (2425, "gelee_bleue", "Gelée Royale Bleue", "Resource", 50, "Royal jelly extracted from Blue Jellies.", json.dumps([]), "jelly_blue.png"),
        (2426, "gelee_menthe", "Gelée Royale Menthe", "Resource", 50, "Mint flavored royal jelly.", json.dumps([]), "jelly_mint.png")
    ]

    cursor.executemany(
        "INSERT OR REPLACE INTO items (id, solomonk_id, name, type, level, description, stats_json, icon_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        sample_items
    )

    sample_recipes = [
        (8252, "Rubis", 2422, 10),
        (8252, "Gelée Royale Bleue", 2425, 100),
        (8252, "Gelée Royale Menthe", 2426, 100)
    ]

    cursor.executemany(
        "INSERT OR REPLACE INTO recipes (result_item_id, ingredient_name, ingredient_item_id, quantity) VALUES (?, ?, ?, ?)",
        sample_recipes
    )

    sample_drops = [
        ("Gélatine Bleue Royale", "Gelée Royale Bleue", 2425, 1.5, 100),
        ("Gélatine Menthe Royale", "Gelée Royale Menthe", 2426, 1.5, 100)
    ]

    cursor.executemany(
        "INSERT OR REPLACE INTO drops (monster_name, item_name, item_id, drop_rate, prospecting_lock) VALUES (?, ?, ?, ?, ?)",
        sample_drops
    )

    try:
        conn.execute("INSERT INTO items_fts(items_fts) VALUES('rebuild');")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()
    print("✅ Sample dataset ingested successfully.")

if __name__ == "__main__":
    import_sample_dataset()
