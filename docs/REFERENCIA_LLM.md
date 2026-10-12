# REFERENCIA PARA EL LLM — cómo convertir un test a JSON y cómo publicarlo

Este documento es para que un agente LLM (o tú mismo en el futuro) sepa, sin ambigüedad:
1. cómo está montado el proyecto,
2. cómo convertir un test escrito a mano al fichero JSON que consume la web,
3. qué pasos hacen falta para publicarlo,
4. qué contestar al profesor cuando pregunte.

Todo el proyecto es estático (HTML + JS + JSON). No hay servidor, base de datos ni cuentas
de alumno. La corrección ocurre en el navegador del alumno y no se guarda ninguna nota.

---

## 1. Mapa del proyecto

    index.html                     Motor del test. NO se toca al añadir exámenes.
    fuentes/*.md                   AQUÍ se escriben los exámenes (texto plano).
    herramientas/convertir.py      fuentes/*.md  ->  data/*.json  (valida el formato).
    herramientas/publicar.py       convierte + publica (git o API de GitHub).
    data/index.json                Índice de exámenes (LO GENERA el script; no editar a mano).
    data/examenes/*.json           Un JSON por examen (LO GENERA el script).
    docs/REFERENCIA_LLM.md         Este documento.
    docs/ESQUEMA_JSON.md           Esquema exacto del JSON y del índice.
    .nojekyll                      Evita que GitHub Pages procese el sitio con Jekyll.

Fuente de verdad = `fuentes/*.md`. Lo de `data/` es derivado: si se edita a mano, la
siguiente conversión lo sobrescribe.

---

## 2. Formato de un test en texto (`fuentes/*.md`)

    # Título del examen
    #Descripción: texto opcional que aparece en el listado
    #Grupo: A
    #Barajar preguntas: no

    ## Enunciado de la pregunta
    - opción incorrecta
    - opción correcta *
    - otra opción
    - otra opción

    ## Pregunta de respuesta múltiple
    - correcta A *
    - incorrecta
    - correcta B *
    - incorrecta

Reglas (el conversor las valida y aborta si algo no cuadra):

1. La primera línea que empieza por `# ` es el TÍTULO (obligatorio).
2. Directivas opcionales (línea que empieza por `#` y contiene `:`):
   - `#Descripción: ...`  -> descripción del examen.
   - `#Grupo: A`          -> etiqueta de grupo (para filtrar en la web con `?grupo=A`).
   - `#Barajar preguntas: si|no` -> si se mezcla el orden de las preguntas (por defecto no).
   - `#Slug: mi-id`       -> fuerza el identificador/URL del examen (por defecto se deriva del título).
3. Cada `## ` abre una PREGUNTA.
4. Cada línea `- ` es una OPCIÓN. Termina en ` *` (espacio + asterisco) para marcar la CORRECTA.
   Puede haber una o varias correctas (varias => pregunta de respuesta múltiple).
5. EXACTAMENTE 4 opciones por pregunta. Ni 3 ni 5: el proyecto fija 4 alternativas.
6. No puede haber opciones duplicadas ni una pregunta con todas las opciones correctas.

Sobre el orden: NO se decide aquí. La web baraja las 4 opciones en cada intento (y también
puede barajar las preguntas si `#Barajar preguntas: si`), de modo que la posición de la correcta
cambia y el alumno no puede acomodarse a "la respuesta es siempre la B".

Ejemplo mínimo válido: `fuentes/tema1-fundamentos-grupoA.md`.

---

## 3. Convertir (paso obligatorio antes de publicar)

    python3 herramientas/convertir.py            # valida y escribe data/
    python3 herramientas/convertir.py --check     # solo valida, no escribe

Salida esperada (ejemplo):

    OK: 2 examen(es), 6 pregunta(s) en total.
      - tema1-fundamentos-grupoa: Tema 1 — Fundamentos (grupo A) (3 preguntas) [grupo A]
      - tema1-fundamentos-grupob: Tema 1 — Fundamentos (grupo B) (3 preguntas) [grupo B]

Si hay errores, el script los lista con fichero y línea y sale con código 1 sin escribir nada.
No se publica nada hasta que la conversión pasa.

`convertir.py` borra y regenera TODOS los JSON de `data/examenes/`, así no quedan exámenes
huérfanos de fuentes eliminadas. `data/index.json` se regenera con la lista completa.

---

## 4. Probar en local antes de publicar

    python3 -m http.server 8765
    # abrir http://localhost:8765            (listado)
    #      http://localhost:8765/?grupo=A    (solo exámenes del grupo A)
    #      http://localhost:8765/?examen=<id>

El examen se autocorrige al pulsar "Corregir"; "Reiniciar" vuelve a barajar las opciones.

---

## 5. Publicar (elegir un modo)

### Modo A — git (lo normal)

    # una sola vez:
    git remote add origin https://github.com/<usuario>/<repo>.git   # si no lo tiene
    # cada vez:
    python3 herramientas/publicar.py -m "Nuevo examen tema 2"

`publicar.py` convierte, hace commit y hace push. Si el remoto pide autenticación, exporta
antes el token:  `export GITHUB_TOKEN=ghp_...`  (se pasa a git con un GIT_ASKPASS temporal,
nunca en la URL ni en la línea de comandos).

### Modo B — API de GitHub Contents (sin clonar el repo)

Sirve para subir/actualizar solo los JSON de `data/` con una llamada PUT por fichero:

    GITHUB_TOKEN=ghp_... python3 herramientas/publicar.py --api --repo usuario/repo -m "tema 2 alta"

Útil si editas el examen en otro sitio y no quieres clonar todo el repositorio.

### Activar GitHub Pages (una sola vez, web de GitHub)

Settings > Pages > Source: "Deploy from a branch" > rama `main`, carpeta `/ (root)` > Save.
La URL pública será `https://<usuario>.github.io/<repo>/`. Repositorio PÚBLICO (Pages privado
requiere plan de pago).

### Tras publicar (verificación mínima)

- `curl -sI https://<usuario>.github.io/<repo>/data/index.json` debe dar 200.
- Abrir la URL en el navegador y comprobar que el examen carga y corrige.

---

## 6. Varios grupos / dos tests el mismo día

- Cada test es un fichero `.md` distinto => un JSON distinto => un enlace distinto.
- Con `#Grupo: A` / `#Grupo: B` la web puede mostrar solo los del grupo:
  da al grupo A `.../?grupo=A` y al grupo B `.../?grupo=B` (o el enlace directo `?examen=<id>`).
- TODO esto cabe en UN SOLO repositorio (un solo despliegue de Pages). NO hace falta un segundo
  remoto para tener dos tests distintos el mismo día.
- Un segundo repositorio solo aporta algo si quieres que un grupo no vea ni el listado del otro
  (catálogos totalmente separados) o si publicas con cuentas/organizaciones distintas. En ese
  caso se puede empujar el mismo repo a dos remotos:
      git remote add grupoB https://github.com/<usuario>/<repoB>.git
      git push grupoB main
  Pero para "dos tests el mismo día" es esfuerzo innecesario.

---

## 7. Cómo responder al profesor (guion)

- "¿Puedo tener dos tests distintos el mismo día para dos grupos?" -> Sí. Dos ficheros `.md`,
  un `#Grupo:` en cada uno, la misma web. Un repo basta; cada grupo recibe su enlace.
- "¿Necesitan cuenta los alumnos?" -> No. Solo abren el enlace. Tú sí necesitas cuenta de GitHub.
- "¿Se guardan las notas?" -> No. La corrección es local en el navegador; no se envía nada.
- "¿Y si un alumno ve las respuestas?" -> El repo es público, así que las respuestas están en el
  JSON. Para PRACTICAR no importa; para un examen evaluable con nota, este montaje no sirve.
- "¿Cuántas preguntas?" -> Sin límite. Solo se exige que cada pregunta tenga 4 opciones.
- "¿La respuesta correcta sale siempre en el mismo sitio?" -> No: las opciones se barajan en cada
  intento.

---

## 8. Preguntas frecuentes técnicas

- Editar `data/*.json` a mano: no. Se sobrescribe. Edita `fuentes/*.md` y reconvierte.
- Añadir un examen: crear `fuentes/<algo>.md`, ejecutar `convertir.py`, publicar.
- Borrar un examen: borrar su `fuentes/<algo>.md`, reconvertir, publicar.
- Poner imágenes dentro de una pregunta: no está soportado en el formato de texto actual; habría
  que ampliar `index.html` y el conversor (pedirlo como mejora).
- Penalización por fallo: no la hay; la puntuación es `aciertos / total`. Se puede añadir.
