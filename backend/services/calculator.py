import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "dofus.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def calculate_recipe_breakdown(item_id: int, multiplier: int = 1) -> dict:
    """Recursively computes total raw base ingredients for any craft."""
    conn = get_db_connection()
    
    item = conn.execute("SELECT id, name, type, level FROM items WHERE id = ?", (item_id,)).fetchone()
    if not item:
        conn.close()
        return {}

    ingredients = conn.execute("""
        SELECT r.ingredient_item_id, r.quantity, i.name, i.type, i.icon_url
        FROM recipes r
        JOIN items i ON r.ingredient_item_id = i.id
        WHERE r.result_item_id = ?
    """, (item_id,)).fetchall()

    raw_totals = {}
    direct_ingredients = []

    for ing in ingredients:
        qty = ing["quantity"] * multiplier
        direct_ingredients.append({
            "id": ing["ingredient_item_id"],
            "name": ing["name"],
            "quantity": qty,
            "icon_url": ing["icon_url"]
        })
        
        # Check sub-recipes recursively
        sub_breakdown = calculate_recipe_breakdown(ing["ingredient_item_id"], qty)
        if sub_breakdown.get("raw_materials"):
            for mat_id, mat_data in sub_breakdown["raw_materials"].items():
                if mat_id in raw_totals:
                    raw_totals[mat_id]["quantity"] += mat_data["quantity"]
                else:
                    raw_totals[mat_id] = mat_data
        else:
            if ing["ingredient_item_id"] in raw_totals:
                raw_totals[ing["ingredient_item_id"]]["quantity"] += qty
            else:
                raw_totals[ing["ingredient_item_id"]] = {
                    "name": ing["name"],
                    "quantity": qty
                }

    conn.close()

    return {
        "item": dict(item),
        "target_quantity": multiplier,
        "direct_ingredients": direct_ingredients,
        "raw_materials": list(raw_totals.values())
    }
