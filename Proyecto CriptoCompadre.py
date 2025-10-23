import sqlite3
import telebot #para manejar la API de Telegram
from Token import TELEGRAM_TOKEN #importamos el token


class CryptoCompadre_Bot:

    def __init__(self, TELEGRAM_TOKEN):
        self.bot = telebot.TeleBot(TELEGRAM_TOKEN)
        self.responder_comando()

    def bienvenida_a_usuario(self, message):
        self.bot.reply_to(message,"Bienvenido al Bot CriptoCompadre, ¿Cómo puedo ayudarte?")

    def responder_comando(self):
        @self.bot.message_handler(commands=["start", "inicio"])
        def responder_a_comandos(message):
            self.bienvenida_a_usuario(message)

        @self.bot.message_handler(content_types=["text"])
        def responder_mensajes_texto(message):
            self.bot_mensajes_texto(message)

    def bot_mensajes_texto(self, message):
        if message.text.startswith("/"):
                self.bot.send_message(message.chat.id, "Comando incorrecto mi compa ")

        else:
            self.bot.send_message(message.chat.id, "Recuerda, compadre, solo me comunico con comandos,"
                                                    " así que no entiendo lo que dices. ¡Intenta con un comando!")

    def run(self):
        print("iniciando el bot")
        self.bot.infinity_polling()
        print("fin")

    def conectar_base_datos(self):
        self.conn = sqlite3.connect('CryptoCompadre.sql')
        self.cursor = self.conn.cursor()

class Usuario:
    pass

class Graficos:
    pass

if __name__ == '__main__':
    bot = CryptoCompadre_Bot(TELEGRAM_TOKEN)
    bot.run()



#class Usuario:
    #def __init__(self, id_usuario: int, nombre_usuario: str, clave_usuario: str, historial_chat: list):
        #self.id_usuario = id_usuario
        #self.nombre_usuario = nombre_usuario
        #self.clave_usuario = clave_usuario

    def iniciar_sesion(self, nombre_usuario, clave_usuario):
        pass

    #def cerrar_sesion(self):
        #pass


class Noticiero:

    def obtener_noticias(self):
        pass

#class Activo:
    #def __init__(self, symbol: str, nombre: str, tipo: str):
        #self.nombre = nombre
        #self.tipo = tipo
        #self.precio_actual = 0.0
        #self.datos_historicos = []

class GeneradorGraficos:
    def generar_grafico_precio(self, activo):
        pass

    def generar_grafico_comparativo(self, lista_activos):
        pass