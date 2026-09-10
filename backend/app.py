from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import requests as http_requests
import sqlite3
from pathlib import Path

DB_PATH = Path(r"D:\CODING\dofus1overlay\data\dofus.db")

def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, solomonk_id TEXT UNIQUE, name TEXT NOT NULL, type TEXT NOT NULL, level INTEGER NOT NULL DEFAULT 1, pods INTEGER DEFAULT 0, description TEXT, stats_json TEXT, icon_url TEXT);
    CREATE TABLE IF NOT EXISTS recipes (id INTEGER PRIMARY KEY AUTOINCREMENT, result_item_id INTEGER NOT NULL, ingredient_name TEXT NOT NULL, ingredient_item_id INTEGER, quantity INTEGER NOT NULL, UNIQUE(result_item_id, ingredient_name));
    CREATE TABLE IF NOT EXISTS drops (id INTEGER PRIMARY KEY AUTOINCREMENT, monster_name TEXT NOT NULL, item_name TEXT NOT NULL, item_id INTEGER, drop_rate REAL NOT NULL, prospecting_lock INTEGER DEFAULT 100);
    CREATE TABLE IF NOT EXISTS monsters (id INTEGER PRIMARY KEY, name TEXT NOT NULL, level_min INTEGER DEFAULT 1, level_max INTEGER DEFAULT 1, boss INTEGER DEFAULT 0, weakness TEXT, url TEXT);
    CREATE TABLE IF NOT EXISTS profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        level INTEGER DEFAULT 1,
        profession TEXT DEFAULT '',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE VIRTUAL TABLE IF NOT EXISTS items_fts USING fts5(name, type, description, content='items', content_rowid='id');
    """)
    conn.commit()
    conn.close()

app = Flask(__name__)
CORS(app)
init_db()

MOONBOT = "https://wiki.moon-bot.io/api"

# ============ PROFILE ENDPOINTS ============
@app.route("/api/profile", methods=["GET"])
def get_profile():
    conn = get_db()
    p = conn.execute("SELECT * FROM profiles ORDER BY updated_at DESC LIMIT 1").fetchone()
    conn.close()
    if not p:
        return jsonify({"name": "", "level": 1, "profession": ""})
    return jsonify(dict(p))

@app.route("/api/profile", methods=["POST"])
def save_profile():
    data = request.get_json()
    name = (data.get("name") or "").strip()
    level = int(data.get("level") or 1)
    profession = (data.get("profession") or "").strip()
    if not name:
        return jsonify({"error": "Name required"}), 400
    conn = get_db()
    conn.execute("DELETE FROM profiles")
    conn.execute("INSERT INTO profiles (name, level, profession) VALUES (?, ?, ?)",
                 (name, level, profession))
    conn.commit()
    conn.close()
    return jsonify({"status": "saved", "name": name, "level": level, "profession": profession})

# ============ SEARCH ENDPOINTS ============
@app.route("/api/search", methods=["GET"])
def search():
    query = request.args.get("q", "").strip()
    if not query: return jsonify([])
    conn = get_db()
    results = conn.execute("""
        SELECT i.id, i.name, i.type, i.level, i.icon_url
        FROM items_fts fts JOIN items i ON fts.rowid = i.id
        WHERE items_fts MATCH ? ORDER BY i.level DESC LIMIT 20
    """, (f"{query}*",)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in results])

@app.route("/api/items/<int:item_id>", methods=["GET"])
def get_item_detail(item_id):
    conn = get_db()
    item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    if not item:
        conn.close()
        return jsonify({"error": "Item not found"}), 404
    item_dict = dict(item)
    item_dict["stats"] = json.loads(item_dict["stats_json"]) if item_dict["stats_json"] else []
    drops = conn.execute("SELECT monster_name, drop_rate, icon_url FROM drops WHERE item_id = ?", (item_id,)).fetchall()
    item_dict["drops"] = [dict(d) for d in drops]
    conn.close()
    return jsonify(item_dict)

@app.route("/api/recipes/breakdown/<int:item_id>", methods=["GET"])
def recipe_breakdown(item_id):
    multiplier = int(request.args.get("qty", 1))
    conn = get_db()
    item = conn.execute("SELECT id, name, type, level FROM items WHERE id = ?", (item_id,)).fetchone()
    if not item:
        conn.close()
        return jsonify({"error": "Item not found"})
    ingredients = conn.execute("""
        SELECT r.ingredient_item_id, r.ingredient_name, r.quantity, i.name as ing_name, i.type, i.icon_url
        FROM recipes r LEFT JOIN items i ON r.ingredient_item_id = i.id WHERE r.result_item_id = ?
    """, (item_id,)).fetchall()
    raw_totals = {}
    direct_ingredients = []
    for ing in ingredients:
        qty = ing["quantity"] * multiplier
        ing_name = ing["ing_name"] or ing["ingredient_name"]
        ing_id = ing["ingredient_item_id"] or ing["ingredient_name"]
        direct_ingredients.append({"id": ing["ingredient_item_id"], "name": ing_name, "quantity": qty, "icon_url": ing["icon_url"]})
        raw_totals[ing_id] = {"id": ing["ingredient_item_id"], "name": ing_name, "quantity": qty}
    conn.close()
    return jsonify({
        "item": dict(item),
        "target_quantity": multiplier,
        "direct_ingredients": direct_ingredients,
        "raw_materials": list(raw_totals.values())
    })

# ============ MONSTER ENDPOINTS ============
@app.route("/api/monsters/search", methods=["GET"])
def search_monsters():
    query = request.args.get("q", "").strip()
    if not query: return jsonify([])
    conn = get_db()
    results = conn.execute("SELECT id, name, level_min, level_max, boss, weakness FROM monsters WHERE name LIKE ? ORDER BY level_min LIMIT 20", (f"%{query}%",)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in results])

@app.route("/api/monsters/<int:monster_id>", methods=["GET"])
def get_monster_detail(monster_id):
    conn = get_db()
    m = conn.execute("SELECT * FROM monsters WHERE id = ?", (monster_id,)).fetchone()
    if not m:
        conn.close()
        return jsonify({"error": "Monster not found"}), 404
    result = dict(m)
    try:
        res = http_requests.get(f"{MOONBOT}/monster/{monster_id}.json", timeout=8)
        if res.status_code == 200:
            detail = res.json()
            result["grades"] = detail.get("grades", [])
            result["weakness"] = detail.get("weakness", result.get("weakness", ""))
            result["boss"] = detail.get("boss", False)
            conn.execute("UPDATE monsters SET weakness=?, boss=? WHERE id=?", (result["weakness"], int(result["boss"]), monster_id))
            conn.commit()
    except:
        pass
    conn.close()
    return jsonify(result)

# ============ FARMING ENDPOINT (uses profile level by default) ============
@app.route("/api/farm/suggest", methods=["GET"])
def farm_suggest():
    # Use query param if provided, otherwise fall back to saved profile level
    level_param = request.args.get("level")
    conn = get_db()
    if level_param is None:
        profile = conn.execute("SELECT level FROM profiles ORDER BY updated_at DESC LIMIT 1").fetchone()
        level = profile["level"] if profile else 50
    else:
        level = int(level_param)
    
    monsters = conn.execute("""
        SELECT id, name, level_min, level_max, boss, weakness FROM monsters
        WHERE level_min <= ? AND level_max >= ? ORDER BY ABS((level_min + level_max) / 2 - ?) ASC LIMIT 15
    """, (level + 5, level - 5, level)).fetchall()
    items = conn.execute("""
        SELECT i.id, i.name, i.type, i.level, (SELECT COUNT(*) FROM recipes r WHERE r.result_item_id = i.id) as recipe_count
        FROM items i WHERE i.level BETWEEN ? AND ? AND i.id IN (SELECT result_item_id FROM recipes) ORDER BY i.level DESC LIMIT 15
    """, (max(1, level - 10), level + 5)).fetchall()
    conn.close()
    return jsonify({"player_level": level, "monsters": [dict(m) for m in monsters], "craftable_items": [dict(i) for i in items]})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

