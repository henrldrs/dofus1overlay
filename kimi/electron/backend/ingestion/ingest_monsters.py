import requests
import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "dofus.db"
BASE_URL = "https://wiki.moon-bot.io/api"

def run():
    print("📡 Fetching monster list...", flush=True)
    res = requests.get(f"{BASE_URL}/monsters.json", timeout=15)
    if res.status_code != 200:
        print("❌ Failed to fetch monsters.json", flush=True)
        return
    monsters = res.json()
    print(f"✅ Found {len(monsters)} monsters. Saving to DB...", flush=True)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS monsters (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        level_min INTEGER DEFAULT 1,
        level_max INTEGER DEFAULT 1,
        boss INTEGER DEFAULT 0,
        weakness TEXT,
        url TEXT
    )""")
    conn.commit()

    count = 0
    for m in monsters:
        mid = m.get("id")
        if not mid:
            continue
        name = m.get("name", "Unknown")
        lvl = m.get("level_min", "1")
        lvl_max = m.get("level_max", lvl)
        # level_min can be a string like "1 à 6"
        try:
            lmin = int(str(lvl).split()[0])
        except:
            lmin = 1
        try:
            lmax = int(str(lvl_max).split()[-1])
        except:
            lmax = lmin

        c.execute("""INSERT OR REPLACE INTO monsters (id, name, level_min, level_max, boss, weakness, url)
                     VALUES (?, ?, ?, ?, ?, ?, ?)""",
                  (mid, name, lmin, lmax, 0, "", m.get("url", "")))
        count += 1

    conn.commit()
    conn.close()
    print(f"🎉 Saved {count} monsters!", flush=True)

if __name__ == "__main__":
    run()
