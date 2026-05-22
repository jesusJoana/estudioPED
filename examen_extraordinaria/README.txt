SISTEMA CLIENTE-SERVIDOR UDP

Descripcion
-----------

Este proyecto implementa un sistema cliente-servidor usando sockets UDP.

El servidor escucha en el puerto 16063 y responde a peticiones del cliente para
buscar cadenas en los ficheros:

- /etc/services
- /etc/passwd

La aplicacion esta desarrollada en Python con Programacion Orientada a Objetos.
Las pruebas estan implementadas con unittest y se ejecutan mediante make.


Estructura
----------

main.py
  Punto de entrada de la aplicacion.

src/servidor.py
  Implementacion del servidor UDP.

src/cliente.py
  Implementacion del cliente UDP.

tests/test_server.py
  Pruebas unitarias del servidor.

tests/test_client.py
  Pruebas unitarias del cliente.

tests/test_integracion.py
  Pruebas de integracion cliente-servidor.

docs/plan_iteraciones.md
  Plan de trabajo seguido durante el desarrollo.


Protocolo
---------

BUSCAR <cadena>

El servidor busca <cadena> en /etc/services y /etc/passwd.
La busqueda distingue mayusculas y minusculas.

Respuesta:

<numero_de_lineas_encontradas>
<linea_encontrada_1>
<linea_encontrada_2>

Si no hay resultados:

0


NUMERO

Devuelve el numero de busquedas BUSCAR validas ejecutadas por el servidor.

Respuesta:

OK <numero>


SALIR

Solicita que el servidor termine su ejecucion.

SALIR solo es efectivo cuando el cliente ha enviado al menos 3 mensajes.
El propio mensaje SALIR cuenta dentro de esos 3 mensajes.

Si aun no se han enviado 3 mensajes:

Aun solo se han enviado <x> mensajes de los 3 necesarios

Si ya se han enviado al menos 3 mensajes:

OK

Despues de responder OK, el servidor finaliza.


Mensajes invalidos
------------------

Cualquier mensaje desconocido, mal escrito o mal formateado devuelve:

ERROR

Ejemplos invalidos:

BUSCAR
BUSCAR root extra
buscar root
NUMERO algo
SALIR ahora


Uso basico
----------

Terminal 1: lanzar el servidor.

make run-server 2> server.log

El servidor quedara escuchando en 127.0.0.1:16063.

Se recomienda redirigir stderr a server.log porque el enunciado pide que el
servidor escriba por la salida de error estandar la IP del cliente y el mensaje
recibido.


Terminal 2: lanzar el cliente.

make run-client

El cliente pedira la direccion completa del servidor:

Direccion completa del servidor (host:puerto):

Ejemplo:

127.0.0.1:16063


Ejemplo de sesion
-----------------

Cliente:

Direccion completa del servidor (host:puerto): 127.0.0.1:16063
BUSCAR root
Mensaje 1: BUSCAR root
1
root:x:0:0:root:/root:/bin/bash
NUMERO
Mensaje 2: NUMERO
OK 1
SALIR
Mensaje 3: SALIR
OK


Servidor
--------

El servidor se ejecuta de forma continua hasta recibir un SALIR valido.

Si se lanza con:

make run-server 2> server.log

el fichero server.log contendra lineas como:

Cliente 127.0.0.1 envio: BUSCAR root
Cliente 127.0.0.1 envio: NUMERO
Cliente 127.0.0.1 envio: SALIR


Notas
-----

El cliente no termina al enviar SALIR si el servidor no responde OK.

Si SALIR se envia antes de llegar al minimo de 3 mensajes, el servidor no se
detiene y el cliente continua permitiendo enviar mas mensajes.

El cliente informa por salida estandar cualquier error de direccion o de
comunicacion con el servidor.
