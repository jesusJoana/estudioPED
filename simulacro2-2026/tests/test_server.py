import socket
import threading
import time
import unittest
from datetime import date, datetime

from src.servidor import ServidorUDP


class TestServidorUDP(unittest.TestCase):
    """Pruebas unitarias de la Iteracion 1: Servidor."""

    def test_iteracion_1_responde_fecha_actual_ante_mensaje_fecha(self):
        """
        Iteracion 1 - Servidor.
        Requisito: ante el mensaje FECHA, el servidor responde con la fecha
        actual del sistema.
        """
        servidor = ServidorUDP()

        respuesta = servidor.procesar_mensaje("FECHA")

        self.assertEqual(date.today(), datetime.strptime(respuesta, "%d/%m/%Y").date())

    def test_iteracion_1_responde_hora_valida_ante_mensaje_hora(self):
        """
        Iteracion 1 - Servidor.
        Requisito: ante el mensaje HORA, el servidor responde con la hora
        actual del sistema.
        """
        servidor = ServidorUDP()

        respuesta = servidor.procesar_mensaje("HORA")

        datetime.strptime(respuesta, "%H:%M:%S")

    def test_iteracion_1_responde_error_ante_mensaje_no_reconocido(self):
        """
        Iteracion 1 - Servidor.
        Requisito: cualquier mensaje distinto de FECHA y HORA obtiene ERROR.
        """
        servidor = ServidorUDP()

        respuesta = servidor.procesar_mensaje("BUENAS")

        self.assertEqual("ERROR", respuesta)

    def test_iteracion_1_distingue_mayusculas_y_minusculas(self):
        """
        Iteracion 1 - Servidor.
        Requisito: el protocolo es estricto; fecha en minusculas no equivale a
        FECHA y debe devolver ERROR.
        """
        servidor = ServidorUDP()

        respuesta = servidor.procesar_mensaje("fecha")

        self.assertEqual("ERROR", respuesta)

    def test_iteracion_1_atiende_varios_datagramas_udp_sin_finalizar(self):
        """
        Iteracion 1 - Servidor.
        Requisito: el servidor UDP recibe varios mensajes reales y responde a
        cada uno sin finalizar tras el primer datagrama.
        """
        servidor = ServidorUDP(host="127.0.0.1", puerto=0)
        hilo_servidor = threading.Thread(
            target=servidor.iniciar,
            kwargs={"max_mensajes": 4},
            daemon=True,
        )
        hilo_servidor.start()
        self._esperar_servidor_udp(servidor)

        try:
            respuestas = [
                self._enviar_udp("FECHA", servidor.puerto),
                self._enviar_udp("HORA", servidor.puerto),
                self._enviar_udp("DESCONOCIDO", servidor.puerto),
                self._enviar_udp("fecha", servidor.puerto),
            ]
        finally:
            servidor.detener()
            hilo_servidor.join(timeout=1)

        self.assertEqual(date.today(), datetime.strptime(respuestas[0], "%d/%m/%Y").date())
        datetime.strptime(respuestas[1], "%H:%M:%S")
        self.assertEqual("ERROR", respuestas[2])
        self.assertEqual("ERROR", respuestas[3])

    def _enviar_udp(self, mensaje, puerto):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as cliente:
            cliente.settimeout(1)
            cliente.sendto(mensaje.encode("utf-8"), ("127.0.0.1", puerto))
            datos, _ = cliente.recvfrom(1024)
            return datos.decode("utf-8")

    def _esperar_servidor_udp(self, servidor):
        limite = time.time() + 1
        while time.time() < limite:
            if servidor.puerto != 0:
                return
            time.sleep(0.01)
        self.fail("El servidor UDP no quedo listo dentro del tiempo esperado")


if __name__ == "__main__":
    unittest.main()
