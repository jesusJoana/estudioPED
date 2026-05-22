import socket
import threading
import time
import unittest
from datetime import datetime


class TestServidorTCP(unittest.TestCase):
    """Pruebas unitarias de la Iteracion 1: Servidor."""

    def crear_servidor(self, *args, **kwargs):
        from src.servidor import ServidorTCP

        return ServidorTCP(*args, **kwargs)

    def test_iteracion_1_servidor_configuracion_por_defecto(self):
        """
        Iteracion 1 - Requisito: el servidor TCP usa host local y puerto 16063
        por defecto, definidos en el constructor.
        """
        servidor = self.crear_servidor()

        self.assertEqual("127.0.0.1", servidor.host)
        self.assertEqual(16063, servidor.puerto)

    def test_iteracion_1_servidor_responde_fecha_actual(self):
        """
        Iteracion 1 - Requisito: ante el mensaje FECHA, el servidor devuelve la
        fecha actual del sistema.
        """
        servidor = self.crear_servidor()
        fecha_esperada = datetime.now().strftime("%Y-%m-%d")

        respuesta = servidor.procesar_mensaje("FECHA")

        self.assertEqual(fecha_esperada, respuesta)

    def test_iteracion_1_servidor_responde_hora_actual(self):
        """
        Iteracion 1 - Requisito: ante el mensaje HORA, el servidor devuelve la
        hora actual del sistema.
        """
        servidor = self.crear_servidor()

        respuesta = servidor.procesar_mensaje("HORA")

        self.assertRegex(respuesta, r"^\d{2}:\d{2}:\d{2}$")
        self.assertEqual(datetime.now().strftime("%H:%M"), respuesta[:5])

    def test_iteracion_1_servidor_responde_error_ante_mensaje_invalido(self):
        """
        Iteracion 1 - Requisito: cualquier mensaje distinto de FECHA o HORA
        devuelve ERROR.
        """
        servidor = self.crear_servidor()

        respuesta = servidor.procesar_mensaje("OTRO")

        self.assertEqual("ERROR", respuesta)

    def test_iteracion_1_servidor_atiende_una_conexion_tcp_real(self):
        """
        Iteracion 1 - Requisito: el servidor acepta una conexion TCP real,
        recibe un mensaje y devuelve la respuesta adecuada.
        """
        servidor = self.crear_servidor(puerto=0)
        hilo_servidor = threading.Thread(
            target=servidor.iniciar,
            kwargs={"max_conexiones": 1},
            daemon=True,
        )

        hilo_servidor.start()
        self._esperar_puerto_asignado(servidor)

        with socket.create_connection((servidor.host, servidor.puerto), timeout=2) as cliente:
            cliente.sendall(b"FECHA\n")
            respuesta = cliente.recv(1024).decode("utf-8").strip()

        hilo_servidor.join(timeout=2)

        self.assertFalse(hilo_servidor.is_alive())
        self.assertEqual(datetime.now().strftime("%Y-%m-%d"), respuesta)

    def _esperar_puerto_asignado(self, servidor):
        limite = time.time() + 2
        while servidor.puerto == 0 and time.time() < limite:
            time.sleep(0.01)

        self.assertNotEqual(0, servidor.puerto)
