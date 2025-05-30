from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from scraper import searchPlayer, getInfoPlayerBoost
from str import POSICIONES_ES
from btns import getButtonsE

def construir_mensaje_y_botones(jugador, stats, grl=None):
    posicion = jugador.get('position', 'N/A')
    posicion_es = POSICIONES_ES.get(posicion, posicion)
    position2 = jugador.get('potentialPositions', [])
    playerId = jugador.get('assetId', 'N/A')
    if isinstance(position2, list):
        posiciones_secundarias_es = [POSICIONES_ES.get(pos, pos) for pos in position2]
        posiciones_secundarias_str = ', '.join(posiciones_secundarias_es) if posiciones_secundarias_es else 'N/A'
    else:
        posiciones_secundarias_str = 'N/A'
    mensaje = (
        f"*Nombre*: {jugador.get('firstName', 'Desconocido')} {jugador.get('lastName', 'Desconocido')}\n"
        f"\n"
        f"*Información de la Carta jugador*:\n"
        f"*ID*: {jugador.get('assetId', 'N/A')}\n"
        f"*GRL*: {grl if grl is not None else jugador.get('rating', 'N/A')}\n"
        f"*Posición*: {posicion_es}\n"
        f"*Pierna hábil*: {'Derecha' if jugador.get('foot', None) == 1 else 'Izquierda' if jugador.get('foot', None) == 2 else 'Desconocida'}\n"
        f"*Pierna mala*: {jugador.get('weakFoot', 'N/A')}\n"
        f"*Filigrinas*: {jugador.get('skillMovesLevel', 'N/A')}\n"
        f"*Posiciones Secundarias*: {posiciones_secundarias_str}\n"
        f"\n"
        f"*Estadísticas*:\n"
        f"*Velocidad*: {stats.get('avg1', 'N/A')}\n"
        f"*Disparo*: {stats.get('avg2', 'N/A')}\n"
        f"*Pase*: {stats.get('avg3', 'N/A')}\n"
        f"*Regate*: {stats.get('avg4', 'N/A')}\n"
        f"*Defensa*: {stats.get('avg5', 'N/A')}\n"
        f"*Físico*: {stats.get('avg6', 'N/A')}\n"
    )
    keyboard = getButtonsE(playerId)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    return mensaje, reply_markup

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Bienvenido al bot para obtener la información sobre los jugadores del juego FC Mobile, como sus estadísticas, GRL, entre otras cosas. Envía /help para ver los comandos disponibles.')

async def player(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        name = context.args[0]
        resultado = searchPlayer(name)
        if isinstance(resultado, dict) and 'players' in resultado:
            players = resultado['players']
            if players:
                primer_jugador = players[0]
                stats = primer_jugador.get('avgStats', {})
                context.user_data['jugador_original'] = primer_jugador
                mensaje, reply_markup = construir_mensaje_y_botones(primer_jugador, stats)
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
        "/player <nombre> - Busca un jugador por nombre\n"
        "/help - Muestra esta ayuda"
    )
    await update.message.reply_text(mensaje)

async def botones_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    

    jugador_original = context.user_data.get('jugador_original')
    if data.startswith('rank') and jugador_original:
        partes = data.split('_')
        rango = partes[0]
        jugador_id = partes[1] if len(partes) > 1 else None
        if jugador_id:
            resultado = getInfoPlayerBoost(jugador_id, rango[4:])
            player_data = resultado.get('playerData', {})
            stats = player_data.get('avgStats', {})
            grl = player_data.get('rating', jugador_original.get('rating', 'N/A'))
            jugador_original['rank'] = player_data.get('rank', 0)            # Actualiza el jugador original con el nuevo rango
            context.user_data['jugador_original'] = jugador_original
            mensaje, reply_markup = construir_mensaje_y_botones(jugador_original, stats, grl)
            await query.edit_message_text(mensaje, reply_markup=reply_markup, parse_mode="MarkdownV2")
        else:
            await query.edit_message_text("No se pudo obtener el id del jugador.")
    elif data.startswith('level') and jugador_original:
        partes = data.split('_')
        nivel = partes[0]
        jugador_id = partes[1] if len(partes) > 1 else None
        nivel_num = int(nivel[5:]) if nivel[5:].isdigit() else 0
        if jugador_id:
            rank = int(jugador_original.get('rank', 0))
            # Validaciones de límite según rango
            if rank == 0 and nivel_num > 5:
                print("Pop-up rango 0")
                await query.answer(
                    text=f"causa",
                    show_alert=False
                )
                return
            if rank == 1 and nivel_num > 10:
                print("Pop-up rango 1")
                await query.answer(
                    text=f"El limite máximo para entrenar al jugador en rango 1 es de 10",
                    show_alert=True
                )
                return
            if rank == 2 and nivel_num > 15:
                print("Pop-up rango 2")
                await query.answer(
                    text=f"El limite máximo para entrenar al jugador en rango 2 es de 15",
                    show_alert=True
                )
                return
            if rank == 3 and nivel_num > 20:
                print("Pop-up rango 3")
                await query.answer(
                    text=f"El limite máximo para entrenar al jugador en rango 3 es de 20",
                    show_alert=True
                )
                return
            if rank == 4 and nivel_num > 25:
                print("Pop-up rango 4")
                await query.answer(
                    text=f"El limite máximo para entrenar al jugador en rango 4 es de 25",
                    show_alert=True
                )
                return

            resultado = getInfoPlayerBoost(jugador_id, rank, level=nivel_num)
            player_data = resultado.get('playerData', {})
            stats = player_data.get('avgStats', {})
            mensaje, reply_markup = construir_mensaje_y_botones(jugador_original, stats, player_data.get('rating', 'N/A'))
            await query.edit_message_text(mensaje, reply_markup=reply_markup, parse_mode="MarkdownV2")
    elif data.startswith('resetAll') and jugador_original:
        partes = data.split('_')
        jugador_id = partes[1] if len(partes) > 1 else None
        if jugador_id:
            resultado = getInfoPlayerBoost(jugador_id, '0')
            player_data = resultado.get('playerData', {})
            stats = player_data.get('avgStats', {})
            grl = player_data.get('rating', jugador_original.get('rating', 'N/A'))

            mensaje, reply_markup = construir_mensaje_y_botones(jugador_original, stats, grl)
            await query.edit_message_text(mensaje, reply_markup=reply_markup, parse_mode="MarkdownV2")
    elif data == 'ignore':
        await query.answer(
            text="Solo es un botón decorativo.",
            show_alert=True
            )
    if True:  # Fuerza la ejecución
        print("Pop-up test")
        await query.answer(
            text="¡Esto es un pop-up de prueba!",
            show_alert=True
        )
        return