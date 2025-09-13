from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram import Bot, Update
from telegram.ext import ContextTypes
import os
from handlers import start, player , help_command, botones_callback, group_id, redeemCodes
import logging
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
GROUP_ID = os.getenv("GROUP_ID")

# Configura el logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

async def error_handler(update, context):
    logging.error(msg="Exception while handling an update:", exc_info=context.error)
    
    # Notificar al creador del error
    bot = Bot(TOKEN)
    try:
        owner_id = os.getenv('OWNER_ID')
        if owner_id:
            error_msg = f"❌ Error en el bot:\n{str(context.error)}"
            await bot.send_message(chat_id=owner_id, text=error_msg)
    except Exception as e:
        print(f"Error enviando notificación de error al creador: {e}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text("Ocurrió un error inesperado. Intenta de nuevo más tarde.")

async def notificar_parada():
    """Notifica al creador cuando el bot se detiene"""
    bot = Bot(TOKEN)
    try:
        owner_id = os.getenv('OWNER_ID')
        if owner_id:
            await bot.send_message(chat_id=owner_id, text="🛑 El bot se ha detenido.")
        if GROUP_ID:
            await bot.send_message(chat_id=GROUP_ID, text="🛑 El bot se ha detenido.")
    except Exception as e:
        print(f"Error enviando mensaje de parada al creador: {e}")

async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.effective_message.web_app_data.data
    user = update.effective_user
    print(update)
    # Aquí puedes procesar los datos recibidos desde la mini app
    print(f"Datos recibidos de la mini app: {data}")
    await update.effective_message.reply_text(
        f"¡Recibido desde la mini app!\nUsuario: {user.first_name}\nDatos: {data}"
    )

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('player', player))
    app.add_handler(CommandHandler('code', redeemCodes))
    app.add_handler(CommandHandler('id', group_id))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CallbackQueryHandler(botones_callback))
    app.add_error_handler(error_handler)

    # Enviar mensaje al creador al iniciar
    async def notificar_creador():
        bot = Bot(TOKEN)
        try:
            owner_id = os.getenv('OWNER_ID')
            if owner_id:
                await bot.send_message(chat_id=owner_id, text="✅ El bot se ha iniciado correctamente.")
            if GROUP_ID:
                await bot.send_message(chat_id=GROUP_ID, text="✅ El bot se ha iniciado correctamente.")
        except Exception as e:
            print(f"Error enviando mensaje al creador: {e}")

    # Función para inicializar el bot
    async def post_init(application):
        await notificar_creador()

    # Función para cuando el bot se cierra
    async def post_shutdown(application):
        await notificar_parada()

    # Configurar post_init y post_shutdown
    app.post_init = post_init
    app.post_shutdown = post_shutdown
    
    print("🤖 Iniciando bot...")
    
    try:
        app.run_polling()
    except KeyboardInterrupt:
        print("🛑 Bot detenido por el usuario")
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        # Notificar error crítico
        import asyncio
        asyncio.run(notificar_parada())
    

if __name__ == '__main__':
    main()
