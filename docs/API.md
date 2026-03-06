# 📚 Documentación de la API interna

> Este documento describe los módulos y funciones principales del bot.

---

## 📦 Módulos

### 📄 main.py

Punto de entrada del bot. Configura la aplicación de Telegram, los handlers y el manejo de errores.

| Función | Descripción |
|---------|-------------|
| `main()` | 🚀 Inicializa y ejecuta el bot con polling |
| `error_handler()` | ⚠️ Captura excepciones y notifica al owner |
| `notificar_parada()` | 🛑 Envía mensaje cuando el bot se detiene |

---

### 📄 handlers.py

Maneja todos los comandos y callbacks del bot.

**Comandos:**

| Función | Descripción |
|---------|-------------|
| `start()` | 🏠 Mensaje de bienvenida |
| `help_command()` | ❓ Lista de comandos disponibles |
| `player()` | 🔍 Búsqueda de jugadores |
| `redeemCodes()` | 🎁 Códigos de canje activos |
| `group_id()` | 🆔 ID del chat/grupo |

**Callbacks (botones):**

| Callback | Descripción |
|----------|-------------|
| `rank0` - `rank5` | 📊 Cambio de rango |
| `level5` - `level30` | 📈 Nivel de entrenamiento |
| `skillUnlock_` | 🪄 Menú de habilidades |
| `skill_` | ⬆️ Incrementar habilidad |
| `resetAll_` | 🔄 Reiniciar a valores base |
| `backToMainMenu_` | ◀️ Volver al menú principal |

---

### 📄 scraper.py

Comunicación con la API de Renderz.app.

| Función | Descripción |
|---------|-------------|
| `searchPlayer(name)` | 🔍 Busca jugadores por nombre |
| `getInfoPlayerBoost(id, data, level, skill)` | 📊 Obtiene estadísticas con upgrades |
| `getRedeemCodes()` | 🎁 Obtiene códigos de canje activos |
| `getSkillsName(idPlayer, skills)` | 🪄 Obtiene nombres de habilidades |

---

### 📄 btns.py

Genera los teclados inline.

| Función | Descripción |
|---------|-------------|
| `getButtonsE(playerId)` | 📊 Botones de rangos, entrenamientos y habilidades |
| `getButtonsH(playerId)` | 🪄 Botones alternativos de habilidades |

---

### 📄 str.py

Constantes de traducción:

| Constante | Descripción |
|-----------|-------------|
| `POSICIONES_ES` | ⚓️ Posiciones (ST→DEL, GK→POR, etc.) |
| `RANK_ES` | 📊 Rangos (0→Base, 1→Verde, etc.) |
| `WORK_ES` | ⚖️ Rendimiento (Alto/Bajo/Medio) |
| `SKILLS` | 🪄 Nombres de habilidades de estilo |
