# Esquema JSON

Generado por `herramientas/convertir.py`. NO se edita a mano.

## data/index.json

    {
      "examenes": [
        {
          "id": "tema1-fundamentos-grupoa",   // identificador y clave de la URL (?examen=<id>)
          "title": "Tema 1 — Fundamentos (grupo A)",
          "description": "Repaso autoevaluable del tema 1",
          "grupo": "A",                        // "" si no se indicó
          "num_preguntas": 3,
          "archivo": "data/examenes/tema1-fundamentos-grupoa.json"
        }
      ]
    }

## data/examenes/<id>.json

    {
      "id": "tema1-fundamentos-grupoa",
      "title": "Tema 1 — Fundamentos (grupo A)",
      "description": "Repaso autoevaluable del tema 1",
      "grupo": "A",
      "barajar_preguntas": false,     // si true, la web mezcla el orden de las preguntas
      "shuffle_options": true,        // la web baraja SIEMPRE las opciones (4 por pregunta)
      "questions": [
        {
          "id": 1,
          "type": "single",           // "single" (1 correcta) | "multiple" (>1 correcta)
          "text": "¿Cuál de estos es un lenguaje de programación?",
          "options": ["HTML", "Python", "JSON", "CSS"],   // siempre 4
          "correct_indices": [1]      // índices (base 0) de las opciones correctas
        }
      ]
    }

Notas:
- `correct_indices` se refiere al orden ORIGINAL de `options`. La web baraja la presentación
  y traduce las marcas del alumno a estos índices para corregir.
- `type` se deduce del número de índices correctos.
- `id` se deriva del título (slug ASCII) salvo que se use `#Slug:` en el .md.
- El esquema de `questions[]` es compatible con el usado en `HTML/OPOTEST` (allí con
  `title`/`description` a nivel de examen y `correct_indices` por pregunta), para reutilizar
  materiales entre ambos proyectos.
