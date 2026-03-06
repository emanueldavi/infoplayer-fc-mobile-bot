from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes
from telegram.error import BadRequest
from scraper import searchPlayer, getInfoPlayerBoost, getRedeemCodes, getSkillsName
from str import POSICIONES_ES, RANK_ES, WORK_ES
from btns import getButtonsE

SKILLS = {}
TOP10 = {}  # Placeholder para top10_command (se puede poblar con datos de jugadores por chat/posición)


def construir_mensaje_y_botones(jugador, stats, grl=None, skill=False):
    posicion = jugador.get('position', 'N/A')
    posicion_es = POSICIONES_ES.get(posicion, posicion)
    rango = jugador.get('rank', 0)
    rango_es = RANK_ES.get(str(rango), rango)
    position2 = jugador.get('potentialPositions', [])
    playerId = jugador.get('assetId') or jugador.get('playerId') or 'N/A'
    if isinstance(position2, list):
        posiciones_secundarias_es = [POSICIONES_ES.get(pos, pos) for pos in position2]
        posiciones_secundarias_str = ', '.join(posiciones_secundarias_es) if posiciones_secundarias_es else 'N/A'
    else:
        posiciones_secundarias_str = 'N/A'
    nombre = jugador.get('commonName', '')
    if  nombre == '':
        nombre = f"{jugador.get('firstName', '')} {jugador.get('lastName', '')}"

    if jugador.get('auctionable') and jugador.get('priceData'):
        rango_str = str(rango)
        price_info = jugador['priceData'].get(rango_str)
        if price_info and 'basePrice' in price_info:
            price = '{:,}'.format(price_info['basePrice'])
        else:
            price = '-'
    else:
        price = '🚫 Intransferible'

    if posicion == "GK":
        mensaje = (
            f"👤 Nombre: {nombre}\n\n"
            f"📋 Info de la carta:\n"
            f"#⃣ GRL: {grl if grl is not None else jugador.get('rating', 'N/A')}\n"
            f"📊 Rango: {rango_es}\n"
            f"⚓️ Posición: {posicion_es}\n"
            f"💰 Precio: {price}\n"
            f"🦵🏻 Pierna hábil: {'Derecha' if jugador.get('foot', None) == 1 else 'Izquierda' if jugador.get('foot', None) == 2 else 'Desconocida'}\n"
            f"👣 Pierna mala: {jugador.get('weakFoot', 'N/A')}\n"
            f"📏 Altura: {jugador.get('height', 'N/A')} cm\n\n"
            f"📊 Estadísticas:\n"
            f"🧤 Estirada: {stats.get('avg1', 'N/A')}\n"
            f"🎯 Colocación: {stats.get('avg2', 'N/A')}\n"
            f"⚽️ Manejo: {stats.get('avg3', 'N/A')}\n"
            f"⚡️ Reflejos: {stats.get('avg4', 'N/A')}\n"
            f"🦵🏻 Patada: {stats.get('avg5', 'N/A')}\n"
            f"💪🏻 Físico: {stats.get('avg6', 'N/A')}\n"
        )
    else:
        mensaje = (
            f"👤 Nombre: {nombre}\n\n"
            f"📋 Info de la carta:\n"
            f"#⃣ GRL: {grl if grl is not None else jugador.get('rating', 'N/A')}\n"
            f"📊 Rango: {rango_es}\n"
            f"⚓️ Posición: {posicion_es}\n"
            f"💰 Precio: {price}\n"
            f"🦵🏻 Pierna hábil: {'Derecha' if jugador.get('foot', None) == 1 else 'Izquierda' if jugador.get('foot', None) == 2 else 'Desconocida'}\n"
            f"👣 Pierna mala: {jugador.get('weakFoot', 'N/A')}\n"
            f"📏 Altura: {jugador.get('height', 'N/A')} cm\n"
            f"⭐️ Filigrinas: {jugador.get('skillMovesLevel', 'N/A')}\n"
            f"⚖️ Rendimiento ⚽️/🛡️: {WORK_ES.get(str(jugador.get('workRateAtt', 'N/A')))}/{WORK_ES.get(str(jugador.get('workRateDef', 'N/A')))}\n"
            f"🪄 Posiciones Secundarias: {posiciones_secundarias_str}\n\n"
            f"📊 Estadísticas:\n"
            f"⚡️ Velocidad: {stats.get('avg1', 'N/A')}\n"
            f"🎯 Disparo: {stats.get('avg2', 'N/A')}\n"
            f"⚽️ Pase: {stats.get('avg3', 'N/A')}\n"
            f"💥 Regate: {stats.get('avg4', 'N/A')}\n"
            f"🛡 Defensa: {stats.get('avg5', 'N/A')}\n"
            f"💪🏻 Físico: {stats.get('avg6', 'N/A')}\n"
            f"🥵 Resistencia: {stats.get('stamina', 'N/A')}\n"
        )
    keyboard = getButtonsE(playerId)
    reply_markup = InlineKeyboardMarkup(keyboard)
    return mensaje, reply_markup

