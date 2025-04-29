from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! Send /search keyword to find offers.")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Please provide a search keyword.\nUsage: /search лазер")
        return

    keyword = context.args[0]
    try:
        conn = sqlite3.connect('messages.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT channel, product_name, price, links FROM extracted_data WHERE full_text LIKE ? LIMIT 5",
            (f"%{keyword}%",)
        )
        results = cursor.fetchall()
        conn.close()

        if results:
            reply = ""
            for channel, product_name, price, links in results:
                reply += f"📢 *{product_name}* ({channel})\n"
                if price:
                    reply += f"💰 Price: {price}\n"
                if links:
                    reply += f"🔗 {links}\n"
                reply += "\n"
            await update.message.reply_text(reply, parse_mode="Markdown")
        else:
            await update.message.reply_text("❗ No matching results found.")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {str(e)}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("search", search))

if __name__ == "__main__":
    print("PriScanBot2 is now running...")
    app.run_polling()
    

