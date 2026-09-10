from flask import Blueprint, request, jsonify
from db.database import get_db

bp = Blueprint('search', __name__)

@bp.route('/search')
def search_items():
    q = request.args.get('q', '')
    if not q:
        return jsonify([])
    
    db = get_db()
    # FTS5 search with prefix matching
    query = f"SELECT i.id, i.name, i.level FROM items i JOIN items_fts f ON i.id = f.rowid WHERE items_fts MATCH ? LIMIT 20"
    
    # Add wildcard for prefix matching
    results = db.execute(query, (f"{q}*",)).fetchall()
    db.close()
    
    return jsonify([dict(row) for row in results])