from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import BadRequest
from scraper import searchPlayer, getInfoPlayerBoost
from str import POSICIONES_ES, RANK_ES, SKILLS
from btns import getButtonsE
import re
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests
import os

ESCALA = 4  # Escala para mayor calidad (ajusta según lo que necesites)

def escape_markdown(text, code=False):
    """
    Escapa caracteres especiales para MarkdownV2 de Telegram.
    Si code=True, escapa todos los caracteres especiales (para monoespaciado).
    Si code=False, deja * y _ y ` sin escapar (para negrita/cursiva/monoespaciado).
    """
    if code:
        # Escapa todos los caracteres especiales para monoespaciado
        return re.sub(r'([\\`*_{}\[\]()#+\-.!|>~=])', r'\\\1', str(text))
    else:
        # Escapa todos excepto * _ ` para permitir negrita/cursiva/monoespaciado
        return re.sub(r'([\\{}\[\]()#+\-.!|>~=])', r'\\\1', str(text))

def escalar_layout(layout, escala):
    nuevo = {}
    for k, v in layout.items():
        nuevo[k] = {}
        for prop, val in v.items():
            if isinstance(val, (int, float)):
                if 'fontSize' in prop:
                    nuevo[k][prop] = int(val * escala * 1.3)  # Usa 1.3 o más para fuentes grandes
                else:
                    nuevo[k][prop] = int(val * escala)
            else:
                nuevo[k][prop] = val
    return nuevo

def construir_mensaje_y_botones(jugador, stats, grl=None, skill=False):
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
    nombre = jugador.get('commonName', '')
    if  nombre == '':
        nombre = f"{jugador.get('firstName', '')} {jugador.get('lastName', '')}"
    nombre = escape_markdown(nombre)

    if posicion == "GK":
        mensaje = (
            f"👤 *Nombre*: {nombre}\n"
            f"\n"
            f"*Información de la Carta*:\n"
            f"\#⃣ *GRL*: {grl if grl is not None else jugador.get('rating', 'N/A')}\n"
            f"📊 *Rango*: {rango_es}\n"
            f"⚓️ *Posición*: {posicion_es}\n"
            f"🦵🏻 *Pierna hábil*: {'Derecha' if jugador.get('foot', None) == 1 else 'Izquierda' if jugador.get('foot', None) == 2 else 'Desconocida'}\n"
            f"👣 *Pierna mala*: {jugador.get('weakFoot', 'N/A')}\n"
            f"📏 *Altura*: {jugador.get('height', 'N/A')}cm\n"
            f"\n"
            f"📊 *Estadísticas*:\n"
            f"🧤 *Estirada*: {stats.get('avg1', 'N/A')}\n"
            f"🎯 *Colocación*: {stats.get('avg2', 'N/A')}\n"
            f"⚽️ *Manejo*: {stats.get('avg3', 'N/A')}\n"
            f"⚡️ *Reflejos*: {stats.get('avg4', 'N/A')}\n"
            f"🦵🏻 *Patada*: {stats.get('avg5', 'N/A')}\n"
            f"💪🏻 *Físico*: {stats.get('avg6', 'N/A')}\n"
        )
    else:
        mensaje = (
            f"👤 *Nombre*: {nombre}\n"
            f"\n"
            f"*Información de la Carta*:\n"
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
            f"🥵 *Resistencia*: {stats.get('stamina', 'N/A')}\n"
        )
    keyboard = getButtonsE(playerId)
    reply_markup = InlineKeyboardMarkup(keyboard)
    return mensaje, reply_markup

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        escape_markdown(
            "_*¡Bienvenido al mejor bot de FC MOBILE en Telegram! Usando mis comandos podrás obtener la información sobre los jugadores del juego, como sus estadísticas, GRL, entre otras cosas.*_\n\n"
            "_*Envía /help para ver los comandos disponibles.*_"
        ),
        parse_mode="MarkdownV2"
    )

