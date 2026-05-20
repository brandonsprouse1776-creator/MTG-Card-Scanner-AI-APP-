import requests
import imagehash
import sqlite3
from PIL import Image
from io import BytesIO

DB = "visual_cards.db"

conn = sqlite3.connect(DB)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS visual_cards (
    id TEXT PRIMARY KEY,
    name TEXT,
    set_code TEXT,
    collector_number TEXT,
    hash TEXT
)
""")

conn.commit()

print("Downloading bulk data...")

bulk = requests.get(
    "https://api.scryfall.com/bulk-data"
).json()

oracle_url = None

for item in bulk["data"]:
    if item["type"] == "default_cards":
        oracle_url = item["download_uri"]
        break

if not oracle_url:
    print("Could not find Scryfall bulk data.")
    quit()

print("Downloading card database...")

cards = requests.get(oracle_url).json()

count = 0

for card in cards:
    try:
        if "image_uris" not in card:
            continue

        url = card["image_uris"].get("small")

        if not url:
            continue

        img_data = requests.get(url, timeout=10).content

        img = Image.open(BytesIO(img_data)).convert("RGB")

        phash = str(imagehash.phash(img))

        c.execute(
            """
            INSERT OR REPLACE INTO visual_cards
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                card["id"],
                card["name"],
                card.get("set"),
                card.get("collector_number"),
                phash
            )
        )

        count += 1

        if count % 100 == 0:
            conn.commit()
            print("Indexed", count)

    except Exception as e:
        print("ERROR", e)

conn.commit()
conn.close()

print("DONE")