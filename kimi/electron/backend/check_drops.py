import sqlite3

conn = sqlite3.connect(r"D:\CODING\dofus1overlay\data\dofus.db")
c = conn.cursor()

print("✅ Sample Drops Collected:\n")
query = """
    SELECT m.name, d.item_name, d.drop_rate 
    FROM drops d 
    JOIN monsters m ON d.monster_id = m.id 
    WHERE m.name LIKE '%Bouftou%' OR m.name LIKE '%Craqueleur%'
    ORDER BY d.drop_rate DESC
    LIMIT 8
"""

for d in c.execute(query).fetchall():
    print(f"  {d[0]} -> {d[1]} ({d[2]}%)")

conn.close()
print("\nDone!")
