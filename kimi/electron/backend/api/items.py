from flask import Blueprint, jsonify
import json
from db.database import get_db

bp = Blueprint('items', __name__)

@bp.route('/items/<int:item_id>')
def get_item(item_id):
    db = get_db()
    
    # Get item details
    item = db.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    if not item:
        return jsonify({"error": "Not found"}), 404
        
    item_dict = dict(item)
    item_dict['stats'] = json.loads(item_dict['stats_json'])
    
    # Get recipe
    recipe = db.execute("""
        SELECT r.ingredient_id, i.name as ingredient_name, r.quantity 
        FROM recipes r JOIN items i ON r.ingredient_id = i.id 
        WHERE r.item_id = ?
    """, (item_id,)).fetchall()
    
    item_dict['recipe'] = [dict(r) for r in recipe]
    
    # Get drops
    drops = db.execute("""
        SELECT m.name as monster_name, d.chance 
        FROM drops d JOIN monsters m ON d.monster_id = m.id 
        WHERE d.item_id = ?
    """, (item_id,)).fetchall()
    item_dict['drops'] = [dict(d) for d in drops]
    
    db.close()
    return jsonify(item_dict)