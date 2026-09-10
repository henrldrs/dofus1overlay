import sqlite3
import requests
import json
from pathlib import Path

DB_PATH = Path(r"D:\CODING\dofus1overlay\data\dofus.db")
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

print(" Checking current icon URLs...\n")

# Check a few monster icons
print("Sample monster icons:")
for m in c.execute("SELECT id, name, icon_url FROM monsters LIMIT 5").fetchall():
    print(f"  {m[1]}: {m[2]}")

print("\nSample item icons:")
for i in c.execute("SELECT id, name, icon_url FROM items LIMIT 5").fetchall():
    print(f"  {i[1]}: {i[2]}")

# Fetch Moonbot search index for correct icon paths
print("\n📡 Fetching Moonbot search index for correct icons...")
try:
    res = requests.get("https://wiki.moon-bot.io/api/search-index.json", timeout=15)
    if res.status_code == 200:
        search_index = res.json()
        print(f"✅ Got {len(search_index)} entries with icons")
        
        # Update item icons
        updated_items = 0
        for entry in search_index:
            if entry.get("c") == "Objet" and entry.get("i"):
                icon_url = f"https://wiki.moon-bot.io{entry['i']}"
                # Try to find matching item by name
                item = c.execute("SELECT id FROM items WHERE LOWER(name) = LOWER(?)", (entry["n"],)).fetchone()
                if item:
                    c.execute("UPDATE items SET icon_url = ? WHERE id = ?", (icon_url, item[0]))
                    updated_items += 1
        conn.commit()
        print(f"✅ Updated {updated_items} item icons")
        
        # Update monster icons
        updated_monsters = 0
        for entry in search_index:
            if entry.get("c") == "Monstre" and entry.get("i"):
                icon_url = f"https://wiki.moon-bot.io{entry['i']}"
                monster = c.execute("SELECT id FROM monsters WHERE LOWER(name) = LOWER(?)", (entry["n"],)).fetchone()
                if monster:
                    c.execute("UPDATE monsters SET icon_url = ? WHERE id = ?", (icon_url, monster[0]))
                    updated_monsters += 1
        conn.commit()
        print(f"✅ Updated {updated_monsters} monster icons")
    else:
        print(f" Failed to fetch search index: HTTP {res.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

conn.close()
print("\n✅ Icon fix complete!")
