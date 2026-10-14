#!/usr/bin/env python3
"""Convierte un banco de preguntas en texto (.md) al JSON que consume la web.

Formato de cada fichero en `fuentes/` (texto plano, se edita rápido):

    # Título del examen
    #Descripción: texto opcional que sale en el listado
    #Grupo: A
    #Barajar preguntas: no
    #Visible: si
    #Por página: 10

    ## Enunciado de la pregunta
    - opción incorrecta
    - opción correcta *
    - otra opción
    - otra opción

    ## Otra pregunta
    - correcta A *
    - incorrecta
    - correcta B *
    - incorrecta

Reglas del formato:
  * La primera línea "# " es el TÍTULO del examen (obligatorio).
  * Directivas opcionales:  "#Descripción: ...", "#Grupo: A", "#Barajar preguntas: si|no",
                            "#Visible: si|no" (si no, el examen NO sale en el listado del alumno),
                            "#Por página: 10" (preguntas por pantalla en la web).
  * Cada "## " abre una PREGUNTA.
  * Cada línea "- " es una OPCIÓN. Marca con un " *" al final las correctas.
  * EXACTAMENTE 4 opciones por pregunta (se valida; error si no son 4).
  * Una o varias opciones con " *" (varias => pregunta de respuesta múltiple).

El orden de las opciones y la posición de la correcta NO se fijan aquí: la web las
baraja en cada intento para que el estudiante no se acomode a una posición fija.

Uso:
    python3 herramientas/convertir.py            # convierte todo fuentes/*.md
    python3 herramientas/convertir.py --check     # solo valida, no escribe nada

Escribe:
    data/examenes/<id>.json     (un fichero por examen)
    data/index.json             (índice que lee la web)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FUENTES = RAIZ / "fuentes"
SALIDA = RAIZ / "data" / "examenes"
INDICE = RAIZ / "data" / "index.json"

NUM_OPCIONES = 4  # criterio del proyecto: siempre 4 alternativas
DIRECTIVAS = {
    "descripcion": "description",
    "description": "description",
    "grupo": "grupo",
    "barajar preguntas": "barajar_preguntas",
    "barajar_preguntas": "barajar_preguntas",
    "visible": "visible",
    "oculto": "visible",
    "por pagina": "preguntas_por_pagina",
    "preguntas por pagina": "preguntas_por_pagina",
    "preguntas_por_pagina": "preguntas_por_pagina",
    "slug": "slug",
    "id": "slug",
}


def slug(texto: str) -> str:
    base = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    base = re.sub(r"[^a-zA-Z0-9]+", "-", base).strip("-").lower()
    return base or "examen"


def sin_acentos(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()


def parsear_bool(valor: str) -> bool:
    return valor.strip().lower() in {"si", "sí", "s", "true", "1", "yes", "y"}


def parsear(texto: str, origen: str) -> dict:
    titulo = None
    meta: dict = {}
    preguntas: list[dict] = []
    actual = None
    errores: list[str] = []

    for n, linea in enumerate(texto.splitlines(), 1):
        s = linea.strip()
        if not s:
            continue

        m_dir = re.match(r"^#\s*([^:]+):\s*(.+)$", s)
        if m_dir and not s.startswith("## "):
            clave = sin_acentos(m_dir.group(1).strip().lower())
            valor = m_dir.group(2).strip()
            destino = DIRECTIVAS.get(clave)
            if destino:
                if destino == "barajar_preguntas":
                    meta[destino] = parsear_bool(valor)
                elif destino == "visible":
                    # "#Oculto: si" es lo mismo que "#Visible: no"
                    if sin_acentos(m_dir.group(1).strip().lower()) == "oculto":
                        meta[destino] = not parsear_bool(valor)
                    else:
                        meta[destino] = parsear_bool(valor)
                elif destino == "preguntas_por_pagina":
                    if re.fullmatch(r"\d+", valor) and int(valor) > 0:
                        meta[destino] = int(valor)
                    else:
                        errores.append(
                            f"{origen}:{n}: '#Por página:' necesita un entero mayor que 0, no {valor!r}")
                else:
                    meta[destino] = valor
                continue

        if s.startswith("## "):
            if actual is not None:
                preguntas.append(actual)
            actual = {"text": s[3:].strip(), "options": [], "correct_indices": []}
            continue

        if s.startswith("# "):
            if titulo is None:
                titulo = s[2:].strip()
            else:
                errores.append(f"{origen}:{n}: segundo título '# ' ignorado")
            continue

        if s.startswith("- "):
            if actual is None:
                errores.append(f"{origen}:{n}: opción fuera de una pregunta '## '")
                continue
            valor = s[2:].strip()
            correcta = valor.endswith("*")
            if correcta:
                valor = valor[:-1].strip()
            actual["options"].append(valor)
            if correcta:
                actual["correct_indices"].append(len(actual["options"]) - 1)
            continue

        errores.append(f"{origen}:{n}: línea no reconocida -> {s!r}")

    if actual is not None:
        preguntas.append(actual)

    if not titulo:
        errores.append(f"{origen}: falta el título '# '")

    if not preguntas:
        errores.append(f"{origen}: no hay ninguna pregunta ('## ')")

    for i, p in enumerate(preguntas, 1):
        p["id"] = i
        ops = p["options"]
        if len(ops) != NUM_OPCIONES:
            errores.append(f"{origen}: pregunta {i}: {len(ops)} opciones (deben ser exactamente {NUM_OPCIONES})")
        if not p["correct_indices"]:
            errores.append(f"{origen}: pregunta {i}: ninguna opción marcada con '*'")
        if len(p["correct_indices"]) == len(ops) and ops:
            errores.append(f"{origen}: pregunta {i}: todas las opciones son correctas (no puede ser)")
        if len(set(ops)) != len(ops):
            errores.append(f"{origen}: pregunta {i}: hay opciones duplicadas")
        p["type"] = "multiple" if len(p["correct_indices"]) > 1 else "single"

    ex_id = meta.get("slug") or slug(titulo or origen)
    datos = {
        "id": ex_id,
        "title": titulo or origen,
        "description": meta.get("description", ""),
        "grupo": meta.get("grupo", ""),
        "visible": meta.get("visible", True),
        "barajar_preguntas": meta.get("barajar_preguntas", False),
        "shuffle_options": True,
    }
    # solo se escribe si el .md lo pide: los exámenes sin la directiva no cambian
    if "preguntas_por_pagina" in meta:
        datos["preguntas_por_pagina"] = meta["preguntas_por_pagina"]
    datos["questions"] = preguntas
    datos["_errores"] = errores
    return datos


def main() -> int:
    ap = argparse.ArgumentParser(description="Convierte fuentes/*.md -> data/*.json")
    ap.add_argument("--check", action="store_true", help="solo validar, no escribir")
    args = ap.parse_args()

    if not FUENTES.is_dir():
        print(f"No existe la carpeta de fuentes: {FUENTES}", file=sys.stderr)
        return 2

    ficheros = sorted(FUENTES.glob("*.md"))
    if not ficheros:
        print(f"No hay ficheros .md en {FUENTES}", file=sys.stderr)
        return 2

    examenes: list[dict] = []
    todos: list[str] = []

    for f in ficheros:
        datos = parsear(f.read_text(encoding="utf-8"), f.name)
        todos.extend(datos.pop("_errores"))
        if any(e["id"] == datos["id"] for e in examenes):
            todos.append(f"{f.name}: id duplicado '{datos['id']}' (usa '#Slug:' para diferenciarlo)")
        examenes.append(datos)

    if todos:
        print("ERRORES de formato:", file=sys.stderr)
        for e in todos:
            print("  -", e, file=sys.stderr)
        print("\nCorrige los ficheros de fuentes/ y vuelve a ejecutar.", file=sys.stderr)
        return 1

    total_preguntas = sum(len(e["questions"]) for e in examenes)
    print(f"OK: {len(examenes)} examen(es), {total_preguntas} pregunta(s) en total.")
    for e in examenes:
        g = f" [grupo {e['grupo']}]" if e["grupo"] else ""
        print(f"  - {e['id']}: {e['title']} ({len(e['questions'])} preguntas){g}")

    if args.check:
        print("(--check: no se ha escrito nada)")
        return 0

    (RAIZ / "data").mkdir(parents=True, exist_ok=True)
    SALIDA.mkdir(parents=True, exist_ok=True)

    # limpia JSON antiguos para no dejar exámenes huérfanos de fuentes borradas
    for viejo in SALIDA.glob("*.json"):
        viejo.unlink()

    for e in examenes:
        (SALIDA / f"{e['id']}.json").write_text(
            json.dumps(e, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    indice = {"examenes": [
        {"id": e["id"], "title": e["title"], "description": e["description"],
         "grupo": e["grupo"], "visible": e.get("visible", True),
         "num_preguntas": len(e["questions"]),
         "archivo": f"data/examenes/{e['id']}.json"}
        for e in examenes]}
    INDICE.write_text(json.dumps(indice, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Escrito: {INDICE} y {len(examenes)} fichero(s) en {SALIDA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
