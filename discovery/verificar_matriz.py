"""Verifica la coherencia de discovery/matriz-ponderada.md contra los raw.

Solo stdlib (Python 3.11+). Sin dependencias.

Comprueba:
  (a) cada producto de los raw aparece en la matriz (y no hay extras);
  (b) las notas están en rango 0-5 y son múltiplos de 0.5;
  (c) los pesos de cada ficha suman 100%;
  (d) el ponderado de la matriz coincide con el recalculado (tolerancia 0.01);
  (e) ningún producto duplicado.

Salida: "OK: N productos verificados" o la lista de errores. Código 1 si falla.
"""
import re
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

BASE = Path(__file__).resolve().parent
RAW_DIR = BASE / "raw"
RAW_FILES = ("argentina.md", "latam.md", "internacional.md")
MATRIZ = BASE / "matriz-ponderada.md"

PESOS = [Decimal(p) for p in ("0.25", "0.20", "0.15", "0.15", "0.10", "0.10", "0.05")]
PASO = Decimal("0.5")
ESPERADOS = 33
TOL = Decimal("0.011")
DOS_DEC = Decimal("0.01")

FICHA = re.compile(r"^###\s+\d+\.\s+(.+?)\s*$")
NOTA = re.compile(r"^\s*-\s+(.+?)\s*\((\d+)%\):\s*\*\*([\d.]+)\*\*")


def numero(texto):
    return Decimal(texto.strip().replace(",", "."))


def redondear(valor):
    return valor.quantize(DOS_DEC, rounding=ROUND_HALF_UP)


def nombre_producto(heading):
    return heading.split(" — ")[0].strip()


def parse_raw(path):
    """Devuelve {producto: [(criterio, peso_pct, nota), ...]} de las fichas '### N. ...'."""
    productos = {}
    actual = None
    for linea in path.read_text(encoding="utf-8").splitlines():
        m = FICHA.match(linea)
        if m:
            actual = nombre_producto(m.group(1))
            productos.setdefault(actual, [])
            continue
        if actual is None:
            continue
        n = NOTA.match(linea)
        if n:
            productos[actual].append((n.group(1).strip(), int(n.group(2)), numero(n.group(3))))
    return productos


def parse_matriz(path):
    """Devuelve la lista de celdas de cada fila numerada de la tabla."""
    filas = []
    for linea in path.read_text(encoding="utf-8").splitlines():
        if not linea.strip().startswith("|"):
            continue
        celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
        if len(celdas) == 14 and re.fullmatch(r"\d+", celdas[0]):
            filas.append(celdas)
    return filas


def main():
    errores = []

    # --- Parseo de los raw ---
    raw_orden = []
    raw_datos = {}
    for archivo in RAW_FILES:
        path = RAW_DIR / archivo
        if not path.exists():
            errores.append(f"no existe {path}")
            continue
        for producto, notas in parse_raw(path).items():
            if producto in raw_datos:
                errores.append(f"producto duplicado en raw: {producto}")
            raw_datos[producto] = notas
            raw_orden.append((producto, archivo))

    # (c) pesos suman 100% y (b) notas en rango y paso por ficha del raw
    for producto, notas in raw_datos.items():
        if len(notas) != 7:
            errores.append(f"{producto}: tiene {len(notas)} notas en el raw (se esperaban 7) [puntuación incompleta]")
        suma_pesos = sum(p for _, p, _ in notas)
        if suma_pesos != 100:
            errores.append(f"{producto}: los pesos del raw suman {suma_pesos}% (no 100%)")
        for criterio, _peso, nota in notas:
            if nota < 0 or nota > 5:
                errores.append(f"{producto}/{criterio}: nota fuera de rango 0-5 ({nota})")
            if (nota % PASO) != 0:
                errores.append(f"{producto}/{criterio}: nota {nota} no es múltiplo de {PASO}")

    # --- Parseo de la matriz ---
    filas = parse_matriz(MATRIZ) if MATRIZ.exists() else []
    if not MATRIZ.exists():
        errores.append(f"no existe {MATRIZ}")
    if len(filas) != ESPERADOS:
        errores.append(f"se esperaban {ESPERADOS} productos en la matriz y hay {len(filas)}")

    matriz_datos = {}
    matriz_orden = []
    calculados = []
    for celdas in filas:
        rank, producto = celdas[0], celdas[1]
        notas_celdas = celdas[4:11]
        ponderado_celda = celdas[11]
        if producto in matriz_datos:
            errores.append(f"producto duplicado en la matriz: {producto}")
        try:
            notas = [numero(c) for c in notas_celdas]
            ponderado = numero(ponderado_celda)
        except Exception:
            errores.append(f"{producto}: no se pudieron leer las notas/ponderado {notas_celdas} / {ponderado_celda}")
            continue
        matriz_datos[producto] = notas
        matriz_orden.append(int(rank))

        # (d) total ponderado recalculado
        total = sum(n * p for n, p in zip(notas, PESOS))
        if abs(total - ponderado) > TOL:
            errores.append(
                f"{producto}: ponderado de la matriz {ponderado} != recalculado {redondear(total)} "
                f"(notas {[str(n) for n in notas]})"
            )
        calculados.append((producto, ponderado, total))

        # (a) la fila de la matriz tiene que existir como ficha del raw
        if producto not in raw_datos:
            errores.append(f"{producto}: aparece en la matriz pero no en ningún raw")

    # (a) cada producto de los raw aparece en la matriz
    for producto, archivo in raw_orden:
        if producto not in matriz_datos:
            errores.append(f"{producto} (raw/{archivo}): NO aparece en la matriz")

    # Orden descendente por ponderado (no creciente)
    ponderados_orden = [p for _, p, _ in calculados]
    if ponderados_orden != sorted(ponderados_orden, reverse=True):
        errores.append("la matriz no está ordenada por ponderado descendente")

    # --- Reporte por producto ---
    for producto, ponderado, total in calculados:
        print(f"{producto:24} {[str(n) for n in matriz_datos[producto]]} -> {redondear(total):>4} (matriz {ponderado:>4})")

    print()
    if errores:
        print(f"FALLA: {len(errores)} discrepancia(s)")
        for e in errores:
            print(" -", e)
        sys.exit(1)
    print(f"OK: {len(filas)} productos verificados contra los 3 raw, sin discrepancias")


if __name__ == "__main__":
    main()
