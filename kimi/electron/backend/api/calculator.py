from flask import Blueprint, request, jsonify
from db.database import get_db

bp = Blueprint('calculator', __name__)

def get_total_resources(item_id, quantity, db, visited=None):
    """Recursively calculates total base resources needed."""
    if visited is None:
        visited = set()
        
    # Prevent infinite loops in case of circular recipes (shouldn't happen in Dofus, but safe)
    if item_id in visited:
        return []
    visited.add(item_id)
    
    resources = []
    recipe = db.execute("SELECT ingredient_id, quantity FROM recipes WHERE item_id = ?", (item_id,)).fetchall()
    
    if not recipe:
        # It's a base resource
        item = db.execute("SELECT name FROM items WHERE id = ?", (item_id,)).fetchone()
        return [{"id": item_id, "name": item['name'], "quantity": quantity}]
        
    for ing in recipe:
        needed_qty = ing['quantity'] * quantity
        # Check if ingredient has its own recipe
        sub_resources = get_total_resources(ing['ingredient_id'], needed_qty, db, visited)
        
        # Merge resources
        for sr in sub_resources:
            existing = next((r for r in resources if r['id'] == sr['id']), None)
            if existing:
                existing['quantity'] += sr['quantity']
            else:
                resources.append(sr)
                
    return resources

@bp.route('/calculate')
def calculate():
    item_id = request.args.get('item_id', type=int)
    quantity = request.args.get('quantity', 1, type=int)
    
    db = get_db()
    total = get_total_resources(item_id, quantity, db)
    db.close()
    
    # Sort by quantity descending
    total.sort(key=lambda x: x['quantity'], reverse=True)
    return jsonify({"resources": total})