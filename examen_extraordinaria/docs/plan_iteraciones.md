# Plan de iteraciones

## Proyecto

Sistema cliente-servidor UDP para consultar informacion sobre frases o cadenas contenidas en ficheros conocidos por el servidor.

El servidor trabajara sobre:

- `/etc/services`
- `/etc/passwd`

El puerto UDP del servidor sera:

- `16063`

El desarrollo seguira el contrato definido en `CONTRATO/contrato_ped.md`, usando:

- Python
- Programacion Orientada a Objetos
- `unittest`
- ejecucion mediante `make`
- arquitectura cliente-servidor
- ciclo TDD pragmatico `RED -> GREEN -> REFACTOR`

Antes de implementar codigo se debera confirmar este plan.

## Criterio de refactorizacion

La entrega `Refactor` se realizara en todas las iteraciones siempre que exista una mejora interna razonable que aplicar.

Como criterio practico para este ejercicio, se intentara incluir refactorizacion en cada iteracion, ya que forma parte del estilo de trabajo esperado. Solo se omitira si, tras dejar los tests en verde, no hay una mejora clara que no introduzca ruido ni cambios de comportamiento.

## Protocolo funcional

### Mensaje `BUSCAR <cadena>`

El servidor buscara `<cadena>` en `/etc/services` y `/etc/passwd`.

La busqueda distinguira mayusculas y minusculas.

La respuesta tendra el formato:

```text
<numero_de_lineas_encontradas>
<linea_encontrada_1>
<linea_encontrada_2>
...
```

Si no hay resultados, la respuesta sera:

```text
0
```

### Mensaje `NUMERO`

El servidor devolvera el numero de busquedas `BUSCAR` ejecutadas hasta ese momento.

Formato de respuesta:

```text
OK <numero_de_busquedas>
```

### Mensaje `SALIR`

El servidor solo terminara si el cliente que envia `SALIR` ya ha enviado al menos 3 mensajes.

El propio mensaje `SALIR` contara dentro de esos 3 mensajes.

Si el cliente no ha llegado al minimo:

```text
Aun solo se han enviado <x> mensajes de los 3 necesarios
```

Si el cliente ya ha llegado al minimo:

```text
OK
```

Despues de responder `OK`, el servidor terminara.

### Mensajes invalidos

Cualquier mensaje desconocido, mal escrito o mal formateado devolvera:

```text
ERROR
```

Ejemplos invalidos:

- `BUSCAR`
- `BUSCAR cadena extra`
- `buscar cadena`
- `NUMERO algo`
- `SALIR ahora`
- cadena vacia

## Estructura prevista

```text
examen_extraordinaria/
  Makefile
  main.py
  README.txt
  INSTALL.txt
  docs/
    plan_iteraciones.md
  src/
    __init__.py
    servidor.py
    cliente.py
  tests/
    __init__.py
    test_server.py
    test_client.py
    test_integracion.py
```

## Iteracion 1: Servidor

### Objetivo

Implementar la funcionalidad principal del servidor UDP:

- crear servidor orientado a objetos;
- escuchar mediante UDP;
- procesar mensajes del protocolo;
- buscar cadenas en `/etc/services` y `/etc/passwd`;
- contar busquedas ejecutadas;
- controlar el minimo de 3 mensajes por cliente para aceptar `SALIR`;
- devolver `ERROR` ante mensajes invalidos.

### Entrega `Test 1 Servidor`

Se crearan pruebas unitarias del servidor en:

- `tests/test_server.py`

Pruebas previstas:

- validar que `BUSCAR <cadena>` devuelve el numero de lineas encontradas y las lineas completas;
- validar que la busqueda distingue mayusculas y minusculas;
- validar que `BUSCAR` mal formateado devuelve `ERROR`;
- validar que `NUMERO` devuelve `OK 0` antes de hacer busquedas;
- validar que `NUMERO` incrementa solo con mensajes `BUSCAR` validos;
- validar que `SALIR` antes de 3 mensajes no termina y devuelve el aviso correspondiente;
- validar que `SALIR` como tercer mensaje devuelve `OK` y marca el servidor para terminar;
- validar que mensajes desconocidos devuelven `ERROR`.

Estas pruebas deberan quedar inicialmente en rojo.

### Entrega `Test 1 Servidor OK`

Implementacion minima en:

- `src/servidor.py`
- `src/__init__.py`

Estrategia:

