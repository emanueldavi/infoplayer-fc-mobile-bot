from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import BadRequest
from scraper import searchPlayer, getInfoPlayerBoost
from str import POSICIONES_ES, RANK_ES
from btns import getButtonsE
import re

def escape_markdown(text):
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', str(text))

def construir_mensaje_y_botones(jugador, stats, grl=None):
    posicion = jugador.get('position', 'N/A')
    posicion_es = POSICIONES_ES.get(posicion, posicion)
    rango = jugador.get('rank', 0)
    rango_es = RANK_ES.get(str(rango), rango)
    position2 = jugador.get('potentialPositions', [])
    playerId = jugador.get('assetId', 'N/A')
    if isinstance(position2, list):
        posiciones_secundarias_es = [POSICIONES_ES.get(pos, pos) for pos in position2]
        posiciones_secundarias_str = ', '.join(posiciones_secundarias_es) if posiciones_secundarias_es else 'N/A'
    else:
        posiciones_secundarias_str = 'N/A'
    # si el rango es 0, seria rango verde, si es 1, seria rango azul, etc.
    
    mensaje = (
        f"👤 *Nombre*: {escape_markdown(jugador.get('commonName', 'Desconocido'))}\n"
        f"\n"
        f"*Información de la Carta jugador*:\n"
        f"\#⃣ *GRL*: {grl if grl is not None else jugador.get('rating', 'N/A')}\n"
        f"📊 *Rango*: {rango_es}\n"
        f"⚓️ *Posición*: {posicion_es}\n"
        f"🦵🏻 *Pierna hábil*: {'Derecha' if jugador.get('foot', None) == 1 else 'Izquierda' if jugador.get('foot', None) == 2 else 'Desconocida'}\n"
        f"👣 *Pierna mala*: {jugador.get('weakFoot', 'N/A')}\n"
        f"⭐️ *Filigrinas*: {jugador.get('skillMovesLevel', 'N/A')}\n"
        f"🪄 *Posiciones Secundarias*: {posiciones_secundarias_str}\n"
        f"\n"
        f"📊 *Estadísticas*:\n"
        f"⚡️ *Velocidad*: {stats.get('avg1', 'N/A')}\n"
        f"🎯 *Disparo*: {stats.get('avg2', 'N/A')}\n"
        f"⚽️ *Pase*: {stats.get('avg3', 'N/A')}\n"
        f"💥 *Regate*: {stats.get('avg4', 'N/A')}\n"
        f"🛡 *Defensa*: {stats.get('avg5', 'N/A')}\n"
        f"💪🏻 *Físico*: {stats.get('avg6', 'N/A')}\n"
    )
    keyboard = getButtonsE(playerId)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    return mensaje, reply_markup

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Bienvenido al bot para obtener la información sobre los jugadores del juego FC Mobile, como sus estadísticas, GRL, entre otras cosas. Envía /help para ver los comandos disponibles.')

