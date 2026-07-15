# Registro de Consultas a IA — Proyecto ICCD332 Grupo 3

**Asignatura:** Arquitectura de Computadores (ICCD332)
**Proyecto:** City Weather APP — Ciudad de México
**Herramienta utilizada:** Claude (Anthropic)
**Período de uso:** julio 2026

Este documento registra las consultas realizadas a herramientas de IA
durante el desarrollo del proyecto, conforme al requisito 9 del
enunciado. Para cada consulta se indica el contexto, lo que se
preguntó, y qué decisión tomó el grupo con la respuesta (aceptarla,
adaptarla o descartarla).

---

## 1. Revisión del código inicial del grupo

**Contexto:** Se tenía una primera versión de `main.py` que guardaba
~17 campos seleccionados manualmente del API.

**Consulta:** Revisión del script para verificar cumplimiento del
enunciado.

**Resultado y decisión del grupo:** La IA señaló que el enunciado
exige *toda* la información del API en columnas y sugirió aplanar el
JSON con una función recursiva, además de corregir el chequeo de
`cod` (el API devuelve entero en éxito y string en error). El grupo
adoptó la función `flatten()` y definió una lista fija `FIELDNAMES`
para que las columnas `rain`/`snow` (que el API solo envía cuando hay
el fenómeno) siempre existan en el CSV. Se decidió reiniciar la
recolección con el esquema completo en lugar de mezclar formatos.

## 2. Seguridad de la API key

**Consulta:** Cómo manejar la API key que había quedado expuesta en
el repositorio de GitHub.

**Resultado y decisión del grupo:** Se movió la key a una variable de
entorno (`OWM_API_KEY`) exportada desde `get-weather.sh`, se leyó en
Python con `os.environ.get()`, y se regeneró la key comprometida. En
la página del sitio la key se muestra ofuscada (`********`).

## 3. Error `source: not found` en get-weather.sh

**Contexto:** Al ejecutar el script aparecía `./get-weather.sh: 14:
source: not found` aunque el dato sí se guardaba.

**Consulta:** Causa del error y si afectaría a crontab.

**Resultado y decisión del grupo:** Se aprendió que en Ubuntu
`/usr/bin/sh` es *dash*, que no dispone del comando `source`. El dato
se guardaba de casualidad porque la terminal ya tenía conda en el
PATH, pero con cron (entorno mínimo) habría fallado. Se cambió el
shebang a `#!/bin/bash` y se verificó con `env -i HOME=$HOME
/bin/bash -c './get-weather.sh'` para simular el entorno vacío de
cron antes de confiar en la automatización.

## 4. Configuración de crontab en WSL

**Consulta:** Sintaxis de la línea de crontab con respaldo en
`output.log` y particularidades de cron en WSL.

**Resultado y decisión del grupo:** Se configuró
`*/15 * * * * .../get-weather.sh >> .../output.log 2>&1` y se
aprendió que en WSL el servicio cron no arranca automáticamente
(`sudo service cron start`). Durante las pruebas se detectó y corrigió
un error de tipeo en la ruta del crontab gracias al propio
`output.log`. Se decidió mantener la periodicidad de 15 minutos del
enunciado (y no una menor) porque el API actualiza sus estaciones
aproximadamente cada 10 minutos, de modo que consultas más frecuentes
producen datos repetidos.

## 5. Finales de línea de Windows en los archivos base

**Contexto:** `./build.sh` fallaba con `bad interpreter:
/usr/bin/bash^M`.

**Consulta:** Significado del error.

**Resultado y decisión del grupo:** Los archivos del material base
traían finales de línea CRLF de Windows. Se corrigió con `dos2unix`
sobre `build.sh` y `build-site.el`.

## 6. Ejecución de bloques org-babel con sesión

**Contexto:** Los bloques Python devolvían resultados vacíos o
`None`.

**Consulta:** Diagnóstico de los errores del buffer `*Python*`.

**Resultado y decisión del grupo:** Se identificaron en orden: (a)
faltaba instalar pandas/matplotlib/openpyxl en el entorno `iccd332`;
(b) el archivo de datos no estaba en la ruta esperada dentro de WSL;
(c) la carpeta `images/` no existía y `savefig` no crea directorios;
(d) el header `:return` de org-babel no funciona con `:session`, por
lo que se dejó la variable como última expresión del bloque. Cada
error se resolvió leyendo el traceback en el buffer `*Python*`, no
volviendo a preguntar a ciegas.

## 7. Análisis de los datos INEC (página 3)

**Consulta:** Estrategia para procesar la hoja `10.robo_domicilio`
del archivo de datos abiertos del INEC (encabezados en fila 4,
columnas mensuales 2014–2026, fila de Total Nacional mezclada con el
detalle cantonal).

**Resultado y decisión del grupo:** Se adoptó la lectura con
`header=3`, la separación de la fila "Total Nacional" y la agregación
anual/provincial con pandas. El grupo decidió incluir una *validación
cruzada* de la serie contra dos fuentes independientes: la fila Total
Nacional del propio Excel y las cifras de la presentación oficial del
INEC de febrero 2026 (721 denuncias ene–feb 2025, 630 ene–feb 2026,
4.407 en 2025), obteniendo coincidencia exacta. También se decidió
excluir 2026 del gráfico anual por ser un año incompleto, y señalar
como limitación que la fuente registra denuncias y no hechos
ocurridos.

## 8. Conversor IEEE 754 (página 2)

**Consulta:** Cómo implementar la conversión decimal → IEEE 754 de 32
bits en JavaScript embebido en org-mode, siguiendo el patrón del
material del curso (`page2-js.org`).

**Resultado y decisión del grupo:** Se utilizó `Float32Array`/
`DataView` para obtener los bits exactos y separar signo, exponente y
mantisa. El grupo añadió el ejemplo de verificación manual con
−12.375 para contrastar el resultado del conversor con el
procedimiento visto en clase.

## 9. Comprensión conceptual

**Consulta:** ¿Por qué recolectar 50+ datos si la tabla solo muestra
10?

**Resultado:** Se aclaró que la tabla con `df.sample(10)` es solo una
muestra ilustrativa de la estructura, mientras que las gráficas usan
el DataFrame completo; y que el volumen de datos espaciados cada 15
minutos es la evidencia de que la automatización con crontab funcionó
sin intervención manual.

---

## Valoración del uso de IA

La IA se utilizó como apoyo para **diagnóstico de errores**
(interpretar tracebacks y mensajes del sistema), **revisión de
cumplimiento del enunciado** y **aceleración de tareas repetitivas**
(estructura de los archivos .org). Las decisiones de diseño —
basarse en la plantilla del curso, reiniciar la recolección con el
esquema completo, mantener los 15 minutos del enunciado, validar los
datos del INEC contra la fuente oficial, y el ejemplo de verificación
manual de IEEE 754 — fueron tomadas y verificadas por el grupo. Todo
código sugerido fue ejecutado, probado y depurado en el entorno
propio antes de incorporarse al proyecto.
