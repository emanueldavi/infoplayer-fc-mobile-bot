# 📝 Changelog

> Todos los cambios notables del proyecto se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y el proyecto adhiere a [Versionado Semántico](https://semver.org/lang/es/).

---

## [Sin publicar]

### ✨ Añadido

- 📚 Documentación completa de GitHub (README, CONTRIBUTING, API, DEPLOYMENT)
- 📄 Archivo `.env.example` para configuración
- 📜 Licencia MIT

### 🔄 Cambiado

- 🌎 Interfaz en español latinoamericano neutro
- 💬 Mejora de mensajes y emojis en toda la interfaz

### 🐛 Corregido

- Variable `url` indefinida en `getInfoPlayer` (scraper.py)
- Indentación en bloque `resetAll` (handlers.py)
- Valor por defecto de `skillStyleSkills` para evitar TypeError
- Paréntesis extra en mensaje de códigos de canje
- Validación de `jugador_original` en callbacks de habilidades
- Lógica frágil en `getRedeemCodes` para detección de códigos expirados
- Registro del handler de Web App
- Validación de TOKEN al iniciar

---

## [1.0.0] - Inicial

### ✨ Añadido

- 🔍 Búsqueda de jugadores por nombre
- 📊 Visualización de estadísticas completas (campo y porteros)
- 📈 Sistema de rangos (Base a Naranja)
- 📊 Niveles de entrenamiento (5-30)
- 🪄 Gestión de habilidades de estilo
- 🎁 Códigos de canje activos
- 🆔 Comando para obtener ID de chat/grupo
- 🌐 Integración con Web App
- 📢 Notificaciones al owner (errores, inicio, parada)
