# Instrucciones para agentes LLM

Antes de cambiar nada en este proyecto, lee `docs/REFERENCIA_LLM.md`. Contiene el formato de los
tests, los comandos exactos de conversión y publicación, y el guion de respuestas al profesor.

Resumen operativo:

- Los tests se escriben en `fuentes/*.md` (NO tocar `data/`, que es generado).
- Convertir: `python3 herramientas/convertir.py` (o `--check` para solo validar).
- Publicar: `python3 herramientas/publicar.py -m "mensaje"` (o `--api` para la API Contents).
- Cada pregunta debe tener EXACTAMENTE 4 opciones; la correcta se marca con ` *` al final.
- `#Visible: no` en un `.md` oculta ese examen del listado del alumno (por defecto `si`).
- El orden de las opciones no se fija en el texto: la web las baraja en cada intento.
- `index.html` es el motor; no hace falta tocarlo para añadir exámenes.
