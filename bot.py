import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import openai

# --- Setup ---
load_dotenv()  # Muat variabel dari .env

# Konfigurasi Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Inisialisasi OpenAI ---
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Fungsi Terjemahan ---
async def translate_with_gpt(text: str, source_lang: str = "Indonesian", target_lang: str = "Hungarian") -> str:
    """Menggunakan OpenAI GPT untuk terjemahan."""
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a professional translator. Translate accurately from {source_lang} to {target_lang}."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0.3  # Untuk hasil lebih konsisten
        )
        return response.choices[0].message['content']
    except Exception as e:
        logger.error(f"OpenAI Error: {str(e)}")
        return f"⚠️ Error: {str(e)}"

# --- Deteksi Bahasa ---
def detect_language(text: str) -> tuple:
    """Deteksi bahasa sederhana (ID/HU)."""
    hun_chars = {'á', 'é', 'í', 'ó', 'ö', 'ő', 'ú', 'ü', 'ű'}
    if any(char in text.lower() for char in hun_chars):
        return ("Hungarian", "Indonesian")
    return ("Indonesian", "Hungarian")

# --- Handler Telegram ---
async def start(update: Update, context):
    await update.message.reply_text(
        "🤖 **Bot Terjemahan ID-HU**\n"
        "Kirim teks dalam Bahasa Indonesia/Hungaria untuk diterjemahkan!"
    )

async def handle_message(update: Update, context):
    user_text = update.message.text
    if not user_text.strip():
        await update.message.reply_text("❌ Masukkan teks yang valid!")
        return
    
    processing_msg = await update.message.reply_text("🔄 Menerjemahkan...")
    
    src_lang, target_lang = detect_language(user_text)
    translation = await translate_with_gpt(user_text, src_lang, target_lang)
    
    await processing_msg.edit_text(
        f"🌍 **Terjemahan ({src_lang[:2]} → {target_lang[:2]}):**\n"
        f"{translation}\n\n"
        f"🔍 *Deteksi otomatis: {src_lang}*",
        parse_mode="Markdown"
    )

# --- Main ---
def main():
    bot_token = os.getenv("7933994365:AAH26fSeAKy-IaM_Z6Nab9uKGmQMtUbJtlA")
    if not bot_token:
        raise ValueError("Token Telegram tidak ditemukan di .env!")
    
    app = Application.builder().token(bot_token).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Bot berjalan...")
    app.run_polling()

if __name__ == "__main__":
    main()