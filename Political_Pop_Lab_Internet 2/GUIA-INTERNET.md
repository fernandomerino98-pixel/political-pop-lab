# Jugar desde cualquier red

El computador anfitrión y los celulares solo necesitan internet. Una vez alojada la aplicación, el computador local puede dejar de ejecutar el servidor.

## Primera publicación

1. Crear una cuenta en https://github.com/signup y verificar el correo.
2. Crear un repositorio **privado** llamado `political-pop-lab`.
3. Descomprimir `Political_Pop_Lab_Internet.zip`. Subir a la raíz del repositorio todos los archivos y la carpeta `public` que contiene. `Dockerfile`, `server.py` y `render.yaml` deben quedar directamente en la raíz, sin otra carpeta contenedora.
4. Crear una cuenta en https://dashboard.render.com y conectar GitHub, dando acceso únicamente a este repositorio.
5. En Render, elegir **New → Blueprint**, seleccionar el repositorio y revisar que el servicio indique **Free**. El archivo `render.yaml` configura el despliegue. No hace falta crear una base de datos.
6. Esperar a que el servicio indique **Live**. Copiar la dirección HTTPS que Render asigne. Esa es la dirección del juego; no usar las direcciones locales antiguas.
7. Abrir esa dirección en el computador, crear una sesión mixta y compartir su QR. Los participantes no necesitan cuenta en GitHub ni Render.

Si Render pide datos de facturación o propone un servicio pagado, revisar el plan antes de continuar. Este paquete configura un servicio gratuito y no contrata ningún servicio por sí mismo.

## Ensayo antes de la actividad

1. Abrir el enlace HTTPS en el computador y crear una sesión mixta con tres bots.
2. En el celular, desactivar Wi-Fi y abrir el enlace usando datos móviles.
3. Ingresar con el QR/código, seleccionar avatar y completar ambas rondas.
4. Comprobar que el anfitrión espere las respuestas humanas y que cada participante tenga un escaño.
5. Abrir la pantalla de proyección y comprobar las dos votaciones y la modificación del proyecto.
6. Repetir con varios celulares y la cantidad de bots prevista para la demostración. La capacidad simultánea en Render todavía debe comprobarse en ese entorno.

## Para el 17 de octubre

El servicio gratuito se suspende tras 15 minutos sin tráfico y tarda aproximadamente un minuto en despertar. Render también puede reiniciarlo. Abrir el enlace antes de crear la sesión y mantener abierta la pantalla del anfitrión durante el juego. Para una actividad programada conviene evaluar una instancia que permanezca activa; su contratación requiere revisar el precio y autorizar el gasto.

Las sesiones están en memoria: cualquier reinicio, suspensión o despliegue borra la partida. Mantener **una sola instancia y un solo proceso**. Un plan pagado que permanezca activo reduce las suspensiones por inactividad, pero no permite recuperar partidas después de reinicios. No desplegar cambios durante una partida.

El historial de secuencias de preguntas también se pierde al reemplazar el almacenamiento temporal del servicio: no se garantiza evitar secuencias repetidas entre reinicios en este despliegue básico. Para conservarlo se necesita almacenamiento persistente.

La versión conserva los créditos y las imágenes de la actividad educativa interna. El repositorio privado protege el código, pero el enlace del juego será accesible desde internet; compartirlo solo con el grupo. No se piden datos personales. No compartir el enlace de control del anfitrión; usar el enlace independiente de proyección.

Fuentes: https://render.com/docs/free · https://render.com/docs/blueprint-spec · https://render.com/docs/docker
