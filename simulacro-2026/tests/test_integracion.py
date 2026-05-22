import io
import threading
import time
import unittest
from contextlib import redirect_stdout
from datetime import datetime
from unittest.mock import patch

from src.cliente import ClienteTCP
from src.servidor import ServidorTCP


class TestIntegracionClienteServidor(unittest.TestCase):
    """Pruebas de la Iteracion 3: Integracion cliente-servidor."""

    def test_iteracion_3_cliente_servidor_responden_a_los_mensajes_del_protocolo(self):
        """
        Iteracion 3 - Requisitos: cliente y servidor reales se comunican por
        TCP y completan el flujo FECHA, HORA y mensaje invalido.
        """
        servidor = self._arrancar_servidor(max_conexiones=3)
        cliente = ClienteTCP(puerto=servidor.puerto)

        respuesta_fecha = cliente.enviar_peticion("FECHA")
        respuesta_hora = cliente.enviar_peticion("HORA")
        respuesta_error = cliente.enviar_peticion("OTRO")

        self.assertEqual(datetime.now().strftime("%Y-%m-%d"), respuesta_fecha)
        self.assertRegex(respuesta_hora, r"^\d{2}:\d{2}:\d{2}$")
        self.assertEqual("ERROR", respuesta_error)
        self.assertEqual(3, cliente.peticiones_enviadas)

    def test_iteracion_3_cliente_interactivo_termina_tras_tres_peticiones_y_salir(self):
        """
        Iteracion 3 - Requisitos: el cliente interactivo envia al menos 3
        peticiones reales, imprime las respuestas y permite cerrar con SALIR.
        """
        servidor = self._arrancar_servidor(max_conexiones=3)
        cliente = ClienteTCP(puerto=servidor.puerto)
        entradas = iter(["FECHA", "HORA", "INVALIDO", "SALIR"])
        salida = io.StringIO()

        with patch("builtins.input", lambda _: next(entradas)), redirect_stdout(salida):
            cliente.ejecutar()

        texto_salida = salida.getvalue()

        self.assertIn(datetime.now().strftime("%Y-%m-%d"), texto_salida)
        self.assertIn("ERROR", texto_salida)
        self.assertEqual(3, cliente.peticiones_enviadas)
        self.assertFalse(cliente.activo)

    def _arrancar_servidor(self, max_conexiones):
        servidor = ServidorTCP(puerto=0)
        hilo = threading.Thread(
            target=servidor.iniciar,
            kwargs={"max_conexiones": max_conexiones},
            daemon=True,
        )
        hilo.start()
        self._esperar_puerto_asignado(servidor)
        self.addCleanup(hilo.join, 2)
        return servidor

    def _esperar_puerto_asignado(self, servidor):
        limite = time.time() + 2
        while servidor.puerto == 0 and time.time() < limite:
            time.sleep(0.01)

        self.assertNotEqual(0, servidor.puerto)
