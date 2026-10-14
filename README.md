# TEST_ALUMNOS — tests de práctica autocorregibles, sin cuentas

Web estática para que los alumnos practiquen con tests tipo test hechos por el profesor.
Cada alumno abre un enlace, hace el test y ve su nota en su propio navegador.
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
    python3 herramientas/servidor.py     # abre http://127.0.0.1:8765

    # 4. Publicar
    python3 herramientas/publicar.py -m "Nuevo examen tema 2"

## Reglas del proyecto

- **4 alternativas por pregunta**, siempre (lo valida el conversor).
- La **posición de la respuesta correcta es aleatoria**: las 4 opciones se barajan en cada
  intento, para que el alumno no se acomode a una posición fija.
- **Sin límite** de preguntas por examen. Los tests se muestran **paginados** (10 preguntas por
  pantalla; `#Por página: N` en el .md para cambiarlo, o el selector de la propia web).
- Las respuestas del alumno **se conservan** al cambiar de página, al volver atrás y al recargar
  (se guardan en el navegador del alumno; nunca se envían).
- El alumno puede **exportar el test completo** a su dispositivo: PDF, HTML offline autocorregible
  (funciona sin internet), JSON, CSV/Excel o texto.
- Se admiten preguntas de **una o varias respuestas correctas**.
- Grupos: `#Grupo: A` en el .md permite dar a cada grupo su propio listado (`...?grupo=A`).
- Visibilidad: `#Visible: si|no` en el .md. Con `no` el examen no aparece en el listado (ni se abre
  por enlace directo). Un solo cambio en el `.md`, reconvertir y publicar.

## Documentación

- `docs/REFERENCIA_LLM.md` — formato de los tests, pasos de conversión y publicación, guion de
  respuestas al profesor. **Es el documento que debe leer un LLM** para operar el proyecto.
- `docs/ESQUEMA_JSON.md` — esquema exacto del JSON y del índice.

## Publicación (resumen)

- Settings > Pages > Deploy from a branch > `main` / `/ (root)`.
- URL: `https://<usuario>.github.io/<repo>/`.
- Ya configurado: el workflow `.github/workflows/convertir.yml` reconvierte `fuentes/` -> `data/` y
  publica solo en cada push a `main`. También si editas un `.md` desde la web de GitHub y confirmas.
- Alternativa sin clonar: `publicar.py --api --repo usuario/repo` (API Contents de GitHub).

## Aviso de uso

El repositorio es público: las preguntas y las respuestas correctas están en el JSON. Vale para
**practicar**, no para un examen evaluable con nota.
