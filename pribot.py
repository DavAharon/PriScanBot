import os
import sqlite3
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
from telegram.request import HTTPXRequest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! I'm PriScanBot 2.0 and I'm active!")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

if __name__ == "__main__":
    app.run_polling()
    
# Search messages.db
def search_messages(keyword):
    conn = sqlite3.connect("messages.db")
    cursor = conn.cursor()
    query = """
        SELECT product_name, price, links
        FROM extracted_data
        WHERE full_text LIKE ?
        ORDER BY id DESC
        LIMIT 3
    """
    cursor.execute(query, (f"%{keyword}%",))
    results = cursor.fetchall()
    conn.close()

    if not results:
        return "❌ No results found."
    
    reply = ""
    for product, price, links in results:
        reply += f"🧴 {product}\n💰 {price or 'N/A'}\n🔗 {links or '—'}\n\n"
    return reply

# /search handler
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /search <keyword>")
        return
    keyword = " ".join(context.args)
    result = search_messages(keyword)
    await update.message.reply_text(result)

# Setup and run bot
request = HTTPXRequest(connect_timeout=30, read_timeout=30)
app = ApplicationBuilder().token(BOT_TOKEN).request(request).build()
app.add_handler(CommandHandler("search", search))
print("🤖 PriScanBot2 is now running...")
app.run_polling()
