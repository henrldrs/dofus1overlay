import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "dofus.db"

def import_sample_dataset():
    """Populates initial dataset including Gelano and its components."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    sample_items = [
        (8252, "Gelano", "Ring", 60, "A famous golden ring giving +1 AP.", json.dumps([{"stat": "AP", "min": 1, "max": 1}]), "gelano.png"),
        (2422, "Rubis", "Resource", 40, "A polished red precious gemstone.", json.dumps([]), "rubis.png"),
        (2425, "Gelée Royale Bleue", "Resource", 50, "Royal jelly extracted from Blue Jellies.", json.dumps([]), "jelly_blue.png"),
        (2426, "Gelée Royale Menthe", "Resource", 50, "Mint flavored royal jelly.", json.dumps([]), "jelly_mint.png")
    ]

    cursor.executemany(
        "INSERT OR REPLACE INTO items (id, name, type, level, description, stats_json, icon_url) VALUES (?, ?, ?, ?, ?, ?, ?)",
        sample_items
    )

    sample_recipes = [
        (8252, 2422, 10),   # Gelano needs 10 Rubis
        (8252, 2425, 100),  # Gelano needs 100 Gelée Royale Bleue
        (8252, 2426, 100)   # Gelano needs 100 Gelée Royale Menthe
    ]

    cursor.executemany(
        "INSERT OR REPLACE INTO recipes (result_item_id, ingredient_item_id, quantity) VALUES (?, ?, ?)",
        sample_recipes
    )

    sample_drops = [
        ("Gélatine Bleue Royale", 2425, 1.5, 100),
        ("Gélatine Menthe Royale", 2426, 1.5, 100)
    ]

    cursor.executemany(
        "INSERT INTO drops (monster_name, item_id, drop_rate, prospecting_lock) VALUES (?, ?, ?, ?)",
        sample_drops
    )

    conn.commit()
    conn.close()
    print("Sample dataset ingested successfully.")

if __name__ == "__main__":
    import_sample_dataset()