def build_skill_keyboard(jugador_original, player_id):
    print(SKILLS)
    keyboard = []
    skill = jugador_original.get('skillStyleSkills', [])
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
    keyboard.append([InlineKeyboardButton("◀️ Volver", callback_data=f"backToMainMenu_{player_id}")])
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "⚽️ ¡Bienvenido! ⚽️\n\n"
        "🎮 El mejor bot de FC MOBILE en Telegram.\n\n"
        "📊 Aquí encontrarás toda la información de los jugadores:\n"
        "   • Estadísticas completas\n"
        "   • GRL y rangos\n"
        "   • Habilidades y entrenamientos\n"
        "   • Códigos de canje\n\n"
        "👉 Envía /help para ver los comandos disponibles."
    )
    await update.message.reply_text(
        msg,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🌐 Abrir Web App", web_app=WebAppInfo(url='https://mappemanuel.loca.lt/'))]])
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = (
        "📋 Comandos disponibles\n\n"
        "🏠 /start - Mensaje de bienvenida\n"
        "🔍 /player <nombre> - Busca un jugador por nombre\n"
        "🎁 /code - Códigos de canje activos\n"
        "🆔 /id - ID del chat o grupo\n"
        "❓ /help - Esta ayuda\n\n"
        "⚡ ¡Pruébalos cuando quieras!"
    )
    await update.message.reply_text(mensaje)

async def group_id(update: Update, context):
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        f"🆔 ID de este chat/grupo:\n\n📌 {chat_id}"
    )

