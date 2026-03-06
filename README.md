# ⚽ FC Mobile Info Bot

> Bot de Telegram para consultar información de jugadores de **FC Mobile** (EA Sports FC Mobile).  
> Obtén estadísticas, GRL, rangos, habilidades y códigos de canje directamente desde Telegram.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License">
</p>

---

## ✨ Características

| Característica | Descripción |
|----------------|-------------|
| 🔍 **Búsqueda de jugadores** | Busca cualquier jugador por nombre |
| 📊 **Estadísticas completas** | Velocidad, disparo, pase, regate, defensa, físico y resistencia |
| 📈 **Rangos y entrenamientos** | Visualiza rangos (⚪️ Base hasta 🟠 Naranja) y niveles 5-30 |
| 🪄 **Habilidades** | Consulta y gestiona las habilidades de estilo de cada jugador |
| 🎁 **Códigos de canje** | Obtén los códigos activos de FC Mobile con un solo comando |
| 🆔 **ID de chat** | Obtén el ID del chat o grupo para configuraciones |
| 🌐 **Web App** | Integración con mini aplicaciones web |
| 🌎 **Español latinoamericano** | Interfaz en español neutro y accesible |

---

## 🚀 Instalación

### 📌 Requisitos previos

- 🐍 Python 3.8 o superior
- 📱 Cuenta de Telegram
- 🤖 Token de Bot (obtenerlo con [@BotFather](https://t.me/BotFather))

### 📦 Pasos de instalación

**1️⃣ Clonar el repositorio**

```bash
git clone https://github.com/tu-usuario/infoplayer-fc-mobile-bot-main.git
cd infoplayer-fc-mobile-bot-main
```

**2️⃣ Crear entorno virtual** *(recomendado)*

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

**3️⃣ Instalar dependencias**

```bash
pip install -r requirements.txt
```

**4️⃣ Configurar variables de entorno**

```bash
cp .env.example .env
```

Edita `.env` con tus valores:

```env
TOKEN=tu_token_de_telegram
GROUP_ID=id_del_grupo_opcional
OWNER_ID=tu_telegram_id
```

---

## ⚙️ Configuración

| Variable | Descripción | Requerido |
|----------|-------------|:---------:|
| `TOKEN` | Token del bot de Telegram (obtener de @BotFather) | ✅ |
| `GROUP_ID` | ID del grupo para notificaciones de inicio/parada | ❌ |
| `OWNER_ID` | Tu ID de Telegram para recibir notificaciones de errores | ❌ |

### 🔑 Cómo obtener el ID de Telegram

1. Usa el comando `/id` del bot en el chat o grupo
2. O usa [@userinfobot](https://t.me/userinfobot) para obtener tu ID

---

## 📱 Comandos

| Comando | Descripción |
|---------|-------------|
| `/start` | 🏠 Mensaje de bienvenida e inicio del bot |
| `/player <nombre>` | 🔍 Busca un jugador por nombre *(ej: `/player Messi`)* |
| `/code` | 🎁 Muestra los códigos de canje activos |
| `/id` | 🆔 Muestra el ID del chat o grupo actual |
| `/help` | ❓ Lista todos los comandos disponibles |

---

## 🎮 Uso

### 🔍 Búsqueda de jugadores

1. Envía `/player` seguido del nombre del jugador
2. Ejemplo: `/player Haaland`
3. Selecciona el jugador de la lista si hay múltiples resultados
4. Usa los botones para explorar:
   - 📊 **Rangos** – Cambia entre Base, Verde, Azul, Morado, Rojo y Naranja
   - 📈 **Entrenamientos** – Ajusta el nivel (5-30 según el rango)
   - 🪄 **Habilidades** – Gestiona las habilidades de estilo
   - 🔄 **Reiniciar todo** – Vuelve a la configuración base

### 🎁 Códigos de canje

1. Envía `/code`
2. El bot mostrará los códigos activos con su recompensa y fecha de expiración
3. Usa el botón **"Canjear aquí"** para ir a la página de canje de EA

---

## 📁 Estructura del proyecto

```
infoplayer-fc-mobile-bot/
├── 📄 main.py           # Punto de entrada, configuración del bot
├── 📄 handlers.py       # Manejadores de comandos y callbacks
├── 📄 scraper.py        # Lógica de scraping y API (Renderz)
├── 📄 btns.py           # Definición de botones inline
├── 📄 str.py            # Traducciones y constantes (posiciones, rangos)
├── 📄 requirements.txt  # Dependencias Python
├── 📄 Procfile          # Configuración para despliegue (Railway, Heroku)
├── 📄 .env.example      # Plantilla de variables de entorno
└── 📄 README.md         # Este archivo
```

---

## 🚢 Despliegue

> **🚂 Implementación actual:** El bot está desplegado en [Railway](https://railway.app).

### ☁️ Heroku

El proyecto incluye un `Procfile` para despliegue en Heroku:

```bash
worker: python main.py
```

1. Crea una app en Heroku
2. Configura las variables de entorno en la configuración del proyecto
3. Despliega el código

### 🌐 Otras plataformas

El bot funciona con cualquier hosting que soporte Python y ejecución continua. Asegúrate de:

- ⚙️ Configurar las variables de entorno
- ▶️ Ejecutar `python main.py` como proceso persistente

> 📖 Para más detalles, consulta [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

---

## 📡 Fuentes de datos

El bot utiliza la API pública de [Renderz.app](https://renderz.app) para obtener información de jugadores de FC Mobile. Los códigos de canje se obtienen de la misma fuente.

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! 🎉

1. 🍴 Haz fork del proyecto
2. 🌿 Crea una rama para tu feature (`git checkout -b feature/nueva-funcion`)
3. 💾 Commit tus cambios (`git commit -m 'feat: Agrega nueva función'`)
4. 📤 Push a la rama (`git push origin feature/nueva-funcion`)
5. 📝 Abre un Pull Request

> 📖 Consulta [CONTRIBUTING.md](CONTRIBUTING.md) para más detalles

---

## 📄 Licencia

Este proyecto está bajo la **Licencia MIT**. Ver el archivo [LICENSE](LICENSE) para más detalles.

---

## ⚠️ Aviso legal

> Este bot **no está afiliado** con EA Sports ni con FC Mobile. Es un proyecto de la comunidad para facilitar la consulta de información del juego. Los datos provienen de fuentes públicas de terceros.
