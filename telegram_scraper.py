from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
import sqlite3
import os
from dotenv import load_dotenv
import re
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
load_dotenv()
api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")
phone = os.getenv("TELEGRAM_PHONE")

# Create or connect to SQLite database
conn = sqlite3.connect("messages.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS extracted_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel TEXT,
    product_name TEXT,
    price TEXT,
    links TEXT,
    full_text TEXT
)
""")
conn.commit()

# Helper functions
def extract_links(text):
    return ", ".join(re.findall(r'https?://\S+', text))

def extract_price(text):
    match = re.search(r'(\d+[.,]?\d*)\s*(AED|USD|EUR|руб|₽|dirham|dhs|dollars?)', text, re.IGNORECASE)
    return match.group() if match else None

def extract_product_name(text):
    lines = text.split("\n")
    return lines[0][:100] if lines else "Unknown"

# Main logic
async def main():
    logging.info("🔄 Starting scheduled scrape task")
    async with TelegramClient("user_session", api_id, api_hash) as client:
        channels = [
            "@news_kosmetolog",
            "@cosmetology_namo",
            "@kosmetologmed",
            "@aynastudy",
            "@cosmetolog_forum",
            "@kosmetolog",
            "@dr_stashevich",
            "@skindeals",
            "@beautyclinic"
        ]

        for target_channel in channels:
            logging.info(f"📡 Scraping: {target_channel}")
            try:
                entity = await client.get_entity(target_channel)
                history = await client(GetHistoryRequest(
                    peer=entity,
                    limit=20,
                    offset_date=None,
                    offset_id=0,
                    max_id=0,
                    min_id=0,
                    add_offset=0,
                    hash=0
                ))

                for msg in history.messages:
                    if msg.message:
                        full_text = msg.message
                        product_name = extract_product_name(full_text)
                        price = extract_price(full_text)
                        links = extract_links(full_text)

                        cursor.execute("""
                            INSERT INTO extracted_data (channel, product_name, price, links, full_text)
                            VALUES (?, ?, ?, ?, ?)
                        """, (target_channel, product_name, price, links, full_text))
                        conn.commit()

                logging.info(f"✅ Done scraping: {target_channel}")

            except Exception as e:
                logging.error(f"❌ Failed to scrape {target_channel}: {e}")

    logging.info("✅ All channels scanned and data saved.")
    conn.close()

# Run it
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
