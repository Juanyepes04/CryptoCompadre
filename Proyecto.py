import sqlite3
import telebot
import requests
from Token import TELEGRAM_TOKEN


# =========================================================
#                 CLASE PRINCIPAL DEL BOT
# =========================================================
class CryptoCompadre_Bot:

    def __init__(self, TELEGRAM_TOKEN):
        self.bot = telebot.TeleBot(TELEGRAM_TOKEN)
        self.responder_comando()

    # --- MENSAJE DE BIENVENIDA ---
    def bienvenida_a_usuario(self, message):
        self.bot.reply_to(
            message,
            "👋 ¡Bienvenido al *Bot CriptoCompadre*! 🚀\n\n"
            "Puedo ayudarte con información del mercado cripto.\n"
            "Usa estos comandos:\n"
            "• /precio [símbolo] → ver precio (ej: /precio BTC)\n"
            "• /top → ver top 5 criptos\n"
            "• /convertir → convierte tus criptos en la moneda que tu quieras\n"
            "¿Qué quieres hacer, compadre?",
            parse_mode="Markdown")

    def obtener_id_desde_simbolo(self, simbolo):
        """Devuelve el ID de CoinGecko a partir del símbolo (btc -> bitcoin)."""
        simbolo = simbolo.lower().strip()
        url = "https://api.coingecko.com/api/v3/search"
        r = requests.get(url, params={"query": simbolo}, timeout=10)
        r.raise_for_status()
        resultados = r.json().get("coins", [])
        for coin in resultados:
            if coin["symbol"].lower() == simbolo:
                return coin["id"]
        return None

    # --- REGISTRO DE COMANDOS ---
    def responder_comando(self):
        # 🔹 Primero, comandos personalizados
        self.comando_top()
        self.comando_precio()
        self.comando_convertir()

        @self.bot.message_handler(commands=["start", "inicio"])
        def responder_a_comandos(message):
            self.bienvenida_a_usuario(message)

        # 🔹 Luego, manejador genérico de texto
        @self.bot.message_handler(func=lambda m: isinstance(m.text, str) and not m.text.startswith('/'))
        def responder_mensajes_texto(message):
            self.bot_mensajes_texto(message)

    # =====================================================
    #                COMANDOS PERSONALIZADOS
    # =====================================================

    # --- COMANDO /PRECIO ---
    def comando_precio(self):
        @self.bot.message_handler(commands=["precio"])
        def obtener_precio(message):
            try:
                partes = message.text.split()
                if len(partes) < 2:
                    self.bot.reply_to(message, "Uso correcto: /precio BTC")
                    return

                simbolo = partes[1].lower().strip()
                id_cripto = self.obtener_id_desde_simbolo(simbolo)

                if not id_cripto:
                    self.bot.reply_to(message, "❌ No encontré esa criptomoneda en CoinGecko.")
                    return

                url = "https://api.coingecko.com/api/v3/simple/price"
                params = {"ids": id_cripto, "vs_currencies": "usd,cop", "include_24hr_change": "true"}
                data = requests.get(url, params=params, timeout=10).json()

                info = data.get(id_cripto)
                if not info:
                    self.bot.reply_to(message, "⚠️ No pude obtener el precio. Intenta más tarde.")
                    return

                precio_usd = info.get("usd", 0)
                precio_cop = info.get("cop", 0)
                cambio_24h = info.get("usd_24h_change")

                if precio_usd == 0:
                    self.bot.reply_to(message, "⚠️ No hay datos válidos de precio (posiblemente token nuevo).")
                    return

                texto = (
                    f"💰 *{simbolo.upper()}*\n\n"
                    f"💵 USD: ${precio_usd:,.2f}\n"
                    f"🇨🇴 COP: ${precio_cop:,.0f}\n"
                )
                if cambio_24h is not None:
                    texto += f"📈 Cambio 24h: {cambio_24h:.2f}%"

                self.bot.reply_to(message, texto, parse_mode="Markdown")

            except Exception as e:
                print("Error en /precio:", e)
                self.bot.reply_to(message, f"⚠️ Error al obtener precio: {e}")

    # --- COMANDO /TOP ---
    def comando_top(self):
        @self.bot.message_handler(commands=["top"])
        def top_criptos(message):
            try:
                url = "https://api.coingecko.com/api/v3/coins/markets"
                params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 5, "page": 1}
                data = requests.get(url, params=params).json()

                mensaje = "🏆 *Top 5 Criptomonedas por Capitalización*\n\n"
                for coin in data:
                    mensaje += f"{coin['market_cap_rank']}. {coin['name']} ({coin['symbol'].upper()})\n"
                    mensaje += f"💵 Precio: ${coin['current_price']:,.2f}\n"
                    mensaje += f"📈 Cambio 24h: {coin['price_change_percentage_24h']:.2f}%\n\n"

                self.bot.send_message(message.chat.id, mensaje, parse_mode="Markdown")
            except Exception as e:
                self.bot.reply_to(message, f"⚠️ Error al obtener datos: {e}")

    def comando_convertir(self):
        @self.bot.message_handler(commands=["convertir"])
        def convertir_monedas(message):
            try:
                partes = message.text.split()
                if len(partes) != 4:
                    self.bot.reply_to(
                        message,
                        "Uso correcto: /convertir [cantidad] [cripto_origen] [moneda_destino]\n"
                        "Ejemplo: /convertir 0.5 BTC USD"
                    )
                    return

                cantidad = float(partes[1])
                cripto_origen = partes[2].lower().strip()
                moneda_destino = partes[3].lower().strip()

                id_origen = self.obtener_id_desde_simbolo(cripto_origen)
                if not id_origen:
                    self.bot.reply_to(message, "No encontré esa criptomoneda.")
                    return

                url = "https://api.coingecko.com/api/v3/simple/price"
                params = {"ids": id_origen, "vs_currencies": moneda_destino}
                data = requests.get(url, params=params, timeout=10).json()

                info = data.get(id_origen)
                if not info or moneda_destino not in info:
                    self.bot.reply_to(message, f"No pude convertir a {moneda_destino.upper()}.")
                    return

                precio = info[moneda_destino]
                if precio == 0:
                    self.bot.reply_to(message, "La API devolvió 0. Intenta más tarde.")
                    return

                total = cantidad * precio
                self.bot.reply_to(
                    message,
                    f" {cantidad} {cripto_origen.upper()} ≈ {total:,.2f} {moneda_destino.upper()}"
                )
            except Exception as e:
                print("Error en /convertir:", e)
                self.bot.reply_to(message, f"Error en conversión: {e}")

    # =====================================================
    #                 OTROS MÉTODOS DEL BOT
    # =====================================================

    def bot_mensajes_texto(self, message):
        if message.text.startswith("/"):
            self.bot.send_message(message.chat.id, "Comando incorrecto, mi compa 😅. Prueba con /precio o /top")
        else:
            self.bot.send_message(
                message.chat.id,
                "Recuerda, compadre, solo me comunico con comandos 💬.\n"
                "Prueba con /precio o /top 😉"
            )

    def conectar_base_datos(self):
        self.conn = sqlite3.connect('CryptoCompadre.sql')
        self.cursor = self.conn.cursor()

    def run(self):
        print("🚀 Iniciando el bot CriptoCompadre...")
        self.bot.infinity_polling()


# =========================================================
#                CLASES AUXILIARES
# =========================================================

class Usuario:
    def __init__(self, id_usuario=None, nombre_usuario=None, clave_usuario=None, historial_chat=None):
        self.id_usuario = id_usuario
        self.nombre_usuario = nombre_usuario
        self.clave_usuario = clave_usuario
        self.historial_chat = historial_chat if historial_chat else []

    def iniciar_sesion(self, nombre_usuario, clave_usuario):
        # Aquí luego podrás validar el usuario desde la base de datos
        pass

    def cerrar_sesion(self):
        # Aquí podrías limpiar la sesión actual
        pass


class Noticiero:
    def obtener_noticias(self):
        # Futuro: usar API de noticias cripto
        pass


class GeneradorGraficos:
    def generar_grafico_precio(self, activo):
        # Futuro: implementar matplotlib para mostrar precios históricos
        pass


    def generar_grafico_comparativo(self, lista_activos):
        # Futuro: graficar comparación de varios activos
        pass


# =========================================================
#                 EJECUCIÓN DEL BOT
# =========================================================
if __name__ == '__main__':
    bot = CryptoCompadre_Bot(TELEGRAM_TOKEN)
    bot.run()

