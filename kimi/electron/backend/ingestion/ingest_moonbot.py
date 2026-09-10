import requests
import sqlite3
import json
from pathlib import Path
import time

DB_PATH = Path(__file__).parent.parent.parent / "data" / "dofus.db"
BASE_URL = "https://wiki.moon-bot.io/api"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def fetch_json(url):
    try:
        res = requests.get(url, timeout=15)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None

def process_item(item_id):
    detail = fetch_json(f"{BASE_URL}/item/{item_id}.json")
    if not detail:
        return False
    
    conn = get_db()
    cursor = conn.cursor()
    
    # FIX: Handle null/missing fields with safe defaults
    name = detail.get("name") or "Unknown"
    item_type = detail.get("type") or "Unknown"
    level = detail.get("level") or 1
    weight = detail.get("weight") or 0
    description = detail.get("description") or ""
    url = detail.get("url") or ""
    stats = detail.get("stats") or []
    
    try:
        cursor.execute("""
            INSERT INTO items (id, solomonk_id, name, type, level, pods, description, stats_json, icon_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name=excluded.name, type=excluded.type, level=excluded.level,
                description=excluded.description, stats_json=excluded.stats_json
        """, (
            item_id,
            url,
            name,
            item_type,
            int(level),
            int(weight),
            description,
            json.dumps(stats),
            f"https://wiki.moon-bot.io/icons/sprite_{item_id}.png"
        ))

        recipe = detail.get("recipe") or []
        for ing in recipe:
            ing_id = ing.get("item_id")
            ing_name = ing.get("name") or "Unknown"
            qty = ing.get("qty") or 1
            
            if ing_id:
                cursor.execute("""
                    INSERT INTO recipes (result_item_id, ingredient_name, ingredient_item_id, quantity)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(result_item_id, ingredient_name) DO UPDATE SET
                        ingredient_item_id=excluded.ingredient_item_id, quantity=excluded.quantity
                """, (item_id, ing_name, ing_id, int(qty)))

        conn.commit()
    except Exception as e:
        print(f"⚠️ Error on item {item_id}: {e}", flush=True)
    finally:
        conn.close()
    
    return True

def run_ingestion():
    print("🚀 Resuming ingestion (keeping existing data)...", flush=True)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # NO DELETE - resume from where we left off
    
    print("📡 Fetching master item list...", flush=True)
    items_list = fetch_json(f"{BASE_URL}/items.json")
    
    if not items_list:
        print("❌ Failed to fetch items.json", flush=True)
        return

    print(f"✅ Found {len(items_list)} items. Starting sequential ingestion...", flush=True)
    
    completed = 0
    failed = 0
    skipped = 0
    start_time = time.time()
    
    for item in items_list:
        item_id = item["id"]
        
        # Skip items already in DB (fast resume)
        conn = get_db()
        exists = conn.execute("SELECT 1 FROM items WHERE id = ?", (item_id,)).fetchone()
        conn.close()
        
        if exists:
            skipped += 1
            completed += 1
            continue
        
        success = process_item(item_id)
        
        if success:
            completed += 1
        else:
            failed += 1
        
        # Print progress every 100 items
        if (completed + failed) % 100 == 0:
            elapsed = time.time() - start_time
            rate = (completed + failed) / elapsed if elapsed > 0 else 0
            remaining = (len(items_list) - completed - failed) / rate if rate > 0 else 0
            print(f"⏳ {completed}/{len(items_list)} items ({skipped} skipped, {failed} failed)... ({rate:.1f}/sec, ~{remaining/60:.1f} mins left)", flush=True)

    print("🔄 Rebuilding FTS search index...", flush=True)
    conn = get_db()
    try:
        conn.execute("INSERT INTO items_fts(items_fts) VALUES('rebuild');")
    except Exception as e:
        print(f"FTS rebuild warning: {e}", flush=True)
    conn.commit()
    conn.close()

    print(f"🎉 Ingestion complete! {completed} items total, {skipped} already existed, {failed} failed.", flush=True)

if __name__ == "__main__":
    run_ingestion()