async def player(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        name = " ".join(context.args)
        resultado = searchPlayer(name)

        # Error de conexión con la API
        if isinstance(resultado, str) and resultado.startswith('Error:'):
            await update.message.reply_text(
                '⚠️ Error al conectar con la base de datos.\n\n'
                '🔄 Intenta de nuevo en unos minutos.'
            )
            return

        # Jugadores encontrados
        if isinstance(resultado, list) and resultado:
            await showPlayer(update, context, resultado)
            return

        # No se encontraron jugadores
        await update.message.reply_text(
            '😕 No encontré ningún jugador con ese nombre.\n\n'
            '🔄 Intenta con otro nombre o verifica la ortografía.'
        )
    else:
        await update.message.reply_text(
            '🔍 Para buscar un jugador, escribe su nombre después del comando.\n\n'
            '📝 Ejemplo: /player Messi'
        )

async def top10_command(update, context):
    chat_id = update.effective_chat.id
    if not context.args:
        await update.message.reply_text("📝 Ejemplo: /top10 ST")
        return
    pos = context.args[0].upper()
    lista = TOP10.get(chat_id, {}).get(pos, [])
    if not lista:
        await update.message.reply_text(f"😕 No hay jugadores en el Top 10 de {pos}.")
        return

    mensaje = f"🏆 Top 10 {POSICIONES_ES.get(pos, pos)}\n\n"
    for idx, jugador in enumerate(lista, 1):
        nombre = jugador.get('commonName') or f"{jugador.get('firstName', '')} {jugador.get('lastName', '')}".strip()
        grl = jugador.get('rating', 'N/A')
        evento = jugador.get('source', 'N/A').split('_')
        evento = evento[1] if len(evento) > 1 else evento[0]
        pierna_mala = jugador.get('weakFoot', 'N/A')
        skills = jugador.get('skillMovesLevel', 'N/A')
        mensaje += (
            f"{idx}. {nombre} | GRL: {grl} | Skills: {skills}⭐ | Pierna mala: {pierna_mala}⭐ | Evento: {evento}\n"
        )

    await update.message.reply_text(mensaje)

async def redeemCodes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = getRedeemCodes()
    disponibles = [c for c in data if c.get("isExpired") is False]
    if disponibles:
        mensaje = "🎁 Códigos de canje activos\n\n"
        for c in disponibles:
            mensaje += (
                f"✨ {c['code']}\n"
                f"   🎯 Recompensa: {c['reward']}\n"
                f"   ⏰ Expira: {c['expired']}\n\n"
            )
        mensaje += "👇 Canjea en el enlace de abajo 👇"
        keyboard = [
            [InlineKeyboardButton("🎮 Canjear aquí", url="https://redeem.fcm.ea.com/")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(mensaje, reply_markup=reply_markup)
    else:
        mensaje = "😔 No hay códigos disponibles en este momento.\n\n"
        if data:
            ultimo = data[0]
            mensaje += (
                "📌 Último código que estuvo activo:\n\n"
                f"✨ {ultimo['code']}\n"
                f"   🎯 Recompensa: {ultimo['reward']}\n"
                f"   ⏰ Expirado: {ultimo['expired']}\n"
            )
        await update.message.reply_text(mensaje)

async def showPlayer(update, context, players, callback_prefix="select_"):
    # Agrupa y filtra jugadores únicos (igual que en player)
    cartas_dict = {}
    for jugador in players:
        binding = jugador.get('bindingXml')
        player_id = jugador.get('playerId')
        grl = jugador.get('rating')
        if not binding or not player_id:
            continue
        clave = (binding, player_id, grl)
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
    # Botones (assetId para API upgrade, fallback a playerId si no existe)
    keyboard = []
    for jugador in unicos[:10]:
        program = jugador.get('source', 'N/A').split('_')
        program = program[1] if len(program) > 1 else program[0]
        nombre = jugador.get('commonName')
        if not nombre:
            nombre = f"{jugador.get('firstName', '')} {jugador.get('lastName', '')}".strip()
        texto = f"{POSICIONES_ES.get(jugador.get('position', 'N/A'), jugador.get('position', 'N/A'))}, {nombre}, {jugador.get('rating', 'N/A')} {program}"
        player_asset_id = jugador.get('assetId') or jugador.get('playerId')
        if player_asset_id is not None:
            keyboard.append([InlineKeyboardButton(texto, callback_data=f"{callback_prefix}{player_asset_id}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = await update.message.reply_text(
        "👆 Elige el jugador que quieres ver:\n\n⚽️ Selecciona uno de los botones de abajo 👇",
        reply_markup=reply_markup
    )
    # Guarda resultados para el callback
    context.chat_data[msg.message_id] = {
        'player_search_results': unicos,
        'owner_id': update.effective_user.id,
    }
    context.user_data['player_search_results'] = unicos
    context.user_data['owner_id'] = update.effective_user.id

async def botones_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    msg_id = query.message.message_id
    chat_id = query.message.chat.id

    datos = context.chat_data.get(msg_id)
    if not datos:
        await query.answer(
            text="⛔️ Este mensaje ya no es válido o no tienes permiso para usarlo.",
            show_alert=True
        )
        return

    owner_id = datos.get('owner_id')
    if owner_id and query.from_user.id != owner_id:
        await query.answer(
            text="⛔️ Solo quien hizo la búsqueda puede usar estos botones. 🔒",
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
            if not isinstance(resultado, dict):
                await query.answer(text="⚠️ Error al obtener datos del jugador. Intenta de nuevo.", show_alert=True)
                return
            player_data = resultado.get('playerData', {})
            if jugador_original.get('position') == 'GK':
                stats = dict(player_data.get('avgGkStats', {}))
            else:
                stats = dict(player_data.get('avgStats', {}))
                stats['stamina'] = (player_data.get('stats') or {}).get('sta', 0)

            grl = player_data.get('rating', jugador_original.get('rating', 'N/A'))
            jugador_original['rank'] = player_data.get('rank', 0)
            context.user_data['jugador_original'] = jugador_original
            mensaje, reply_markup = construir_mensaje_y_botones(jugador_original, stats, grl)
            try:
                await query.edit_message_text(mensaje, reply_markup=reply_markup)
            except BadRequest as e:
                if "Message is not modified" in str(e):
                    await query.answer(
                        text="✅ Ya tienes este rango seleccionado.",
                        show_alert=True
                    )
                    return
                else:
                    raise
        else:
            await query.edit_message_text("😕 No pude obtener el ID del jugador. Intenta de nuevo.")
    elif data.startswith('level') and jugador_original:
        partes = data.split('_')
        nivel = partes[0]
        jugador_id = partes[1] if len(partes) > 1 else None
        nivel_num = int(nivel[5:]) if nivel[5:].isdigit() else 0
        rank = int(jugador_original.get('rank', 0))
        if not jugador_id:
            await query.edit_message_text("😕 No pude obtener el ID del jugador. Intenta de nuevo.")
            return
        limites = {0: 5, 1: 10, 2: 15, 3: 20, 4: 25, 5: 30}
        limite = limites.get(rank, 0)
        if nivel_num > limite:
            await query.answer(
                text=f"❌ Elegiste nivel {nivel_num}, pero el rango {rank} solo permite hasta nivel {limite}.",
                show_alert=True
            )
            return

        resultado = getInfoPlayerBoost(jugador_id, str(rank), level=nivel_num, skill=jugador_original.get('skillUpgrades', []))
        if not isinstance(resultado, dict):
            await query.answer(text="⚠️ Error al obtener datos del jugador. Intenta de nuevo.", show_alert=True)
            return
        player_data = resultado.get('playerData', {})
        if jugador_original.get('position') == 'GK':
            stats = dict(player_data.get('avgGkStats', {}))
        else:
            stats = dict(player_data.get('avgStats', {}))
            stats['stamina'] = (player_data.get('stats') or {}).get('sta', 0)

        jugador_original['level'] = nivel_num
        mensaje, reply_markup = construir_mensaje_y_botones(jugador_original, stats, player_data.get('rating', 'N/A'))
        try:
            await query.edit_message_text(mensaje, reply_markup=reply_markup)
        except BadRequest as e:
            if "Message is not modified" in str(e):
                await query.answer(
                    text="✅ Ya tienes este nivel seleccionado.",
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
            if not isinstance(resultado, dict):
                await query.answer(text="⚠️ Error al reiniciar. Intenta de nuevo.", show_alert=True)
                return
            player_data = resultado.get('playerData', {})
            if jugador_original.get('position') == 'GK':
                stats = dict(player_data.get('avgGkStats', {}))
            else:
                stats = dict(player_data.get('avgStats', {}))
                stats['stamina'] = (player_data.get('stats') or {}).get('sta', 0)

            grl = player_data.get('rating', jugador_original.get('rating', 'N/A'))
            jugador_original['rank'] = 0
            jugador_original['level'] = 0
            jugador_original['skillUpgrades'] = []
            context.user_data['jugador_original'] = jugador_original

            mensaje, reply_markup = construir_mensaje_y_botones(jugador_original, stats, grl)
            try:
                await query.edit_message_text(mensaje, reply_markup=reply_markup)
            except BadRequest as e:
                if "Message is not modified" in str(e):
                    pass
                else:
                    raise    
    elif data == 'ignoreRank':
        await query.answer(
            text="📊 Rangos disponibles:\n\n"
                "⚪️ Base | 🟢 Verde | 🔵 Azul\n"
                "🟣 Morado | 🔴 Rojo | 🟠 Naranja\n\n"
                "👆 ¡Elige el que quieras!",
            show_alert=True
        )
        return
    elif data == 'ignoreLevels':
        await query.answer(
            text="📈 Límite de entrenamiento por rango:\n\n"
                "⚪️ Base: Nivel 5\n"
                "🟢 Verde: Nivel 10\n"
                "🔵 Azul: Nivel 15\n"
                "🟣 Morado: Nivel 20\n"
                "🔴 Rojo: Nivel 25\n"
                "🟠 Naranja: Nivel 30",
            show_alert=True
        )
        return
    elif data.startswith('select_'):
        player_id = data.split('_')[1]
        players = context.user_data.get('player_search_results', [])
        jugador = next(
            (p for p in players if str(p.get('assetId')) == player_id or str(p.get('playerId')) == player_id),
            None
        )
        
        if jugador:
            # Obtener datos completos con estadísticas (la búsqueda puede no incluir avgStats)
            resultado = getInfoPlayerBoost(player_id, '0')
            if isinstance(resultado, dict):
                player_data = resultado.get('playerData', {})
                jugador = {**jugador, **player_data}
                if jugador.get('position') == 'GK':
                    stats = dict(player_data.get('avgGkStats', jugador.get('avgGkStats', {})))
                else:
                    stats = dict(player_data.get('avgStats', jugador.get('avgStats', {})))
                    stats['stamina'] = (player_data.get('stats') or {}).get('sta', (jugador.get('stats') or {}).get('sta', 0))
            else:
                if jugador.get('position') == 'GK':
                    stats = dict(jugador.get('avgGkStats', {}))
                else:
                    stats = dict(jugador.get('avgStats', {}))
                    stats['stamina'] = (jugador.get('stats') or {}).get('sta', 0)
            global SKILLS
            SKILLS = getSkillsName(jugador.get('assetId'), jugador.get('skillStyleSkills', []))
            context.user_data['jugador_original'] = jugador
            mensaje, reply_markup = construir_mensaje_y_botones(jugador, stats)
            await query.edit_message_text(mensaje, reply_markup=reply_markup)
        else:
            await query.edit_message_text("😕 No encontré ese jugador.")
        return
    elif data.startswith('skillUnlock_'):
        player_id = data.split('_')[1]
        if player_id and jugador_original:
            reply_markup = build_skill_keyboard(jugador_original, player_id)
            await query.edit_message_reply_markup(reply_markup=reply_markup)
        elif not jugador_original:
            await query.answer(text="⛔️ Primero busca un jugador con /player 🔍", show_alert=True)
        else:
            await query.edit_message_text("😕 No encontré ese jugador. Intenta con otra búsqueda.")
        return

    elif data.startswith('skill_'):
        if not jugador_original:
            await query.answer(text="⛔️ Primero busca un jugador con /player 🔍", show_alert=True)
            return
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
                            text="⚠️ Debes subir la habilidad base a nivel 3 primero. 📊",
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
                            text="⚠️ Debes subir la habilidad base a nivel 3 primero. 📊",
                            show_alert=True
                        )
                        return

            resultado = getInfoPlayerBoost(
                player_id,
                str(jugador_original.get('rank', 0)),
                jugador_original.get('level', 0),
                skill=[s for s in skills if s.get('level', 0) > 0]
            )
            if not isinstance(resultado, dict):
                await query.answer(text="⚠️ Error al actualizar habilidades. Intenta de nuevo.", show_alert=True)
                return
            try:
                player_data = resultado.get('playerData', {})
                jugador_original['skillUpgrades'] = player_data.get('skillUpgrades', [])
                if jugador_original.get('position') == 'GK':
                    stats = dict(player_data.get('avgGkStats', {}))
                else:
                    stats = dict(player_data.get('avgStats', {}))
                    stats['stamina'] = (player_data.get('stats') or {}).get('sta', 0)

                mensaje, reply_markup = construir_mensaje_y_botones(jugador_original, stats, player_data.get('rating', 'N/A'), skill=True)
                await query.edit_message_text(mensaje, reply_markup=query.message.reply_markup)
                # Actualiza el teclado de habilidades con los niveles actualizados
                reply_markup = build_skill_keyboard(jugador_original, player_id)
                await query.edit_message_reply_markup(reply_markup=reply_markup)
            except BadRequest as e:
                if "Message is not modified" in str(e):
                    await query.answer(
                        text="😕 Hubo un error al actualizar las estadísticas.",
                        show_alert=True
                    )
                    return
                else:
                    raise
            except AttributeError as e:
                if "'str' object has no attribute 'get'" in str(e):
                    if len(jugador_original.get('skillUpgrades', [])) > 0:
                        await query.answer(
                            text="✅ Ya aplicaste todas las habilidades disponibles.",
                            show_alert=True
                        )
                    else:
                        await query.answer(
                            text="⚠️ Sube de rango al jugador primero para desbloquear habilidades. 📈",
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
