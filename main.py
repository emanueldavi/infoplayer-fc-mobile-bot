from telegram.ext import ApplicationBuilder, filters, CommandHandler, CallbackQueryHandler, MessageHandler, ConversationHandler
from telegram import Bot
import os
from handlers import start, player , BUSCAR_JUGADOR, help_command, botones_callback, group_id, redeemCodes, top10_command, start_edit_top10, recibir_nombre_jugador, cancelar_edicion, botones_callback
import logging
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
GROUP_ID = os.getenv("GROUP_ID")


# Configura el logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('edit_top10', start_edit_top10)],
    states={
        BUSCAR_JUGADOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_nombre_jugador)],
    },
    fallbacks=[CommandHandler('cancel', cancelar_edicion)],
    allow_reentry=True,
)
async def error_handler(update, context):
    logging.error(msg="Exception while handling an update:", exc_info=context.error)
    if update and update.effective_message:
        await update.effective_message.reply_text("Ocurrió un error inesperado. Intenta de nuevo más tarde.")

def main():
    print(TOKEN)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('player', player))
    app.add_handler(CommandHandler('code', redeemCodes))
    app.add_handler(CommandHandler('id', group_id))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('top10', top10_command))
    app.add_handler(CommandHandler('edit_top10', start_edit_top10))
    app.add_handler(conv_handler)
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