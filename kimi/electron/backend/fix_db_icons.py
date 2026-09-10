import sqlite3
conn = sqlite3.connect(r"D:\CODING\dofus1overlay\data\dofus.db")
c = conn.cursor()

# Fix item icons that are just paths
c.execute("UPDATE items SET icon_url = 'https://wiki.moon-bot.io' || icon_url WHERE icon_url LIKE '/icons/%'")
print(f"Fixed {c.rowcount} item icon URLs")

# Fix monster icons that are just paths
c.execute("UPDATE monsters SET icon_url = 'https://wiki.moon-bot.io' || icon_url WHERE icon_url LIKE '/icons/%'")
print(f"Fixed {c.rowcount} monster icon URLs")

# Check a sample
print("\nSample Item Icons:")
for row in c.execute("SELECT name, icon_url FROM items WHERE icon_url IS NOT NULL LIMIT 3").fetchall():
    print(f"  {row[0]}: {row[1]}")

conn.commit()
conn.close()
