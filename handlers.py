from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import BadRequest
from scraper import searchPlayer, getInfoPlayerBoost, getRedeemCodes, getSkillsName
from fc_api_client import get_player_stats, compare_players, get_top_players, _stat_value, STAT_KEYS
from renderz_client import get_player_stats as get_player_stats_renderz
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
        "⚽️ ¡Bienvenido al bot de FC Mobile!\n\n"
        "📋 Comandos:\n"
        "🔍 /player <nombre> - Busca un jugador\n"
        "⚔️ /compare <p1> <p2> - Compara jugadores\n"
        "🏆 /top [stat] - Top 5 jugadores\n"
        "🎁 /code - Códigos de canje\n"
        "🆔 /id - ID del chat\n"
        "❓ /help - Ayuda"
    )
    await update.message.reply_text(msg)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = (
        "📋 Comandos disponibles\n\n"
        "🏠 /start - Mensaje de bienvenida\n"
        "🔍 /player <nombre> - Busca un jugador por nombre\n"
        "⚔️ /compare <p1> <p2> - Compara dos jugadores\n"
        "🏆 /top [stat] - Top 5 por OVR o stat (pace, shooting, etc.)\n"
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

def _format_player_stats(data: dict) -> str:
    """Formatea las estadísticas del jugador para Telegram (español, con emojis)."""
    if data.get("error"):
        return None
    name = data.get("name", "Desconocido")
    team = data.get("team", "")
    pos = data.get("position", "N/A")
    ovr = data.get("ovr", 0)
    pace = data.get("pace", 0)
    shooting = data.get("shooting", 0)
    passing = data.get("passing", 0)
    dribbling = data.get("dribbling", 0)
    defending = data.get("defending", 0)
    physical = data.get("physical", 0)
    lines = [
        f"👤 Nombre: {name}",
        f"🏟 Equipo: {team}" if team else None,
        "",
        "📋 Información de la carta:",
        f"#⃣ GRL: {ovr}",
        f"⚽ Posición: {pos}",
        "",
        "📊 Estadísticas:",
        f"⚡ Velocidad: {pace}",
        f"🎯 Disparo: {shooting}",
        f"⚽ Pase: {passing}",
        f"😎 Regate: {dribbling}",
        f"💥 Defensa: {defending}",
        f"💪 Físico: {physical}",
    ]
    return "\n".join(line for line in lines if line is not None)


def _fallback_player_from_scraper(name: str) -> dict | None:
    """Fallback: usa searchPlayer + getInfoPlayerBoost cuando renderz_client falla."""
    try:
        result = searchPlayer(name)
        if not result or isinstance(result, str):
            return None
        players = result if isinstance(result, list) else [result]
        if not players:
            return None
        jugador = players[0]
        asset_id = str(jugador.get("assetId") or jugador.get("playerId") or "")
        if not asset_id:
            return None
        boost = getInfoPlayerBoost(asset_id, "0")
        if not isinstance(boost, dict):
            return None
        pd = boost.get("playerData", boost)
        if isinstance(pd, dict):
            stats = pd.get("avgStats", jugador.get("avgStats", {}))
            if jugador.get("position") == "GK":
                stats = pd.get("avgGkStats", jugador.get("avgGkStats", {}))
            if not isinstance(stats, dict):
                stats = {}
            nombre = jugador.get("commonName") or f"{jugador.get('firstName', '')} {jugador.get('lastName', '')}".strip()
            return {
                "name": nombre or pd.get("commonName", "Unknown"),
                "ovr": pd.get("rating", jugador.get("rating", 0)),
                "position": jugador.get("position", pd.get("position", "N/A")),
                "pace": stats.get("avg1", 0),
                "shooting": stats.get("avg2", 0),
                "passing": stats.get("avg3", 0),
                "dribbling": stats.get("avg4", 0),
                "defending": stats.get("avg5", 0),
                "physical": stats.get("avg6", 0),
                "url": f"https://renderz.app/24/player/{asset_id}",
                "asset_id": asset_id,
            }
        return None
    except Exception:
        return None


async def player(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        name = " ".join(context.args)
        try:
            data = get_player_stats(name)
        except Exception:
            data = {"error": "connection_error"}
        if data.get("error"):
            try:
                fallback = get_player_stats_renderz(name)
                if fallback and not fallback.get("error"):
                    data = fallback
            except Exception:
                pass

        if data.get("error") == "player_not_found":
            await update.message.reply_text(
                '😕 No encontré ningún jugador con ese nombre.\n\n'
                '🔄 Intenta con otro nombre o verifica la ortografía.'
            )
            return

        if data.get("error") in ("scrape_failed", "connection_error", "timeout", "api_error", "invalid_response"):
            await update.message.reply_text(
                '⚠️ No se pudieron obtener las estadísticas.\n\n'
                '🔄 Intenta de nuevo más tarde.'
            )
            return

        msg = _format_player_stats(data)
        if msg:
            await update.message.reply_text(msg)
        else:
            await update.message.reply_text('😕 No encontré ningún jugador con ese nombre.')
    else:
        await update.message.reply_text(
            '🔍 Para buscar un jugador, escribe su nombre después del comando.\n\n'
            '📝 Ejemplo: /player Messi'
        )


async def compare_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Compare two players' statistics."""
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "Usage:\n/compare <player1> <player2>\n\n"
            "📝 Ejemplo: /compare messi ronaldo"
        )
        return
    player1_name = context.args[0]
    player2_name = " ".join(context.args[1:])
    try:
        p1, p2 = compare_players(player1_name, player2_name)
    except Exception:
        await update.message.reply_text("⚠️ Error al conectar con la API. Intenta más tarde.")
        return
    if p1.get("error"):
        await update.message.reply_text(f"😕 No encontré a '{player1_name}'.")
        return
    if p2.get("error"):
        await update.message.reply_text(f"😕 No encontré a '{player2_name}'.")
        return
    stats_order = [
        ("ovr", "#⃣ GRL"),
        ("pace", "⚡ Velocidad"),
        ("shooting", "🎯 Disparo"),
        ("passing", "⚽ Pase"),
        ("dribbling", "😎 Regate"),
        ("defending", "💥 Defensa"),
        ("physical", "💪 Físico"),
    ]
    lines = [
        "⚔️ Comparación de jugadores",
        "",
        f"👤 {p1.get('name', '?')} vs 👤 {p2.get('name', '?')}",
        "",
        "📊 Estadísticas:",
    ]
    for key, emoji_label in stats_order:
        v1 = _stat_value(p1, key)
        v2 = _stat_value(p2, key)
        s1 = str(p1.get(key, 0))
        s2 = str(p2.get(key, 0))
        if v1 > v2:
            lines.append(f"{emoji_label}: ⭐{s1} | {s2}")
        elif v2 > v1:
            lines.append(f"{emoji_label}: {s1} | ⭐{s2}")
        else:
            lines.append(f"{emoji_label}: {s1} | {s2}")
    await update.message.reply_text("\n".join(lines))


async def top_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show top 5 players by OVR or by a specific stat."""
    stat_arg = context.args[0] if context.args else None
    stat_key = STAT_KEYS.get((stat_arg or "").lower().strip(), "ovr")
    stat_label = stat_arg.title() if stat_arg and stat_key != "ovr" else "OVR"
    try:
        players = get_top_players(stat_arg)
    except Exception:
        await update.message.reply_text("⚠️ Error al conectar con la API. Intenta más tarde.")
        return
    if not players:
        await update.message.reply_text("😕 No se pudieron obtener datos de jugadores.")
        return
    lines = [f"🏆 Top 5 por {stat_label}", ""]
    medals = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
    for i, p in enumerate(players):
        name = p.get("name", "?")
        val = p.get(stat_key, 0)
        lines.append(f"{medals[i]} {name} — {val}")
    await update.message.reply_text("\n".join(lines))


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

    # Formato simple (desde /player): usa API upgrade y _format_player_stats
    if datos.get('format') == 'simple':
        asset_id = datos.get('asset_id')
        if not asset_id:
            await query.answer(text="⚠️ Error: no hay ID de jugador.", show_alert=True)
            return
        rank = int(datos.get('rank', 0))
        level = int(datos.get('level', 0))

        base_name = datos.get('base_name', 'Jugador')

        def _boost_to_format(resultado):
            pd = resultado.get('playerData', resultado)
            stats = pd.get('avgStats', pd.get('avgGkStats', {}))
            if not isinstance(stats, dict):
                stats = {}
            return {
                "name": pd.get("commonName", pd.get("cardName", base_name)),
                "ovr": pd.get("rating", 0),
                "position": pd.get("position", "N/A"),
                "pace": stats.get("avg1", 0),
                "shooting": stats.get("avg2", 0),
                "passing": stats.get("avg3", 0),
                "dribbling": stats.get("avg4", 0),
                "defending": stats.get("avg5", 0),
                "physical": stats.get("avg6", 0),
            }

        if data.startswith('rank') and not data == 'ignoreRank':
            partes = data.split('_')
            jugador_id = partes[1] if len(partes) > 1 else None
            if jugador_id:
                rango_num = partes[0][4:] if len(partes[0]) > 4 else '0'
                resultado = getInfoPlayerBoost(jugador_id, rango_num)
                if isinstance(resultado, dict):
                    fmt_data = _boost_to_format(resultado)
                    mensaje = _format_player_stats(fmt_data)
                    datos['rank'] = int(rango_num)
                    context.chat_data[msg_id] = datos
                    try:
                        await query.edit_message_text(mensaje, reply_markup=InlineKeyboardMarkup(getButtonsE(jugador_id)))
                    except BadRequest:
                        await query.answer(text="✅ Ya tienes este rango.", show_alert=True)
                else:
                    await query.answer(
                        text="⚠️ La API de RenderZ no responde (403). Las estadísticas por rango/entrenamiento no están disponibles. Intenta más tarde.",
                        show_alert=True
                    )
            return
        elif data.startswith('level') and not data == 'ignoreLevels':
            partes = data.split('_')
            jugador_id = partes[1] if len(partes) > 1 else None
            nivel_num = int(partes[0][5:]) if len(partes) > 0 and partes[0][5:].isdigit() else 0
            limites = {0: 5, 1: 10, 2: 15, 3: 20, 4: 25, 5: 30}
            if nivel_num > limites.get(rank, 0):
                await query.answer(text=f"❌ Rango {rank} permite hasta nivel {limites.get(rank, 0)}.", show_alert=True)
                return
            if jugador_id:
                resultado = getInfoPlayerBoost(jugador_id, str(rank), level=nivel_num)
                if isinstance(resultado, dict):
                    fmt_data = _boost_to_format(resultado)
                    mensaje = _format_player_stats(fmt_data)
                    datos['level'] = nivel_num
                    context.chat_data[msg_id] = datos
                    try:
                        await query.edit_message_text(mensaje, reply_markup=InlineKeyboardMarkup(getButtonsE(jugador_id)))
                    except BadRequest:
                        await query.answer(text="✅ Ya tienes este nivel.", show_alert=True)
                else:
                    await query.answer(
                        text="⚠️ La API de RenderZ no responde (403). Intenta más tarde.",
                        show_alert=True
                    )
            return
        elif data.startswith('resetAll'):
            partes = data.split('_')
            jugador_id = partes[1] if len(partes) > 1 else None
            if jugador_id:
                resultado = getInfoPlayerBoost(jugador_id, '0')
                if isinstance(resultado, dict):
                    fmt_data = _boost_to_format(resultado)
                    mensaje = _format_player_stats(fmt_data)
                    datos['rank'] = 0
                    datos['level'] = 0
                    context.chat_data[msg_id] = datos
                    await query.edit_message_text(mensaje, reply_markup=InlineKeyboardMarkup(getButtonsE(jugador_id)))
                else:
                    await query.answer(
                        text="⚠️ La API de RenderZ no responde (403). Intenta más tarde.",
                        show_alert=True
                    )
            return
        elif data.startswith('skillUnlock_') or data.startswith('skill_'):
            await query.answer(text="🪄 Las habilidades completas están en la búsqueda detallada.", show_alert=True)
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
