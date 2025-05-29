from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from config import TOKEN
from handlers import start, player, help_command, botones_callback
import logging

# Configura el logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

async def error_handler(update, context):
    logging.error(msg="Exception while handling an update:", exc_info=context.error)
    if update and update.effective_message:
        await update.effective_message.reply_text("Ocurrió un error inesperado. Intenta de nuevo más tarde.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('player', player))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CallbackQueryHandler(botones_callback)) # Handler para los botones
    app.add_error_handler(error_handler)  # <-- Agrega esta línea
    app.run_polling()

if __name__ == '__main__':
    main()