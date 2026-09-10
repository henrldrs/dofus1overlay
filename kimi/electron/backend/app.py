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
    CREATE TABLE IF NOT EXISTS monsters (id INTEGER PRIMARY KEY, name TEXT NOT NULL, level_min INTEGER DEFAULT 1, level_max INTEGER DEFAULT 1, boss INTEGER DEFAULT 0, weakness TEXT, url TEXT, icon_url TEXT);
    CREATE TABLE IF NOT EXISTS profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name TEXT NOT NULL, 
        level INTEGER DEFAULT 1, 
        profession TEXT DEFAULT '',
        strength INTEGER DEFAULT 0,
        intelligence INTEGER DEFAULT 0,
        agility INTEGER DEFAULT 0,
        chance INTEGER DEFAULT 0,
        vitality INTEGER DEFAULT 0,
        wisdom INTEGER DEFAULT 0,
        prospecting INTEGER DEFAULT 100,
        main_element TEXT DEFAULT 'neutral',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS drops (id INTEGER PRIMARY KEY AUTOINCREMENT, monster_id INTEGER, monster_name TEXT, item_id INTEGER, item_name TEXT NOT NULL, drop_rate REAL, icon_url TEXT);
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
        return jsonify({"name": "", "level": 1, "profession": "", "strength": 0, "intelligence": 0, "agility": 0, "chance": 0, "vitality": 0, "wisdom": 0, "prospecting": 100, "main_element": "neutral"})
    return jsonify(dict(p))

