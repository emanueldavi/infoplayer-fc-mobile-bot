import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = '7838284821:AAHgBQC00rYViABAaRB4VhfcxtxIa1waNjM'  # Reemplaza con tu token

def obtener_titulo(url):
    try:
        respuesta = requests.get(url)
        if respuesta.status_code == 200:
            soup = BeautifulSoup(respuesta.text, 'html.parser')
            titulo = soup.title.string if soup.title else 'Sin título'
            return titulo
        else:
            return f'Error al acceder a la página: {respuesta.status_code}'
    except Exception as e:
        return f'Error: {e}'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Envía /scrape <url> para obtener el título de una página.')

async def scrape(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        url = context.args[0]
        titulo = obtener_titulo(url)
        await update.message.reply_text(f'Título: {titulo}')
    else:
        await update.message.reply_text('Por favor, proporciona una URL. Ejemplo: /scrape https://www.example.com')

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        url = context.args[0]
        titulo = obtener_titulo(url)
        await update.message.reply_text(f'Título: {titulo}')
    else:
        await update.message.reply_text('Por favor, proporciona una URL. Ejemplo: /scrape https://www.example.com')

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('stats', stats))
    app.add_handler(CommandHandler('scrape', scrape))
    app.run_polling()