async def group_id(update: Update, context):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"El ID de este chat/grupo es: `{chat_id}`", parse_mode="MarkdownV2")

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
                    grl = jugador.get('rating')  # <-- Añadido
                    if not binding or not player_id:
                        continue
                    clave = (binding, player_id, grl)  # <-- Incluye el GRL en la clave
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
                msg = await update.message.reply_text(
                    "Selecciona el jugador que buscas:",
                    reply_markup=reply_markup
                )
                context.chat_data[msg.message_id] = {
                    'player_search_results': unicos,
                    'owner_id': update.effective_user.id,
                    # ...otros datos necesarios...
                }
                
                context.user_data['player_search_results'] = unicos
                context.user_data['owner_id'] = update.effective_user.id  # <--- Guarda el dueño
            else:
                await update.message.reply_text('No se encontraron jugadores con ese nombre.')
        else:
            await update.message.reply_text(escape_markdown( '_*Ha ocurrido un error, este jugador no se encuentra en los datos de FC MOBILE, por favor inténtelo nuevamente, proporcionando datos correctos.*_'), parse_mode="MarkdownV2")
    else:
        await update.message.reply_text(
            escape_markdown(
            '_*Para brindarte información, debes proporcionar el nombre del jugador a investigar.*_\n\n'
            f'_*Ejemplo:*_ `{escape_markdown('/player Jugador', code=True)}`'
            ),
            parse_mode="MarkdownV2"
        )
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
    msg_id = query.message.message_id

    datos = context.chat_data.get(msg_id)
    if not datos:
        await query.answer(
            text="⛔️ Este mensaje ya no es válido o no tienes permiso.",
            show_alert=True
        )
        return

    owner_id = datos.get('owner_id')
    if owner_id and query.from_user.id != owner_id:
        await query.answer(
            text="⛔️ Solo el usuario que generó este mensaje puede usar estos botones.",
            show_alert=True
        )
        return

    jugador_original = context.user_data.get('jugador_original')
    if data.startswith('rank') and jugador_original:
        partes = data.split('_')
        rango = partes[0]
        jugador_id = partes[1] if len(partes) > 1 else None
        if jugador_id:
            resultado = getInfoPlayerBoost(jugador_id, rango[4:])
            player_data = resultado.get('playerData', {})
            stats = player_data.get('avgStats', {})
            stats['stamina'] = player_data.get('stats', {}).get('sta', 0)

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

        resultado = getInfoPlayerBoost(jugador_id, rank, level=nivel_num, skill=jugador_original.get('skillUpgrades', []))
        jugador_original['level'] = nivel_num  # Actualiza o agrega el nivel del jugador original
        
        player_data = resultado.get('playerData', {})
        stats = player_data.get('avgStats', {})
        stats['stamina'] = player_data.get('stats', {}).get('sta', 0)

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
            jugador_original['level'] = 0  # Reiniciar nivel a 0
            jugador_original['skillUpgrades'] = []  # Reiniciar habilidades
            stats['stamina'] = player_data.get('stats', {}).get('sta', 'N/A')  # Reiniciar resistencia a 0

            mensaje, reply_markup = construir_mensaje_y_botones(jugador_original, stats, grl)
        try:
            await query.edit_message_text(mensaje, reply_markup=reply_markup, parse_mode="MarkdownV2")
        except BadRequest as e:
            if "Message is not modified" in str(e):
                # No hacer nada si el mensaje no cambió
                pass
            else:
                raise    
    elif data == 'ignoreRank':
        await query.answer(
            text="⚪️ = Rango Base\n"
                f"🟢 = Rango Verde\n"
                f"🔵 = Rango Azul\n"
                f"🟣 = Rango Morado\n"
                f"🔴 = Rango Rojo\n"
                f"🟠 = Rango Naranja\n",
            show_alert=True
        )
        return
    elif data == 'ignoreLevels':
        await query.answer(
            text="Los niveles de entrenamiento tienen límite para cada rango:\n"
                "Rango ⚪️: Nivel 5\n"
                "Rango 🟢: Nivel 10\n"
                "Rango 🔵: Nivel 15\n"
                "Rango 🟣: Nivel 20\n"
                "Rango 🔴: Nivel 25\n"
                "Rango 🟠: Nivel 30",
            show_alert=True
        )
        return
    elif data.startswith('select_'):
        player_id = data.split('_')[1]
        players = context.user_data.get('player_search_results', [])
        jugador = next((p for p in players if str(p.get('assetId')) == player_id), None)
        
        if jugador:
            if jugador.get('position') == 'GK':
                stats = jugador.get('avgGkStats', {})
            else:
                stats = jugador.get('avgStats', {})
                stats['stamina'] = jugador.get('stats', {}).get('sta', 0)
            context.user_data['jugador_original'] = jugador
            mensaje, reply_markup = construir_mensaje_y_botones(jugador, stats)
            await query.edit_message_text(mensaje, reply_markup=reply_markup, parse_mode="MarkdownV2")
        else:
            await query.edit_message_text("No se pudo encontrar el jugador seleccionado.")
        return
    elif data.startswith('skillUnlock_'):
        player_id = data.split('_')[1]
        if player_id:
            reply_markup = build_skill_keyboard(jugador_original, player_id)
            await query.edit_message_reply_markup(reply_markup=reply_markup)
        else:
            await query.edit_message_text("No se pudo encontrar el jugador seleccionado.")
        return

    elif data.startswith('skill_'):
        partes = data.split('_')
        player_id = partes[1]
        skill_id = partes[2] if len(partes) > 2 else None
        if player_id and skill_id:
            skills = jugador_original.get('skillUpgrades', [])
            all_skill_ids = set(str(s.get('id')) for s in skills if s.get('id') is not None)
            all_skill_ids.add(str(skill_id))
            primeras_tres = sorted(all_skill_ids)[:3]

            skill = next((s for s in skills if str(s.get('id')) == str(skill_id)), None)

            # Lógica para incrementar habilidades
            if skill:
                if str(skill_id) in primeras_tres:
                    if skill['level'] < 3:
                        skill['level'] += 1
                else:
                    # Solo permitir incrementar si la base tiene nivel 3
                    base_id = str(int(skill_id) - 30)
                    base_skill = next((s for s in skills if str(s.get('id')) == base_id), None)
                    if base_skill and base_skill['level'] >= 3:
                        if skill['level'] < 1:
                            skill['level'] += 1
                    else:
                        await query.answer(
                            text="Debes subir la habilidad base a nivel 3 para desbloquear esta habilidad.",
                            show_alert=True
                        )
                        return
            else:
                # Solo agregar si no existe, respetando el límite inicial
                if str(skill_id) in primeras_tres:
                    skills.append({'id': skill_id, 'level': 1})
                else:
                    # Solo permitir agregar si la base tiene nivel 3
                    base_id = str(int(skill_id) - 30)
                    base_skill = next((s for s in skills if str(s.get('id')) == base_id), None)
                    if base_skill and base_skill['level'] >= 3:
                        skills.append({'id': skill_id, 'level': 1})
                    else:
                        await query.answer(
                            text="Debes subir la habilidad base a nivel 3 para desbloquear esta habilidad.",
                            show_alert=True
                        )
                        return

            resultado = getInfoPlayerBoost(
                player_id,
                jugador_original.get('rank', 0),
                jugador_original.get('level', 0),
                skill=[s for s in skills if s.get('level', 0) > 0]  # Solo habilidades con nivel > 0
            )

            try:
                player_data = resultado.get('playerData', {})
                jugador_original['skillUpgrades'] = player_data.get('skillUpgrades', [])
                stats = player_data.get('avgStats', {})
                stats['stamina'] = player_data.get('stats', {}).get('sta', 'N/A')  # Reiniciar resistencia a 0

                mensaje, reply_markup = construir_mensaje_y_botones(jugador_original, stats, player_data.get('rating', 'N/A'), skill=True)
                await query.edit_message_text(mensaje, reply_markup=query.message.reply_markup, parse_mode="MarkdownV2")
                # Actualiza el teclado de habilidades con los niveles actualizados
                reply_markup = build_skill_keyboard(jugador_original, player_id)
                await query.edit_message_reply_markup(reply_markup=reply_markup)
            except BadRequest as e:
                if "Message is not modified" in str(e):
                    await query.answer(
                        text="Ha ocurrido un error al intentar actualizar las estadísticas del jugador.",
                        show_alert=True
                    )
                    return
                else:
                    raise
            except AttributeError as e:
                if "'str' object has no attribute 'get'" in str(e):
                    if len(jugador_original.get('skillUpgrades', [])) > 0:
                        await query.answer(
                            text="Has aplicado todas las habilidades disponibles para este jugador.",
                            show_alert=True
                        )
                    else:
                        await query.answer(
                            text="Para aplicar habilidades, primero debes subir de rango al jugador.",
                            show_alert=True
                        )
                    return
                else:
                    raise

    elif data.startswith('backToMainMenu_'):
        player_id = data.split('_')[1]
        if player_id:
            keyboard = getButtonsE(player_id)
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_reply_markup(reply_markup=reply_markup)
        else:
            return

def build_skill_keyboard(jugador_original, player_id):
    keyboard = []
    skill = jugador_original.get('skillStyleSkills', 0)
    upgrades = {str(s.get('id')): s.get('level', 0) for s in jugador_original.get('skillUpgrades', [])}
    for skills in skill:
        if skills.get('id'):
            skill_id = str(skills.get('id'))
            nivel = upgrades.get(skill_id, 0)
            texto_boton = f"{SKILLS.get(skill_id, skill_id)} ({nivel})"
            keyboard.append([
                InlineKeyboardButton(
                    texto_boton,
                    callback_data=f"skill_{player_id}_{skill_id}"
                )
            ])
    keyboard.append([InlineKeyboardButton("Volver", callback_data=f"backToMainMenu_{player_id}")])
    return InlineKeyboardMarkup(keyboard)
