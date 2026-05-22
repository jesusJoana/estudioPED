README - Sistema cliente-servidor TCP
====================================

1. Descripcion general
----------------------

Este proyecto implementa un sistema cliente-servidor usando Python y sockets
TCP/IP.

El servidor escucha en el host 127.0.0.1 y en el puerto TCP 16063. Se ejecuta de
forma continua, acepta conexiones de clientes y responde segun el mensaje
recibido.

Mensajes soportados por el servidor:

- FECHA: devuelve la fecha actual del sistema con formato AAAA-MM-DD.
- HORA: devuelve la hora actual del sistema con formato HH:MM:SS.
- Cualquier otro mensaje: devuelve ERROR.

El cliente se conecta automaticamente al servidor configurado. Permite escribir
mensajes de forma interactiva por terminal y muestra por salida estandar las
respuestas recibidas.

La orden SALIR es local del cliente y no se envia al servidor. El cliente solo
permite cerrar cuando se han enviado al menos 3 peticiones. Si se intenta cerrar
antes, muestra:

Faltan x mensajes antes de poder cerrar el cliente

2. Estructura del proyecto
--------------------------

main.py
    Punto de entrada de la aplicacion.

src/servidor.py
    Clase ServidorTCP y logica del protocolo del servidor.

src/cliente.py
    Clase ClienteTCP y logica interactiva del cliente.

tests/test_server.py
    Pruebas unitarias de la Iteracion 1: Servidor.

tests/test_client.py
    Pruebas unitarias de la Iteracion 2: Cliente.

tests/test_integracion.py
    Pruebas de la Iteracion 3: Integracion cliente-servidor.

docs/plan_de_iteraciones.md
    Plan de desarrollo seguido durante el ejercicio.

3. Manual de usuario
--------------------

Para ejecutar el servidor:

make run-server

El servidor queda escuchando en 127.0.0.1:16063 hasta que se detenga
manualmente con Ctrl+C.

Para ejecutar el cliente, abrir otra terminal y lanzar:

make run-client

Ejemplo de uso del cliente:

> FECHA
2026-05-22
> HORA
10:30:00
> OTRO
ERROR
> SALIR

Si se escribe SALIR antes de enviar 3 peticiones:

> SALIR
Faltan 3 mensajes antes de poder cerrar el cliente

4. Ejecucion de pruebas
-----------------------

Para ejecutar todas las pruebas automatizadas:

make test

Las pruebas usan unittest y sockets TCP reales cuando corresponde. Las pruebas
de integracion arrancan servidor y cliente reales usando un puerto temporal para
evitar conflictos con el puerto principal 16063.

5. Comandos disponibles
-----------------------

make install
    Crea el entorno virtual venv e instala dependencias si existe
    requirements.txt.

make test
    Ejecuta todas las pruebas con unittest.

make run-server
    Ejecuta el servidor.

make run-client
    Ejecuta el cliente interactivo.

make clean
    Elimina ficheros temporales de Python.

6. Notas de desarrollo
----------------------

El desarrollo se ha organizado siguiendo el ciclo RED -> GREEN -> REFACTOR:

- Iteracion 1: Servidor.
- Iteracion 2: Cliente.
- Iteracion 3: Integracion cliente-servidor.

En la Iteracion 3, las pruebas de integracion quedaron en verde directamente
porque las iteraciones anteriores ya habian implementado correctamente la
comunicacion TCP necesaria. No se forzo un fallo artificial.
