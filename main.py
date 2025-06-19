from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from telegram import Bot
import os
from handlers import start, player , help_command, botones_callback, group_id
import logging

TOKEN = os.getenv("TOKEN")
GROUP_ID = os.getenv("GROUP_ID")

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
    app.add_handler(CommandHandler('id', group_id))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CallbackQueryHandler(botones_callback))
    app.add_error_handler(error_handler)

    # Enviar mensaje al creador al iniciar
    async def notificar_creador(chat_id=None):
        bot = Bot(TOKEN)
        try:
            if chat_id is None:
                chat_id = os.getenv('OWNER_ID')
            await bot.send_message(chat_id=chat_id , text="✅ El bot se ha iniciado correctamente.")
        except Exception as e:
            print(f"Error enviando mensaje al creador: {e}")

    import asyncio
    asyncio.get_event_loop().run_until_complete(notificar_creador())
    asyncio.get_event_loop().run_until_complete(notificar_creador(GROUP_ID))

    app.run_polling()
    

if __name__ == '__main__':
    main()