async def player(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        name = " ".join(context.args)
        resultado = searchPlayer(name)
        if isinstance(resultado, dict) and 'players' in resultado:
            players = resultado['players']
            if players:
                # Agrupar por (bindingXml, playerId) y mostrar solo el transferible si existe, si no el primero
                cartas_dict = {}
                for jugador in players:
                    binding = jugador.get('bindingXml')
                    player_id = jugador.get('playerId')
                    if not binding or not player_id:
                        continue
                    clave = (binding, player_id)
                    if clave not in cartas_dict:
                        cartas_dict[clave] = []
                    cartas_dict[clave].append(jugador)
                unicos = []
                for grupo in cartas_dict.values():
                    transferibles = [j for j in grupo if j.get('auctionable', False)]
                    if transferibles:
                        unicos.append(transferibles[0])
                    else:
                        unicos.append(grupo[0])
                # Mostrar los primeros 10 jugadores únicos como botones
                keyboard = []
                for jugador in unicos[:10]:
                    program = jugador.get('source', 'N/A').split('_')
                    program = program[1] if len(program) > 1 else program[0]
                    nombre = jugador.get('commonName')
                    if not nombre:
                        nombre = f"{jugador.get('firstName', '')} {jugador.get('lastName', '')}".strip()
                    texto = f"{POSICIONES_ES.get(jugador.get('position', 'N/A'), jugador.get('position', 'N/A'))}, {nombre}, {jugador.get('rating', 'N/A')} {program}"
                    player_asset_id = jugador.get('assetId')
                    keyboard.append([InlineKeyboardButton(texto, callback_data=f"select_{player_asset_id}")])
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    "Selecciona el jugador que buscas:",
                    reply_markup=reply_markup
                )
                context.user_data['player_search_results'] = unicos
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
            try:
                await query.edit_message_text(mensaje, reply_markup=reply_markup, parse_mode="MarkdownV2")
            except BadRequest as e:
                if "Message is not modified" in str(e):
                    await query.answer(
                        text="Ya has seleccionado este rango.",
                        show_alert=True
                    )
                    return
                else:
                    raise
        else:
            await query.edit_message_text("No se pudo obtener el id del jugador.")
    elif data.startswith('level') and jugador_original:
        partes = data.split('_')
        nivel = partes[0]
        jugador_id = partes[1] if len(partes) > 1 else None
        nivel_num = int(nivel[5:]) if nivel[5:].isdigit() else 0
        if jugador_id:
            rank = int(jugador_original.get('rank', 0))
            limites = {0: 5, 1: 10, 2: 15, 3: 20, 4: 25, 5: 30}
            limite = limites.get(rank, 0)

            if nivel_num > limite:
                await query.answer(
                text=f"❌ Seleccionaste nivel {nivel_num}, pero el rango {rank} solo permite hasta nivel {limite}.",
                show_alert=True
                        )
                return

        resultado = getInfoPlayerBoost(jugador_id, rank, level=nivel_num)
        player_data = resultado.get('playerData', {})
        stats = player_data.get('avgStats', {})
        mensaje, reply_markup = construir_mensaje_y_botones(jugador_original, stats, player_data.get('rating', 'N/A'))
        try:
            await query.edit_message_text(mensaje, reply_markup=reply_markup, parse_mode="MarkdownV2")
        except BadRequest as e:
            if "Message is not modified" in str(e):
                await query.answer(
                        text="Ya has seleccionado este nivel.",
                        show_alert=True
                )
                return
            else:
                raise
    elif data.startswith('resetAll') and jugador_original:
        partes = data.split('_')
        jugador_id = partes[1] if len(partes) > 1 else None
        if jugador_id:
            resultado = getInfoPlayerBoost(jugador_id, '0')
            player_data = resultado.get('playerData', {})
            stats = player_data.get('avgStats', {})
            grl = player_data.get('rating', jugador_original.get('rating', 'N/A'))
            jugador_original['rank'] = 0

            mensaje, reply_markup = construir_mensaje_y_botones(jugador_original, stats, grl)
        try:
            await query.edit_message_text(mensaje, reply_markup=reply_markup, parse_mode="MarkdownV2")
        except BadRequest as e:
            if "Message is not modified" in str(e):
                # No hacer nada si el mensaje no cambió
                pass
            else:
                raise    
    elif data == 'ignore':
        await query.answer(
            text="Solo es un botón decorativo.",
            show_alert=True
            )
    elif data.startswith('select_'):
        player_id = data.split('_')[1]
        players = context.user_data.get('player_search_results', [])
        jugador = next((p for p in players if str(p.get('assetId')) == player_id), None)
        if jugador:
            stats = jugador.get('avgStats', {})
            context.user_data['jugador_original'] = jugador
            mensaje, reply_markup = construir_mensaje_y_botones(jugador, stats)
            await query.edit_message_text(mensaje, reply_markup=reply_markup, parse_mode="MarkdownV2")
        else:
            await query.edit_message_text("No se pudo encontrar el jugador seleccionado.")
        return