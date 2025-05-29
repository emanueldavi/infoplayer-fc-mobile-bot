from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from scraper import searchPlayer, getInfoPlayerBoost
from config import POSICIONES_ES

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Bienvenido al bot para obtener la información sobre los jugadores del juego FC Mobile, como sus estadísticas, GRL, entre otras cosas. Envía /help para ver los comandos disponibles.')

async def player(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        name = context.args[0]
        resultado = searchPlayer(name)
        # Verifica si la respuesta es un dict y contiene resultados
        if isinstance(resultado, dict) and 'players' in resultado:
            players = resultado['players']
            if players:
                primer_jugador = players[0]
                stats = primer_jugador.get('avgStats', {})
                posicion = primer_jugador.get('position', 'N/A')
                posicion_es = POSICIONES_ES.get(posicion, posicion)
                position2 = primer_jugador.get('potentialPositions', [])
                playerId =  primer_jugador.get('assetId', 'N/A')
                if isinstance(position2, list):
                    posiciones_secundarias_es = [POSICIONES_ES.get(pos, pos) for pos in position2]
                    posiciones_secundarias_str = ', '.join(posiciones_secundarias_es) if posiciones_secundarias_es else 'N/A'
                else:
                    posiciones_secundarias_str = 'N/A'     
                mensaje = (
                    f"*Nombre*: {primer_jugador.get('firstName', 'Desconocido') + ' ' + primer_jugador.get('lastName', 'Desconocido')}\n"
                    f'\n'
                    f"*Información de la Carta jugador*:\n"
                    f"*ID*: {primer_jugador.get('assetId', 'N/A')}\n"
                    f"*GRL*: {primer_jugador.get('rating', 'N/A')}\n"
                    f"*Posición*: {posicion_es}\n"
                    f"*Pierna hábil*: {'Derecha' if primer_jugador.get('foot', None) == 1 else 'Izquierda' if primer_jugador.get('foot', None) == 2 else 'Desconocida'}\n"                    f"*Pierna mala*: {primer_jugador.get('weakFoot', 'N/A')}\n"
                    f"*Filigranas*: {primer_jugador.get('skillMovesLevel', 'N/A')}\n"
                    f"*Posiciones Segundarias*: {posiciones_secundarias_str}\n"
                    f'\n'
                    f'*Estadísticas*:\n'
                    f"*Velocidad*: {stats.get('avg1', 'N/A')}\n"
                    f"*Disparo*: {stats.get('avg2', 'N/A')}\n"
                    f"*Pase*: {stats.get('avg3', 'N/A')}\n"
                    f"*Regate*: {stats.get('avg4', 'N/A')}\n"
                    f"*Defensa*: {stats.get('avg5', 'N/A')}\n"
                    f"*Físico*: {stats.get('avg6', 'N/A')}\n"

                    )
                # Crear botón con enlace al jugador (ajusta la URL según tu necesidad)
                keyboard = [
                    [
                        InlineKeyboardButton("Rangos", callback_data='ignore'),
                    ],
                    [
                        InlineKeyboardButton("⚪️", callback_data=f'rank0_{playerId}'),
                        InlineKeyboardButton("🟢", callback_data=f'rank1_{playerId}'),
                        InlineKeyboardButton("🔵", callback_data=f'rank2_{playerId}'),
                        InlineKeyboardButton("🟣", callback_data=f'rank3_{playerId}'),
                        InlineKeyboardButton("🔴", callback_data=f'rank4_{playerId}'),
                        InlineKeyboardButton("🟠", callback_data=f'rank5_{playerId}'),                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(mensaje, reply_markup=reply_markup, parse_mode="MarkdownV2")
            else:
                await update.message.reply_text('No se encontraron jugadores con ese nombre.')
        else:
            await update.message.reply_text(f'Error en la búsqueda: {resultado}')
    else:
        await update.message.reply_text('Por favor, proporciona el nombre del jugador. Ejemplo: /player messi')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = (
        "Comandos disponibles:\n"
        "/start - Mensaje de bienvenida\n"
        "/scrape <url> - Obtiene el título de una página web\n"
        "/stats <url> - Alias de /scrape\n"
        "/player <nombre> - Busca un jugador por nombre\n"
        "/help - Muestra esta ayuda"
    )
    await update.message.reply_text(mensaje)

async def botones_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith('rank'):
        # Extrae el tipo de rango y el id del jugador
        partes = data.split('_')
        rango = partes[0]   # rank0, rank1, etc.
        jugador_id = partes[1] if len(partes) > 1 else None

        if jugador_id:
            # Aquí llamas a tu función de la API usando el id del jugador
            # Por ejemplo:
            resultado = getInfoPlayerBoost(jugador_id, rango) 
            print(resultado) # Implementa esta función según tu lógica
            await query.edit_message_text(f"Datos actualizados para el jugador {jugador_id} con rango {rango}:\n{resultado}")
        else:
            await query.edit_message_text("No se pudo obtener el id del jugador.")
    elif data == 'ignore':
        # Botón estético, no hace nada
        pass