@app.route("/api/profile", methods=["POST"])
def save_profile():
    data = request.get_json()
    name = (data.get("name") or "").strip()
    level = int(data.get("level") or 1)
    profession = (data.get("profession") or "").strip()
    strength = int(data.get("strength") or 0)
    intelligence = int(data.get("intelligence") or 0)
    agility = int(data.get("agility") or 0)
    chance = int(data.get("chance") or 0)
    vitality = int(data.get("vitality") or 0)
    wisdom = int(data.get("wisdom") or 0)
    prospecting = int(data.get("prospecting") or 100)
    main_element = (data.get("main_element") or "neutral").strip()
    
    if not name:
        return jsonify({"error": "Name required"}), 400
    
    conn = get_db()
    conn.execute("DELETE FROM profiles")
    conn.execute("""INSERT INTO profiles (name, level, profession, strength, intelligence, agility, chance, vitality, wisdom, prospecting, main_element) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                 (name, level, profession, strength, intelligence, agility, chance, vitality, wisdom, prospecting, main_element))
    conn.commit()
    conn.close()
    return jsonify({"status": "saved", "name": name})

# ============ SEARCH ENDPOINTS ============
@app.route("/api/search", methods=["GET"])
def search():
    query = request.args.get("q", "").strip()
    item_type = request.args.get("type", "").strip()
    min_level = int(request.args.get("min_level") or 0)
    max_level = int(request.args.get("max_level") or 200)
    
    if not query:
        return jsonify([])
    
    conn = get_db()
    
    # Build dynamic query with filters
    base_query = """
        SELECT i.id, i.name, i.type, i.level, i.icon_url
        FROM items_fts fts JOIN items i ON fts.rowid = i.id
        WHERE items_fts MATCH ?
    """
    params = [f"{query}*"]
    
    if item_type:
        base_query += " AND i.type = ?"
        params.append(item_type)
    
    base_query += " AND i.level BETWEEN ? AND ?"
    params.extend([min_level, max_level])
    
    base_query += " ORDER BY i.level DESC LIMIT 30"
    
    results = conn.execute(base_query, params).fetchall()
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
    
    drops = conn.execute("""
        SELECT DISTINCT monster_id, monster_name, drop_rate, icon_url as monster_icon
        FROM drops 
        WHERE item_id = ? OR LOWER(item_name) = LOWER(?)
        ORDER BY drop_rate DESC
    """, (item_id, item_dict["name"])).fetchall()
    item_dict["drops"] = [dict(d) for d in drops]
    
    conn.close()
    return jsonify(item_dict)

@app.route("/api/recipes/breakdown/<int:item_id>", methods=["GET"])
def recipe_breakdown(item_id):
    multiplier = int(request.args.get("qty", 1))
    conn = get_db()
    item = conn.execute("SELECT id, name, type, level, icon_url FROM items WHERE id = ?", (item_id,)).fetchone()
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
    return jsonify({"item": dict(item), "target_quantity": multiplier, "direct_ingredients": direct_ingredients, "raw_materials": list(raw_totals.values())})

# ============ MONSTER ENDPOINTS ============
@app.route("/api/monsters/search", methods=["GET"])
def search_monsters():
    query = request.args.get("q", "").strip()
    min_level = int(request.args.get("min_level") or 0)
    max_level = int(request.args.get("max_level") or 200)
    weakness = request.args.get("weakness", "").strip()
    
    if not query:
        return jsonify([])
    
    conn = get_db()
    base_query = "SELECT id, name, level_min, level_max, boss, weakness, icon_url FROM monsters WHERE name LIKE ?"
    params = [f"%{query}%"]
    
    if min_level > 0 or max_level < 200:
        base_query += " AND level_min >= ? AND level_max <= ?"
        params.extend([min_level, max_level])
    
    if weakness:
        base_query += " AND LOWER(weakness) = LOWER(?)"
        params.append(weakness)
    
    base_query += " ORDER BY level_min LIMIT 30"
    
    results = conn.execute(base_query, params).fetchall()
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
    
    drops = conn.execute("""
        SELECT item_id, item_name, drop_rate, icon_url
        FROM drops WHERE monster_id = ? ORDER BY drop_rate DESC
    """, (monster_id,)).fetchall()
    result["drops"] = [dict(d) for d in drops]
    
    # Fetch live data from Moonbot
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

# ============ DROP ENDPOINTS ============
@app.route("/api/drops/monster/<int:monster_id>", methods=["GET"])
def get_monster_drops(monster_id):
    conn = get_db()
    drops = conn.execute("SELECT item_id, item_name, drop_rate, icon_url FROM drops WHERE monster_id = ? ORDER BY drop_rate DESC", (monster_id,)).fetchall()
    conn.close()
    return jsonify([dict(d) for d in drops])

@app.route("/api/drops/item/<int:item_id>", methods=["GET"])
def get_item_drops(item_id):
    conn = get_db()
    drops = conn.execute("""
        SELECT DISTINCT monster_id, monster_name, drop_rate, icon_url as monster_icon
        FROM drops WHERE item_id = ? ORDER BY drop_rate DESC
    """, (item_id,)).fetchall()
    conn.close()
    return jsonify([dict(d) for d in drops])

# ============ FARMING ENDPOINT (Element-based recommendations) ============
@app.route("/api/farm/suggest", methods=["GET"])
def farm_suggest():
    level_param = request.args.get("level")
    element = request.args.get("element", "").strip()
    conn = get_db()
    
    if level_param is None:
        profile = conn.execute("SELECT level, main_element FROM profiles ORDER BY updated_at DESC LIMIT 1").fetchone()
        level = profile["level"] if profile else 50
        if not element and profile:
            element = profile.get("main_element", "")
    else:
        level = int(level_param)
    
    # Base query for monsters
    base_query = """
        SELECT id, name, level_min, level_max, boss, weakness, icon_url 
        FROM monsters WHERE level_min <= ? AND level_max >= ?
    """
    params = [level + 5, level - 5]
    
    # Filter by element weakness if specified
    if element and element.lower() != "neutral":
        base_query += " AND LOWER(weakness) = LOWER(?)"
        params.append(element)
    
    base_query += " ORDER BY ABS((level_min + level_max) / 2 - ?) ASC LIMIT 20"
    params.append(level)
    
    monsters = conn.execute(base_query, params).fetchall()
    
    items = conn.execute("""
        SELECT i.id, i.name, i.type, i.level, i.icon_url, (SELECT COUNT(*) FROM recipes r WHERE r.result_item_id = i.id) as recipe_count
        FROM items i WHERE i.level BETWEEN ? AND ? AND i.id IN (SELECT result_item_id FROM recipes) ORDER BY i.level DESC LIMIT 20
    """, (max(1, level - 10), level + 5)).fetchall()
    
    conn.close()
    return jsonify({"player_level": level, "element": element, "monsters": [dict(m) for m in monsters], "craftable_items": [dict(i) for i in items]})

# ============ ITEM TYPES (for filtering) ============
@app.route("/api/types", methods=["GET"])
def get_types():
    conn = get_db()
    types = conn.execute("SELECT DISTINCT type FROM items ORDER BY type").fetchall()
    conn.close()
    return jsonify([t["type"] for t in types])

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
