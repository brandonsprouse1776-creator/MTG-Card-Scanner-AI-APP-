import requests
import sqlite3
import re

DB = "local_cards.db"

# -----------------------------
# CLEAN TEXT
# -----------------------------
def clean(text):
    text = str(text).lower()

    text = re.sub(r"[^a-z0-9 ]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# -----------------------------
# DB
# -----------------------------
conn = sqlite3.connect(DB)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS cards (
    id TEXT PRIMARY KEY,
    name TEXT,
    clean_name TEXT,
    set_code TEXT,
    collector_number TEXT,
    oracle_text TEXT,
    flavor_text TEXT,
    type_line TEXT,
    image_url TEXT
)
""")

conn.commit()

# -----------------------------
# GET BULK DATA URL
# -----------------------------
print("Downloading Scryfall bulk metadata...")

bulk = requests.get(
    "https://api.scryfall.com/bulk-data"
).json()

download_url = None

for item in bulk["data"]:
    if item["type"] == "default_cards":
        download_url = item["download_uri"]
        break

if not download_url:
    print("Could not find bulk data.")
    quit()

# -----------------------------
# DOWNLOAD ALL CARDS
# -----------------------------
print("Downloading full card database...")

cards = requests.get(download_url).json()

print("Processing cards...")

count = 0

for card in cards:
    try:
        card_id = card.get("id")

        if not card_id:
            continue

        name = card.get("name", "")
        clean_name = clean(name)

        set_code = card.get("set", "")
        collector_number = card.get("collector_number", "")

        oracle = card.get("oracle_text", "")
        flavor = card.get("flavor_text", "")
        type_line = card.get("type_line", "")

        image_url = ""

        if "image_uris" in card:
            image_url = card["image_uris"].get("normal", "")

        c.execute("""
        INSERT OR REPLACE INTO cards VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """, (
            card_id,
            name,
            clean_name,
            set_code,
            collector_number,
            oracle,
            flavor,
            type_line,
            image_url
        ))

        count += 1

        if count % 1000 == 0:
            conn.commit()
            print("Indexed", count)

    except Exception as e:
        print("ERROR", e)

conn.commit()
conn.close()

print("DONE")