# Political Pop Lab · Personas y bots

## Ejecutar
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python server.py
```
Abre http://localhost:8002 en el computador. Para celulares, abre primero en el anfitrión la dirección IP actual del computador con el puerto 8002, en la misma red Wi-Fi; así el QR contendrá una dirección accesible. Localhost no funciona desde otros dispositivos.

## Sesión mixta
1. Crear sesión mixta.
2. Elegir cantidad de bots y velocidad; pulsar Iniciar simulación para activar los bots. En modalidad mixta permanecen en la sala de espera hasta que el anfitrión comience la ronda.
3. Compartir QR/código con los participantes y esperar sus avatares. El ingreso se cierra al abrir la primera ronda.
4. Abrir pantalla para proyectar en otra pestaña o pantalla. Este enlace es de solo lectura y no permite controlar la sesión.
5. Comenzar ronda 1. Los bots responden sin sustituir las respuestas humanas. El escrutinio aparece cuando todos terminan. El anfitrión puede cerrar manualmente si falta alguien.
6. Abrir ronda 2 y luego la primera votación.
7. Tras el primer resultado, conversar sobre las dos modificaciones: gratuidad focalizada o descuento de la mitad del pasaje. El anfitrión elige una y abre la segunda votación.
8. Ver el resultado y comparar ambos apoyos. Los participantes pueden guardar su reflexión personal.

Para participar tú mismo, abre el enlace de participantes en otro dispositivo o pestaña. La pestaña de anfitrión mantiene sus controles. Los bots se detienen en las transiciones de ronda de la sesión mixta para que puedas explicar los resultados. Pausar y Un paso controlan las acciones sintéticas.

## Ensayo solo con bots
En el inicio, elegir Ensayo solo con bots. Responden automáticamente hasta la negociación. El anfitrión debe elegir una modificación para abrir la segunda votación.

## Legislación simulada
Dos votaciones independientes de un proyecto ficticio sobre transporte estudiantil, con propuestas, financiamiento y decisiones a discutir. La segunda votación no borra la primera. La regla es mayoría absoluta de todos los escaños; no pretende reproducir todo el procedimiento legislativo chileno. Los bots usan preferencias sintéticas y probabilidades según el contenido de cada alternativa; sus votos no son una predicción sobre personas o movimientos reales. Cada bancada puede dividir sus votos.

## Separación y privacidad
Esta carpeta y el proceso del puerto 8002 están separados del prototipo original del puerto 8000. Datos de personas y bots viven solo en memoria hasta eliminar la sesión o por un máximo de cuatro horas; reiniciar pierde sesiones. No se solicitan nombres, correo, edad, curso ni cuentas. El anfitrión ve participación por avatar/escaño; no ve respuestas ni votos individuales humanos. La pantalla proyectada no recibe fichas individuales ni credenciales de anfitrión. Conservar sus enlaces de acceso solo durante la actividad. El historial de preguntas guarda únicamente secuencias de identificadores para evitar repeticiones, no respuestas.

Las imágenes y sus créditos corresponden a la versión educativa interna autorizada por el organizador. Revisar permisos antes de publicar o distribuir el material marcado educationalOnly en el catálogo.

## Pruebas
```
python -m unittest discover -s tests -v
node tests/layout.cjs
```
Incluye simulación completa, participación humana con bots, espera por respuestas humanas, acceso de proyección de solo lectura, dos votaciones, permisos de modificaciones, conservación del primer resultado y cálculo por pregunta. La revisión en celulares y la red real del recinto sigue siendo necesaria antes de la actividad.
