# TEST_ALUMNOS — tests de práctica autocorregibles, sin cuentas

Web estática para que los alumnos practiquen con tests tipo test hechos por el profesor.
Cada alumno abre un enlace, hace el test y ve su nota **en su propio navegador**.
No hay cuentas, no hay servidor, no se guarda ninguna puntuación.

## Idea

    fuentes/*.md   --convertir.py-->   data/*.json   --git push-->   GitHub Pages

Escribes el test en texto plano (rápido), un script lo convierte a JSON y lo publicas con un
`push`. El motor (`index.html`) no se toca nunca al añadir exámenes.

## Uso rápido

    # 1. Escribir un examen
    nano fuentes/tema2.md

    # 2. Convertir (valida el formato)
    python3 herramientas/convertir.py

    # 3. Probar en local
    #    OJO: abrir index.html con doble clic (file://) NO funciona: el navegador
    #    bloquea la lectura de los JSON. Hace falta servirlo por HTTP.
    python3 herramientas/servidor.py     # abre http://127.0.0.1:8765

    # 4. Publicar
    python3 herramientas/publicar.py -m "Nuevo examen tema 2"

## Reglas del proyecto

- **4 alternativas por pregunta**, siempre (lo valida el conversor).
- La **posición de la respuesta correcta es aleatoria**: las 4 opciones se barajan en cada
  intento, para que el alumno no se acomode a una posición fija.
- **Sin límite** de preguntas por examen.
- Se admiten preguntas de **una o varias respuestas correctas**.
- Grupos: `#Grupo: A` en el .md permite dar a cada grupo su propio listado (`...?grupo=A`).

## Dos grupos, dos tests el mismo día

Dos ficheros `.md` distintos => dos JSON => dos enlaces. Un solo repositorio y un solo
despliegue de Pages bastan. (Un segundo repositorio solo si quieres catálogos totalmente
separados; no es necesario para esto.) Detalle en `docs/REFERENCIA_LLM.md`, sección 6.

## Documentación

- `docs/REFERENCIA_LLM.md` — formato de los tests, pasos de conversión y publicación, guion de
  respuestas al profesor. **Es el documento que debe leer un LLM** para operar el proyecto.
- `docs/ESQUEMA_JSON.md` — esquema exacto del JSON y del índice.

## Publicación (resumen)

- Repositorio **público** (Pages privado requiere plan de pago).
- Settings > Pages > Deploy from a branch > `main` / `/ (root)`.
- URL: `https://<usuario>.github.io/<repo>/`.
- Alternativa sin clonar: `publicar.py --api --repo usuario/repo` (API Contents de GitHub).

## Aviso de uso

El repositorio es público: las preguntas y las respuestas correctas están en el JSON. Vale para
**practicar**, no para un examen evaluable con nota.
