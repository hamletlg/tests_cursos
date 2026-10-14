#!/usr/bin/env python3
"""Publica los exámenes: convierte y sube el repositorio (git) o solo los JSON (API).

Dos modos:

  1) MODO GIT (por defecto)  ->  para el flujo normal del profesor
     Convierte fuentes/*.md, hace commit y push del repositorio completo.
         python3 herramientas/publicar.py -m "Nuevo examen tema 2"
     El token se toma de $GITHUB_TOKEN (o $GIT_TOKEN). Nunca se escribe en la URL
     ni en la línea de comandos: se pasa a git con GIT_ASKPASS temporal.

  2) MODO API (--api)  ->  autoría sin clonar el repo, subiendo solo los JSON
     Usa la API de GitHub "Contents" (PUT). Sirve para actualizar un examen
     concreto sin tener el repo a mano.
         GITHUB_TOKEN=... python3 herramientas/publicar.py --api --repo usuario/repo -m "tema 2 alta"

Requisitos modo git: git configurado y remoto 'origin' apuntando al repo.
Requisitos modo api: variable GITHUB_TOKEN con permiso de contenido sobre el repo.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
API = "https://api.github.com"


def ejecutar(cmd, **kw):
    print("+", " ".join(cmd))
    return subprocess.run(cmd, cwd=RAIZ, text=True, **kw)


def convertir() -> int:
    return ejecutar([sys.executable, str(RAIZ / "herramientas" / "convertir.py")]).returncode


def modo_git(mensaje: str, token: str | None) -> int:
    if ejecutar(["git", "add", "-A"]).returncode != 0:
        return 1
    if ejecutar(["git", "diff", "--cached", "--quiet"]).returncode != 0:
        if ejecutar(["git", "commit", "-m", mensaje]).returncode != 0:
            return 1
    else:
        # Sin cambios nuevos que commitear. Antes se salía aquí sin subir nada, así que un commit
        # local pendiente (por ejemplo, si el push anterior falló) se quedaba sin publicar.
        r = ejecutar(["git", "rev-list", "--count", "HEAD", "--not", "--remotes"],
                     stdout=subprocess.PIPE)
        pendientes = (r.stdout or "").strip()
        if r.returncode != 0 or pendientes == "0":
            print("No hay cambios que publicar.")
            return 0
        print(f"Sin cambios nuevos, pero hay {pendientes} commit(s) local(es) sin subir: se hace push.")

    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    askpass = None
    if token:
        fd, askpass = tempfile.mkstemp(prefix=".askpass-")
        os.close(fd)
        with open(askpass, "w", encoding="utf-8") as f:
            f.write("#!/bin/sh\n"
                    'case "$1" in\n'
                    "  *[Uu]sername*) echo x-access-token ;;\n"
                    f'  *) echo "{token}" ;;\n'
                    "esac\n")
        os.chmod(askpass, 0o700)
        env["GIT_ASKPASS"] = askpass
    try:
        r = ejecutar(["git", "push", "-u", "origin", "HEAD"], env=env,
                     stderr=subprocess.STDOUT)
        salida = (r.stdout or "")
        if token:
            salida = salida.replace(token, "***")
        print(salida)
        return r.returncode
    finally:
        if askpass:
            os.unlink(askpass)


def api_put(repo: str, ruta: str, contenido: bytes, mensaje: str, token: str) -> str:
    url = f"{API}/repos/{repo}/contents/{ruta}"
    sha = None
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "test-alumnos-publicar",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            sha = json.load(r).get("sha")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise

    cuerpo = {
        "message": mensaje,
        "content": base64.b64encode(contenido).decode("ascii"),
        "branch": "main",
    }
    if sha:
        cuerpo["sha"] = sha
    req = urllib.request.Request(url, data=json.dumps(cuerpo).encode(),
                                method="PUT", headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": "test-alumnos-publicar",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["commit"]["sha"]


def modo_api(repo: str, mensaje: str, token: str) -> int:
    ficheros = [RAIZ / "data" / "index.json"] + sorted((RAIZ / "data" / "examenes").glob("*.json"))
    for f in ficheros:
        ruta = f.relative_to(RAIZ).as_posix()
        try:
            sha = api_put(repo, ruta, f.read_bytes(), f"{mensaje} [{ruta}]", token)
            print(f"  ok {ruta} -> commit {sha[:8]}")
        except urllib.error.HTTPError as e:
            print(f"  ERROR {ruta}: HTTP {e.code} {e.read().decode(errors='replace')[:200]}",
                  file=sys.stderr)
            return 1
    print(f"Subidos {len(ficheros)} fichero(s) a {repo} por API.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Convierte y publica los exámenes.")
    ap.add_argument("-m", "--mensaje", default="Actualiza exámenes")
    ap.add_argument("--api", action="store_true", help="subir solo los JSON vía API Contents")
    ap.add_argument("--repo", help="owner/nombre (obligatorio en --api)")
    ap.add_argument("--sin-convertir", action="store_true", help="no ejecutar convertir.py antes")
    args = ap.parse_args()

    if not args.sin_convertir:
        if convertir() != 0:
            print("La conversión falló; no se publica nada.", file=sys.stderr)
            return 1

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GIT_TOKEN")

    if args.api:
        if not args.repo:
            print("--api requiere --repo owner/nombre", file=sys.stderr)
            return 2
        if not token:
            print("--api requiere GITHUB_TOKEN en el entorno", file=sys.stderr)
            return 2
        return modo_api(args.repo, args.mensaje, token)

    return modo_git(args.mensaje, token)


if __name__ == "__main__":
    raise SystemExit(main())
