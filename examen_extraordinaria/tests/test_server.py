import os
import tempfile
import unittest

from src.servidor import ServidorUDP


class TestServidorUDP(unittest.TestCase):
    """Pruebas unitarias de la Iteracion 1: Servidor."""

    def setUp(self):
        self.directorio = tempfile.TemporaryDirectory()
        self.services = os.path.join(self.directorio.name, "services")
        self.passwd = os.path.join(self.directorio.name, "passwd")

        with open(self.services, "w", encoding="utf-8") as fichero:
            fichero.write("ssh 22/tcp # SSH Remote Login Protocol\n")
            fichero.write("http 80/tcp # World Wide Web\n")
            fichero.write("RootService 999/tcp # servicio con mayuscula\n")

        with open(self.passwd, "w", encoding="utf-8") as fichero:
            fichero.write("root:x:0:0:root:/root:/bin/bash\n")
            fichero.write("daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\n")
            fichero.write("usuario:x:1000:1000:Root User:/home/usuario:/bin/bash\n")

        self.servidor = ServidorUDP(
            host="127.0.0.1",
            puerto=0,
            rutas_ficheros=[self.services, self.passwd],
        )
        self.cliente = ("127.0.0.1", 45000)

    def tearDown(self):
        self.directorio.cleanup()

    def test_buscar_devuelve_numero_y_lineas_completas(self):
        """Iteracion 1: BUSCAR devuelve total de coincidencias y lineas completas."""
        respuesta = self.servidor.procesar_mensaje("BUSCAR root", self.cliente)

        self.assertEqual(
            respuesta,
            "1\nroot:x:0:0:root:/root:/bin/bash",
        )

    def test_buscar_distingue_mayusculas_y_minusculas(self):
        """Iteracion 1: la busqueda diferencia mayusculas de minusculas."""
        respuesta = self.servidor.procesar_mensaje("BUSCAR Root", self.cliente)

        self.assertEqual(
            respuesta,
            "2\n"
            "RootService 999/tcp # servicio con mayuscula\n"
            "usuario:x:1000:1000:Root User:/home/usuario:/bin/bash",
        )

    def test_buscar_sin_resultados_devuelve_cero(self):
        """Iteracion 1: BUSCAR devuelve 0 cuando no hay coincidencias."""
        respuesta = self.servidor.procesar_mensaje("BUSCAR inexistente", self.cliente)

        self.assertEqual(respuesta, "0")

    def test_buscar_mal_formateado_devuelve_error(self):
        """Iteracion 1: BUSCAR mal escrito o mal formateado devuelve ERROR."""
        mensajes_invalidos = [
            "BUSCAR",
            "BUSCAR root extra",
            "buscar root",
            "BUSCAR ",
        ]

        for mensaje in mensajes_invalidos:
            with self.subTest(mensaje=mensaje):
                respuesta = self.servidor.procesar_mensaje(mensaje, self.cliente)
                self.assertEqual(respuesta, "ERROR")

    def test_numero_devuelve_cero_antes_de_buscar(self):
        """Iteracion 1: NUMERO devuelve OK 0 antes de ejecutar busquedas."""
        respuesta = self.servidor.procesar_mensaje("NUMERO", self.cliente)

        self.assertEqual(respuesta, "OK 0")

    def test_numero_cuenta_solo_busquedas_validas(self):
        """Iteracion 1: NUMERO cuenta solo mensajes BUSCAR validos."""
        self.servidor.procesar_mensaje("BUSCAR root", self.cliente)
        self.servidor.procesar_mensaje("BUSCAR", self.cliente)
        self.servidor.procesar_mensaje("NUMERO", self.cliente)
        self.servidor.procesar_mensaje("DESCONOCIDO", self.cliente)

        respuesta = self.servidor.procesar_mensaje("NUMERO", self.cliente)

        self.assertEqual(respuesta, "OK 1")

    def test_salir_antes_de_tres_mensajes_no_termina(self):
        """Iteracion 1: SALIR antes de 3 mensajes avisa y no detiene el servidor."""
        respuesta = self.servidor.procesar_mensaje("SALIR", self.cliente)

        self.assertEqual(
            respuesta,
            "Aun solo se han enviado 1 mensajes de los 3 necesarios",
        )
        self.assertFalse(self.servidor.debe_terminar)

    def test_salir_como_tercer_mensaje_devuelve_ok_y_termina(self):
        """Iteracion 1: SALIR como tercer mensaje devuelve OK y detiene el servidor."""
        self.servidor.procesar_mensaje("NUMERO", self.cliente)
        self.servidor.procesar_mensaje("BUSCAR root", self.cliente)

        respuesta = self.servidor.procesar_mensaje("SALIR", self.cliente)

        self.assertEqual(respuesta, "OK")
        self.assertTrue(self.servidor.debe_terminar)

    def test_mensajes_invalidos_devuelven_error(self):
        """Iteracion 1: cualquier mensaje no reconocido devuelve ERROR."""
        mensajes_invalidos = [
            "",
            " ",
            "HOLA",
            "NUMERO ahora",
            "SALIR ahora",
        ]

        for mensaje in mensajes_invalidos:
            with self.subTest(mensaje=mensaje):
                respuesta = self.servidor.procesar_mensaje(mensaje, self.cliente)
                self.assertEqual(respuesta, "ERROR")


if __name__ == "__main__":
    unittest.main()
