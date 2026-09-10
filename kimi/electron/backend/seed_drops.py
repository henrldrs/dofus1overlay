import sqlite3
from pathlib import Path

DB_PATH = Path(r"D:\CODING\dofus1overlay\data\dofus.db")
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Ensure drops table has correct schema
c.execute("DROP TABLE IF EXISTS drops")
c.execute("""CREATE TABLE drops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    monster_id INTEGER,
    monster_name TEXT,
    item_id INTEGER,
    item_name TEXT NOT NULL,
    drop_rate REAL,
    icon_url TEXT
)""")

# Popular monster drops (curated from Dofus Retro wiki data)
drops_data = [
    # Bouftou family
    (None, "Bouftou", None, "Laine de Bouftou", 15.0),
    (None, "Bouftou", None, "Corne de Bouftou", 8.0),
    (None, "Bouftou", None, "Cuir de Bouftou", 5.0),
    (None, "Bouftou Royal", None, "Laine de Bouftou Royal", 12.0),
    (None, "Bouftou Royal", None, "Corne de Bouftou Royal", 6.0),
    (None, "Boufton Rouge", None, "Laine de Boufton", 18.0),
    (None, "Boufton Vert", None, "Laine de Boufton", 18.0),
    # Tofu family
    (None, "Tofu", None, "Plume de Tofu", 20.0),
    (None, "Tofu", None, "Oeuf de Tofu", 5.0),
    (None, "Tofu Royal", None, "Plume de Tofu Royal", 10.0),
    (None, "Tofu Maléfique", None, "Plume de Tofu Maléfique", 8.0),
    # Piou family
    (None, "Piou Rouge", None, "Plume de Piou Rouge", 25.0),
    (None, "Piou Bleu", None, "Plume de Piou Bleu", 25.0),
    (None, "Piou Vert", None, "Plume de Piou Vert", 25.0),
    (None, "Piou Jaune", None, "Plume de Piou Jaune", 25.0),
    (None, "Piou Rose", None, "Plume de Piou Rose", 25.0),
    (None, "Piou Violet", None, "Plume de Piou Violet", 25.0),
    # Craqueleur
    (None, "Craqueleur", None, "Morceau de Craqueleur", 12.0),
    (None, "Craqueleur", None, "Pierre de Craqueleur", 8.0),
    (None, "Craqueleur Légendaire", None, "Morceau de Craqueleur Légendaire", 5.0),
    # Blop family
    (None, "Blop Coco", None, "Fleur de Blop Coco", 15.0),
    (None, "Blop Griotte", None, "Fleur de Blop Griotte", 15.0),
    (None, "Blop Indigo", None, "Fleur de Blop Indigo", 15.0),
    (None, "Blop Reinette", None, "Fleur de Blop Reinette", 15.0),
    (None, "Blop Multicolore", None, "Fleur de Blop Multicolore", 8.0),
    # Gelée family
    (None, "Gelée Bleue", None, "Gelée Royale Bleue", 1.5),
    (None, "Gelée Menthe", None, "Gelée Royale Menthe", 1.5),
    (None, "Gelée Fraise", None, "Gelée Royale Fraise", 1.5),
    (None, "Gelée Citron", None, "Gelée Royale Citron", 1.5),
    # Gobelin
    (None, "Gobelin", None, "Oreille de Gobelin", 10.0),
    (None, "Gobelin", None, "Couteau de Gobelin", 3.0),
    # Arachnée
    (None, "Arachnée", None, "Patte d'Arachnée", 12.0),
    (None, "Arachnée", None, "Oeil d'Arachnée", 5.0),
    # Sanglier
    (None, "Sanglier", None, "Défense de Sanglier", 10.0),
    (None, "Sanglier", None, "Cuir de Sanglier", 8.0),
    (None, "Sanglier des Plaines", None, "Défense de Sanglier des Plaines", 8.0),
    # Ours
    (None, "Ours Brun", None, "Cuir d'Ours", 10.0),
    (None, "Ours Brun", None, "Griffe d'Ours", 6.0),
    # Loup
    (None, "Loup Blanc", None, "Croc de Loup", 8.0),
    (None, "Loup Blanc", None, "Cuir de Loup", 10.0),
    # Dragon Cochon
    (None, "Dragon Cochon", None, "Écaille de Dragon Cochon", 5.0),
    (None, "Dragon Cochon", None, "Griffe de Dragon Cochon", 3.0),
    # Kralamour
    (None, "Kralamour", None, "Tentacule de Kralamour", 10.0),
    (None, "Kralamour", None, "Encre de Kralamour", 6.0),
    # Wabbit
    (None, "Wabbit", None, "Patte de Wabbit", 12.0),
    (None, "Wabbit", None, "Oreille de Wabbit", 8.0),
    # Prespic
    (None, "Prespic", None, "Oeil de Prespic", 10.0),
    (None, "Prespic", None, "Plume de Prespic", 8.0),
    # Mulou
    (None, "Mulou", None, "Croc de Mulou", 12.0),
    (None, "Mulou", None, "Cuir de Mulou", 8.0),
    # Champod
    (None, "Champod", None, "Spore de Champod", 15.0),
    (None, "Champod", None, "Chapeau de Champod", 5.0),
]

for monster_name, item_name, drop_rate in [(d[1], d[3], d[4]) for d in drops_data]:
    # Try to link to existing monster/item IDs
    monster = c.execute("SELECT id FROM monsters WHERE LOWER(name) = LOWER(?)", (monster_name,)).fetchone()
    item = c.execute("SELECT id FROM items WHERE LOWER(name) = LOWER(?)", (item_name,)).fetchone()
    mid = monster[0] if monster else None
    iid = item[0] if item else None
    
    c.execute("INSERT INTO drops (monster_id, monster_name, item_id, item_name, drop_rate) VALUES (?, ?, ?, ?, ?)",
              (mid, monster_name, iid, item_name, drop_rate))

conn.commit()

# Verify
count = c.execute("SELECT COUNT(*) FROM drops").fetchone()[0]
print(f"✅ Seeded {count} drop entries for popular monsters!")

# Show sample
print("\nSample drops:")
for d in c.execute("SELECT monster_name, item_name, drop_rate FROM drops ORDER BY drop_rate DESC LIMIT 10").fetchall():
    print(f"  {d[0]} -> {d[1]} ({d[2]}%)")

conn.close()
