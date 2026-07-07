#!/usr/bin/env python3
"""Compila main.tex y genera casos_programacion_lineal.pdf en la carpeta raiz.

Uso:
    python compilar.py

Requiere una distribucion LaTeX instalada (MiKTeX o TeX Live) con
pdflatex y, opcionalmente, latexmk.
"""

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAIN_TEX = ROOT / "main.tex"
OUTPUT_PDF = ROOT / "casos_programacion_lineal.pdf"
BUILD_DIR = ROOT / "build"


def run(cmd):
    """Ejecuta un comando mostrando la orden y devuelve el codigo de salida."""
    print(">", " ".join(cmd))
    return subprocess.run(cmd, cwd=ROOT).returncode


def compile_with_latexmk():
    """Compila con latexmk (gestiona automaticamente las pasadas necesarias)."""
    cmd = [
        "latexmk",
        "-pdf",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-file-line-error",
        f"-output-directory={BUILD_DIR}",
        str(MAIN_TEX),
    ]
    return run(cmd)


def compile_with_pdflatex():
    """Compila con pdflatex realizando varias pasadas (indice/referencias)."""
    cmd = [
        "pdflatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-file-line-error",
        f"-output-directory={BUILD_DIR}",
        str(MAIN_TEX),
    ]
    rc = 0
    for _ in range(3):
        rc = run(cmd)
        if rc != 0:
            return rc
    return rc


def main():
    if not MAIN_TEX.exists():
        sys.exit(f"No se encuentra {MAIN_TEX}")

    BUILD_DIR.mkdir(exist_ok=True)

    if not shutil.which("latexmk") and not shutil.which("pdflatex"):
        sys.exit(
            "No se encontro 'latexmk' ni 'pdflatex'. "
            "Instala una distribucion LaTeX (MiKTeX o TeX Live)."
        )

    rc = 1
    if shutil.which("latexmk"):
        rc = compile_with_latexmk()
        if rc != 0 and shutil.which("pdflatex"):
            # latexmk puede fallar aunque exista (p. ej. MiKTeX sin Perl).
            # En ese caso reintentamos directamente con pdflatex.
            print("\nlatexmk fallo; reintentando con pdflatex...\n")
            rc = compile_with_pdflatex()
    else:
        rc = compile_with_pdflatex()

    built_pdf = BUILD_DIR / "main.pdf"
    if rc != 0 or not built_pdf.exists():
        sys.exit(f"La compilacion fallo (codigo {rc}). Revisa el log en {BUILD_DIR}.")

    # Movemos (no copiamos) el PDF fuera de build/ para dejar un unico PDF final.
    OUTPUT_PDF.unlink(missing_ok=True)
    shutil.move(str(built_pdf), str(OUTPUT_PDF))
    print(f"\nPDF generado: {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
