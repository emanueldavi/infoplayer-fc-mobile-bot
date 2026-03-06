# 🚢 Guía de despliegue

> Instrucciones para desplegar el **FC Mobile Info Bot** en diferentes plataformas.

> **🚂 Implementación actual:** El bot está desplegado en [Railway](https://railway.app).

---

## ☁️ Heroku

**1️⃣** Crear cuenta en [Heroku](https://heroku.com)

**2️⃣** Instalar Heroku CLI *(opcional)*:

```bash
# Windows (con Chocolatey)
choco install heroku-cli

# macOS
brew tap heroku/brew && brew install heroku
```

**3️⃣** Crear aplicación:

```bash
heroku create nombre-de-tu-bot
```

**4️⃣** Configurar variables de entorno:

```bash
heroku config:set TOKEN=tu_token_aqui
heroku config:set OWNER_ID=tu_telegram_id
heroku config:set GROUP_ID=id_grupo  # opcional
```

**5️⃣** Desplegar:

```bash
git push heroku main
```

**6️⃣** Escalar el worker:

```bash
heroku ps:scale worker=1
```

---

## 🚂 Railway

| Paso | Acción |
|------|--------|
| 1️⃣ | Conecta tu repositorio de GitHub a [Railway](https://railway.app) |
| 2️⃣ | Añade las variables de entorno en **Settings** |
| 3️⃣ | Configura el comando de inicio: `python main.py` |
| 4️⃣ | Railway detectará automáticamente el Procfile |

---

## 🎨 Render

| Paso | Acción |
|------|--------|
| 1️⃣ | Crea un nuevo **Background Worker** en [Render](https://render.com) |
| 2️⃣ | Conecta tu repositorio |
| 3️⃣ | Comando de inicio: `python main.py` |
| 4️⃣ | Añade las variables de entorno en **Environment** |

---

## 🐧 VPS (Linux)

**1️⃣ Instalar dependencias**

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**2️⃣ Clonar y configurar**

```bash
git clone https://github.com/tu-usuario/infoplayer-fc-mobile-bot.git
cd infoplayer-fc-mobile-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env  # Editar con tus valores
```

**3️⃣ Ejecutar con systemd** *(recomendado)*

Crear `/etc/systemd/system/fc-mobile-bot.service`:

```ini
[Unit]
Description=FC Mobile Telegram Bot
After=network.target

[Service]
Type=simple
User=tu_usuario
WorkingDirectory=/ruta/al/bot
ExecStart=/ruta/al/bot/venv/bin/python main.py
Restart=always
RestartSec=10
EnvironmentFile=/ruta/al/bot/.env

[Install]
WantedBy=multi-user.target
```

**4️⃣ Activar el servicio**

```bash
sudo systemctl daemon-reload
sudo systemctl enable fc-mobile-bot
sudo systemctl start fc-mobile-bot
sudo systemctl status fc-mobile-bot
```

---

## ⚠️ Consideraciones

| Punto | Descripción |
|-------|-------------|
| 📡 **Polling** | El bot usa polling, no webhooks. No necesitas dominio ni SSL |
| 🔐 **Token** | Mantén el `TOKEN` secreto y nunca lo subas al repositorio |
| 💰 **Heroku** | El plan gratuito tiene limitaciones; considera un plan de pago para uso continuo |
