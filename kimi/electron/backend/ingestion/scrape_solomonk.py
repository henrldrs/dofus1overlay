import cloudscraper
import sqlite3
import json
import time
import re
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin

DB_PATH = Path(r"D:\CODING\dofus1overlay\data\dofus.db")
SOLOMONK_BASE = "https://solomonk.fr"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def fetch_page(url):
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )
    try:
        response = scraper.get(url, timeout=20)
        if response.status_code == 200:
            return response.text
        print(f"HTTP {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    return None

def parse_monster_page(html, monster_name):
    soup = BeautifulSoup(html, 'lxml')
    drops = []
    
    # Look for tables that contain "%" (drop rate indicator)
    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all(['td', 'th'])
            if len(cols) >= 2:
                text = row.get_text(separator=' ', strip=True)
                if '%' in text:
                    try:
                        item_col = cols[0]
                        item_name = item_col.get_text(strip=True)
                        
                        rate_col = cols[-1]
                        rate_text = rate_col.get_text(strip=True)
                        
                        drop_rate = None
                        match = re.search(r'([\d\.]+)\s*%', rate_text)
                        if match:
                            drop_rate = float(match.group(1))
                        
                        if item_name and len(item_name) > 2 and item_name.lower() not in ['objet', 'item', 'butin', 'drop', 'récompense']:
                            drops.append({'item_name': item_name, 'drop_rate': drop_rate})
                    except Exception:
                        pass
    
    # Try to find monster icon
    icon_url = None
    img = soup.find('img', src=lambda x: x and ('monster' in x.lower() or 'monstre' in x.lower() or 'creature' in x.lower()))
    if not img:
        header = soup.find('div', class_=lambda x: x and 'header' in x.lower())
        if header:
            img = header.find('img')
    
    if img and img.get('src'):
        icon_url = urljoin(SOLOMONK_BASE, img['src'])
    else:
        safe_name = monster_name.lower().replace(' ', '-').replace('é', 'e').replace('è', 'e').replace('ê', 'e')
        icon_url = f"{SOLOMONK_BASE}/images/monstres/{safe_name}.png"
    
    return drops, icon_url

def run_scraper():
    print("=" * 60)
    print("  SOLOMONK DROP TABLE SCRAPER (Cloudflare Bypass)")
    print("=" * 60)
    conn = get_db()
    cursor = conn.cursor()
    
    monsters = cursor.execute("SELECT id, name, url FROM monsters WHERE url IS NOT NULL AND url != ''").fetchall()
    if not monsters:
        print(" No monsters with URLs found!")
        conn.close()
        return
    
    print(f"\n Found {len(monsters)} monsters to scrape\n")
    
    # FIX: Drop and recreate the drops table to ensure correct schema
    print(" Resetting drops table schema...")
    cursor.execute("DROP TABLE IF EXISTS drops")
    cursor.execute("""CREATE TABLE drops (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        monster_id INTEGER, 
        monster_name TEXT,
        item_id INTEGER, 
        item_name TEXT NOT NULL, 
        drop_rate REAL, 
        icon_url TEXT,
        FOREIGN KEY (monster_id) REFERENCES monsters(id), 
        FOREIGN KEY (item_id) REFERENCES items(id)
    )""")
    conn.commit()
    
    # Add icon_url to monsters if missing
    try:
        cursor.execute("ALTER TABLE monsters ADD COLUMN icon_url TEXT")
        conn.commit()
    except:
        pass
    
    total_drops = 0
    scraped = 0
    
    for monster in monsters:
        mid, mname, murl = monster['id'], monster['name'], monster['url']
        if not murl.startswith('http'):
            murl = urljoin(SOLOMONK_BASE, murl)
        
        print(f"  [{scraped+1}/{len(monsters)}] {mname}...", end=' ', flush=True)
        
        html = fetch_page(murl)
        if not html or "Security check" in html or "Attention" in html:
            print(" Blocked by Cloudflare")
            scraped += 1
            time.sleep(5) # Back off if blocked
            continue
            
        drops, icon_url = parse_monster_page(html, mname)
        
        if icon_url:
            cursor.execute("UPDATE monsters SET icon_url = ? WHERE id = ?", (icon_url, mid))
            conn.commit()
            
        if drops:
            for drop in drops:
                item = cursor.execute("SELECT id FROM items WHERE LOWER(name) = LOWER(?)", (drop['item_name'],)).fetchone()
                item_id = item['id'] if item else None
                cursor.execute("INSERT INTO drops (monster_id, monster_name, item_id, item_name, drop_rate, icon_url) VALUES (?, ?, ?, ?, ?, ?)",
                    (mid, mname, item_id, drop['item_name'], drop['drop_rate'], icon_url))
                total_drops += 1
            conn.commit()
            print(f"OK ({len(drops)} drops)")
        else:
            print("OK (0 drops)")
            
        scraped += 1
        time.sleep(1.5) # Be polite to the server
        
    conn.close()
    print(f"\n{'='*60}")
    print(f"  COMPLETE! {scraped} monsters processed, {total_drops} total drops collected")
    print(f"{'='*60}")

if __name__ == "__main__":
    run_scraper()
