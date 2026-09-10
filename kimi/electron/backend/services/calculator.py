from db.database import get_db

def calculate_recipe_breakdown(item_id: int, multiplier: int = 1) -> dict:
    conn = get_db()
    item = conn.execute("SELECT id, name, type, level FROM items WHERE id = ?", (item_id,)).fetchone()
    if not item:
        conn.close()
        return {"error": "Item not found"}

    ingredients = conn.execute("""
        SELECT r.ingredient_item_id, r.ingredient_name, r.quantity, i.name as ing_name, i.type, i.icon_url
        FROM recipes r
        LEFT JOIN items i ON r.ingredient_item_id = i.id
        WHERE r.result_item_id = ?
    """, (item_id,)).fetchall()

    raw_totals = {}
    direct_ingredients = []

    for ing in ingredients:
        qty = ing["quantity"] * multiplier
        ing_name = ing["ing_name"] or ing["ingredient_name"]
        ing_id = ing["ingredient_item_id"] or ing["ingredient_name"]
        
        direct_ingredients.append({
            "id": ing["ingredient_item_id"],
            "name": ing_name,
            "quantity": qty,
            "icon_url": ing["icon_url"]
        })
        
        if isinstance(ing["ingredient_item_id"], int):
            sub_breakdown = calculate_recipe_breakdown(ing["ingredient_item_id"], qty)
            if sub_breakdown.get("raw_materials"):
                for mat in sub_breakdown["raw_materials"]:
                    mat_id = mat.get("id") or mat["name"]
                    if mat_id in raw_totals:
                        raw_totals[mat_id]["quantity"] += mat["quantity"]
                    else:
                        raw_totals[mat_id] = mat
        else:
            if ing_id in raw_totals:
                raw_totals[ing_id]["quantity"] += qty
            else:
                raw_totals[ing_id] = {
                    "id": ing["ingredient_item_id"],
                    "name": ing_name,
                    "quantity": qty
                }

    conn.close()
    return {
        "item": dict(item),
        "target_quantity": multiplier,
        "direct_ingredients": direct_ingredients,
        "raw_materials": list(raw_totals.values())
    }