- crear una clase `ServidorUDP`;
- definir `host` y `puerto` en el constructor, por defecto `127.0.0.1` y `16063`;
- separar el procesamiento del mensaje en un metodo testeable;
- mantener contador de busquedas global del servidor;
- mantener contador de mensajes por cliente usando la direccion recibida;
- implementar lectura de ficheros con manejo basico de errores;
- implementar un bucle UDP continuo para ejecucion real, y mecanismos limitados o testeables para pruebas.

### Entrega `Refactor 1 Servidor`

Se realizara siempre que exista una mejora interna razonable tras dejar en verde `Test 1 Servidor OK`.

Mejoras previstas:

- extraer constantes del protocolo;
- mejorar nombres;
- simplificar validaciones;
- reducir duplicacion entre lectura de ficheros y formateo de respuestas.

No se anadiran nuevas funcionalidades en esta entrega.

## Iteracion 2: Cliente

### Objetivo

Implementar el cliente UDP inicial:

- crear cliente orientado a objetos;
- conectarse automaticamente al servidor por defecto;
- pedir mensajes iterativamente por terminal;
- enviar al menos 3 mensajes;
- imprimir respuestas recibidas;
- imprimir errores de comunicacion;
- cerrar correctamente el socket al terminar.

### Entrega `Test 2 Cliente`

Se crearan pruebas unitarias del cliente en:

- `tests/test_client.py`

Pruebas previstas:

- validar que el cliente puede enviar un mensaje UDP y recibir una respuesta;
- validar que imprime por salida estandar la respuesta recibida;
- validar que puede procesar una secuencia de al menos 3 mensajes;
- validar que termina tras recibir respuesta a `SALIR`;
- validar que muestra un error si no recibe respuesta dentro del timeout;
- validar que cierra el socket correctamente.

Estas pruebas deberan quedar inicialmente en rojo.

### Entrega `Test 2 Cliente OK`

Implementacion minima en:

- `src/cliente.py`
- `main.py`

Estrategia:

- crear una clase `ClienteUDP`;
- definir `host` y `puerto` en el constructor, por defecto `127.0.0.1` y `16063`;
- usar socket UDP con timeout;
- usar `connect` sobre UDP para fijar destino;
- separar envio/recepcion de la interaccion por terminal;
- implementar un metodo de ejecucion interactiva que pida mensajes hasta cumplir el flujo esperado.

### Entrega `Refactor 2 Cliente`

Se realizara siempre que exista una mejora interna razonable tras dejar en verde `Test 2 Cliente OK`.

Mejoras previstas:

- limpiar gestion de errores;
- mejorar nombres de metodos;
- reducir duplicacion entre ejecucion interactiva y pruebas.

No se anadiran nuevas funcionalidades en esta entrega.

## Iteracion 3: Integracion cliente-servidor

### Objetivo

Validar el flujo completo con cliente y servidor reales comunicandose por UDP.

### Entrega `Test 3 Integracion`

Se crearan pruebas de integracion en:

- `tests/test_integracion.py`

Pruebas previstas:

- arrancar un servidor UDP real en un puerto de prueba;
- enviar desde un cliente real una secuencia como `BUSCAR`, `NUMERO`, `SALIR`;
- comprobar que el cliente recibe e imprime las respuestas correctas;
- comprobar que `SALIR` antes del tercer mensaje no detiene el servidor;
- comprobar que `SALIR` como tercer mensaje o posterior detiene el servidor;
- comprobar que un mensaje invalido devuelve `ERROR`.

Estas pruebas deberan quedar inicialmente en rojo.

### Entrega `Test 3 Integracion OK`

Implementacion minima para dejar en verde la colaboracion entre:

- `src/servidor.py`
- `src/cliente.py`
- `main.py`
- `Makefile`, si fuera necesario ajustar objetivos existentes.

Estrategia:

- ejecutar servidor en hilo o proceso controlado por el test;
- usar puertos temporales de prueba para evitar conflictos;
- configurar timeouts para que ninguna prueba quede bloqueada;
- mantener `16063` como puerto por defecto de ejecucion real.

### Entrega `Refactor 3 Integracion`

Se realizara siempre que exista una mejora interna razonable tras dejar en verde `Test 3 Integracion OK`.

Mejoras previstas:

- unificar configuracion de timeouts;
- mejorar apagado controlado del servidor en pruebas;
- aclarar responsabilidades entre cliente, servidor y `main.py`.

