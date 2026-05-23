import io
import socket
import subprocess
import sys
import threading
import time
import unittest
from contextlib import redirect_stdout
from datetime import date, datetime
from pathlib import Path
from unittest.mock import patch

from src.cliente import ClienteUDP
from src.servidor import ServidorUDP


class TestIntegracionClienteServidorUDP(unittest.TestCase):
    """Pruebas de la Iteracion 3: Integracion cliente-servidor."""

    def test_iteracion_3_cliente_y_servidor_intercambian_fecha(self):
        """
        Iteracion 3 - Integracion.
        Requisito: cliente y servidor reales intercambian FECHA y el cliente
        recibe una fecha valida.
        """
        servidor, hilo = self._arrancar_servidor(max_mensajes=1)
        cliente = ClienteUDP(host_servidor="127.0.0.1", puerto=servidor.puerto)

        try:
            respuesta = cliente.enviar_mensaje("FECHA")
        finally:
            servidor.detener()
            hilo.join(timeout=1)

        self.assertEqual(date.today(), datetime.strptime(respuesta, "%d/%m/%Y").date())

    def test_iteracion_3_cliente_y_servidor_intercambian_hora(self):
        """
        Iteracion 3 - Integracion.
        Requisito: cliente y servidor reales intercambian HORA y el cliente
        recibe una hora valida.
        """
        servidor, hilo = self._arrancar_servidor(max_mensajes=1)
        cliente = ClienteUDP(host_servidor="127.0.0.1", puerto=servidor.puerto)

        try:
            respuesta = cliente.enviar_mensaje("HORA")
        finally:
            servidor.detener()
            hilo.join(timeout=1)

        datetime.strptime(respuesta, "%H:%M:%S")

    def test_iteracion_3_cliente_y_servidor_intercambian_mensaje_desconocido(self):
        """
        Iteracion 3 - Integracion.
        Requisito: cliente y servidor reales intercambian un mensaje no
        reconocido y el cliente recibe ERROR.
        """
        servidor, hilo = self._arrancar_servidor(max_mensajes=1)
        cliente = ClienteUDP(host_servidor="127.0.0.1", puerto=servidor.puerto)

        try:
            respuesta = cliente.enviar_mensaje("fecha")
        finally:
            servidor.detener()
            hilo.join(timeout=1)

        self.assertEqual("ERROR", respuesta)

    def test_iteracion_3_flujo_completo_cliente_tres_mensajes_y_salir(self):
        """
        Iteracion 3 - Integracion.
        Requisito: el cliente envia tres mensajes reales al servidor y despues
        finaliza correctamente al recibir SALIR.
        """
        servidor, hilo = self._arrancar_servidor(max_mensajes=3)
        cliente = ClienteUDP(host_servidor="127.0.0.1", puerto=servidor.puerto)

        entradas = iter(["FECHA", "HORA", "OTRO", "SALIR"])
        salida = io.StringIO()
        with patch("builtins.input", side_effect=lambda _: next(entradas)):
            with redirect_stdout(salida):
                cliente.ejecutar_interactivo()

        servidor.detener()
        hilo.join(timeout=1)

        texto = salida.getvalue()
        self.assertIn("Cliente finalizado correctamente.", texto)
        self.assertIn("ERROR", texto)
        self.assertEqual(3, cliente.mensajes_enviados)

    def test_iteracion_3_main_lanza_servidor_y_atiende_udp(self):
        """
        Iteracion 3 - Integracion.
        Requisito: la aplicacion cliente-servidor se lanza desde main.py en
        modo servidor.
        """
        raiz = Path(__file__).resolve().parents[1]
        proceso = subprocess.Popen(
            [sys.executable, "main.py", "servidor"],
            cwd=raiz,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            self._esperar_puerto_udp("127.0.0.1", 16063)
            respuesta = self._enviar_udp("fecha", 16063)
        finally:
            proceso.terminate()
            proceso.wait(timeout=2)

        self.assertEqual("ERROR", respuesta)

    def _arrancar_servidor(self, max_mensajes):
        servidor = ServidorUDP(host="127.0.0.1", puerto=0)
        hilo = threading.Thread(
            target=servidor.iniciar,
            kwargs={"max_mensajes": max_mensajes},
            daemon=True,
        )
        hilo.start()

        limite = time.time() + 1
        while time.time() < limite:
            if servidor.puerto != 0:
                return servidor, hilo
            time.sleep(0.01)

        servidor.detener()
        self.fail("El servidor UDP no quedo listo")

    def _enviar_udp(self, mensaje, puerto):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as cliente:
            cliente.settimeout(1)
            cliente.sendto(mensaje.encode("utf-8"), ("127.0.0.1", puerto))
            datos, _ = cliente.recvfrom(1024)
            return datos.decode("utf-8")

    def _esperar_puerto_udp(self, host, puerto):
        limite = time.time() + 2
        while time.time() < limite:
            try:
                self._enviar_udp("PING", puerto)
                return
            except OSError:
                time.sleep(0.05)
        self.fail(f"El puerto UDP {host}:{puerto} no respondio a tiempo")


if __name__ == "__main__":
    unittest.main()