No se anadiran nuevas funcionalidades en esta entrega.

## Iteracion 4: Servidor modificado

### Objetivo

Modificar el servidor para que imprima en la salida de error estandar una linea cada vez que recibe un mensaje de un cliente.

La linea debera incluir:

- direccion IP del cliente;
- mensaje recibido.

Ejemplo:

```text
Cliente 127.0.0.1 envio: BUSCAR ssh
```

### Entrega `Test 4 Servidor modificado`

Se anadiran pruebas en:

- `tests/test_server.py`

Pruebas previstas:

- validar que al recibir un mensaje se escribe una linea en `stderr`;
- validar que la linea contiene la IP del cliente;
- validar que la linea contiene el mensaje recibido;
- validar que esta salida no altera la respuesta enviada al cliente.

Estas pruebas deberan quedar inicialmente en rojo.

### Entrega `Test 4 Servidor modificado OK`

Implementacion minima en:

- `src/servidor.py`

Estrategia:

- escribir en `sys.stderr` o permitir inyectar un flujo de error para facilitar pruebas;
- registrar el mensaje justo despues de recibirlo y antes o durante su procesamiento;
- conservar intacto el protocolo de respuestas.

### Entrega `Refactor 4 Servidor modificado`

Se realizara siempre que exista una mejora interna razonable tras dejar en verde `Test 4 Servidor modificado OK`.

Mejoras previstas:

- extraer el formateo del log a un metodo privado;
- mejorar la inyeccion del flujo de error en pruebas.

No se anadiran nuevas funcionalidades en esta entrega.

## Iteracion 5: Cliente modificado

### Objetivo

Modificar el cliente para que pregunte al usuario por la direccion completa del servidor e imprima un error si no consigue comunicarse con el servidor.

Formato previsto de direccion:

```text
<host>:<puerto>
```

Ejemplo:

```text
127.0.0.1:16063
```

### Entrega `Test 5 Cliente modificado`

Se anadiran pruebas en:

- `tests/test_client.py`

Pruebas previstas:

- validar que el cliente solicita la direccion completa del servidor;
- validar que parsea correctamente `127.0.0.1:16063`;
- validar que rechaza direcciones mal formateadas;
- validar que imprime un error si no consigue comunicarse con el servidor;
- validar que, con una direccion correcta, mantiene el flujo normal de envio de mensajes.

Estas pruebas deberan quedar inicialmente en rojo.

### Entrega `Test 5 Cliente modificado OK`

Implementacion minima en:

- `src/cliente.py`
- `main.py`, si fuera necesario ajustar el modo de ejecucion.

Estrategia:

- anadir un metodo para pedir y parsear la direccion completa;
- mantener valores por defecto en el constructor para pruebas y compatibilidad;
- detectar errores de formato antes de crear o usar el socket;
- mantener timeout para detectar falta de respuesta del servidor.

### Entrega `Refactor 5 Cliente modificado`

Se realizara siempre que exista una mejora interna razonable tras dejar en verde `Test 5 Cliente modificado OK`.

Mejoras previstas:

- extraer parseo de direccion a un metodo pequeno;
- mejorar mensajes de error;
- simplificar el flujo interactivo.

No se anadiran nuevas funcionalidades en esta entrega.

## Documentacion final

Al cerrar la practica se generaran o actualizaran:

- `README.txt`
- `INSTALL.txt`

Contenido previsto:

- descripcion general;
- instrucciones de instalacion;
- ejecucion con `make`;
- ejemplos de uso;
- descripcion del protocolo;
- notas sobre UDP, puerto `16063` y formato de direccion del cliente modificado.

## Riesgos y decisiones

- UDP no establece conexiones reales como TCP. En el cliente se usara `socket.connect` para fijar destino y simplificar envio/recepcion, pero el servidor seguira usando `recvfrom`.
- El control de los 3 mensajes se hara por cliente, usando la direccion del cliente recibida por el servidor.
- El mensaje `SALIR` contara como mensaje enviado. Por tanto, si `SALIR` es el tercer mensaje de ese cliente, sera valido.
- Los tests usaran puertos de prueba distintos de `16063` cuando sea necesario para evitar conflictos.
- Se usaran timeouts en todos los sockets de pruebas para evitar bloqueos.
- No se usaran dependencias externas salvo que aparezca una necesidad justificada.
