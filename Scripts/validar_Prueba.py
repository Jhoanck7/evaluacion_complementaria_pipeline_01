"""Script 1 del pipeline: validación del dataset de estudiantes.

Lee el archivo crudo, detecta valores faltantes y fuera de rango,
y genera dos archivos de salida: un CSV validado y un reporte en texto.
"""

import os

import polars as pl

# Carpeta raíz del proyecto: es la carpeta que está UN nivel arriba de Scripts/
# __file__ es la ruta completa de este script (validar.py)
# os.path.dirname(...) sube un nivel en la carpeta
# Entonces PROJECT_ROOT apunta siempre a tarea1/, sin importar desde dónde se ejecute
PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Rutas de entrada y salida construidas a partir de la raíz del proyecto
INPUT_PATH: str = os.path.join(PROJECT_ROOT, "data", "raw", "estudiantes.csv")
OUTPUT_CSV: str = os.path.join(PROJECT_ROOT, "data", "interim", "validado.csv")
OUTPUT_REPORTE: str = os.path.join(
    PROJECT_ROOT, "data", "interim", "reporte_validacion.txt"
)

# Rango válido para notas en el sistema chileno
NOTA_MIN: float = 1.0
NOTA_MAX: float = 7.0

# Rango válido para asistencia (porcentaje)
ASISTENCIA_MIN: float = 0.0
ASISTENCIA_MAX: float = 100.0

# Columnas que corresponden a notas
COLUMNAS_NOTAS: list[str] = ["nota1", "nota2", "nota3"]


def leer_dataset(ruta: str) -> pl.DataFrame:
    """Lee el CSV de estudiantes y lo retorna como DataFrame de Polars."""
    df = pl.read_csv(ruta, null_values=["", "NA", "N/A"])
    return df


def agregar_columna_faltantes(df: pl.DataFrame) -> pl.DataFrame:
    """Agrega la columna tiene_faltantes (True si la fila tiene algún nulo)."""
    columnas_datos: list[str] = ["nota1", "nota2", "nota3", "asistencia"]

    # Para cada columna verificamos si es nula y luego hacemos OR entre todas
    tiene_faltantes = pl.lit(False)
    for col in columnas_datos:
        tiene_faltantes = tiene_faltantes | pl.col(col).is_null()

    df_con_flag = df.with_columns(tiene_faltantes.alias("tiene_faltantes"))
    return df_con_flag


def contar_faltantes_por_columna(df: pl.DataFrame) -> dict[str, int]:
    """Cuenta cuántos valores nulos hay en cada columna del DataFrame."""
    conteo: dict[str, int] = {}
    for col in df.columns:
        n_nulos = df[col].null_count()
        conteo[col] = n_nulos
    return conteo


def obtener_filas_con_faltantes(df: pl.DataFrame) -> list[str]:
    """Retorna una lista de nombres de estudiantes que tienen al menos un valor nulo."""
    filas_con_nulos = df.filter(pl.col("tiene_faltantes"))
    nombres: list[str] = filas_con_nulos["nombre"].to_list()
    return nombres


def detectar_valores_fuera_de_rango(df: pl.DataFrame) -> list[str]:
    """
    Detecta valores que están fuera del rango esperado.

    Para notas: entre 1.0 y 7.0 (sistema chileno).
    Para asistencia: entre 0 y 100 (porcentaje).

    Retorna una lista de strings describiendo cada anomalía encontrada.
    """
    anomalias: list[str] = []

    # Revisar cada columna de notas
    for col in COLUMNAS_NOTAS:
        # Filtramos filas donde la nota no es nula pero está fuera de rango
        fuera = df.filter(
            pl.col(col).is_not_null()
            & ((pl.col(col) < NOTA_MIN) | (pl.col(col) > NOTA_MAX))
        )
        for fila in fuera.iter_rows(named=True):
            mensaje = (
                f"  - Estudiante '{fila['nombre']}': "
                f"{col} = {fila[col]} (fuera de [{NOTA_MIN}, {NOTA_MAX}])"
            )
            anomalias.append(mensaje)

    # Revisar columna de asistencia
    fuera_asistencia = df.filter(
        pl.col("asistencia").is_not_null()
        & (
            (pl.col("asistencia") < ASISTENCIA_MIN)
            | (pl.col("asistencia") > ASISTENCIA_MAX)
        )
    )
    for fila in fuera_asistencia.iter_rows(named=True):
        mensaje = (
            f"  - Estudiante '{fila['nombre']}': "
            f"asistencia = {fila['asistencia']} "
            f"(fuera de [{ASISTENCIA_MIN}, {ASISTENCIA_MAX}])"
        )
        anomalias.append(mensaje)

    return anomalias


def generar_reporte(
    df: pl.DataFrame,
    conteo_faltantes: dict[str, int],
    filas_con_faltantes: list[str],
    anomalias: list[str],
    ruta_salida: str,
) -> None:
    """Genera el reporte de validación en texto plano y lo guarda en disco."""
    lineas: list[str] = []

    lineas.append("=" * 55)
    lineas.append("REPORTE DE VALIDACIÓN — DATASET DE ESTUDIANTES")
    lineas.append("=" * 55)
    lineas.append("")

    # Resumen general
    total_filas = df.shape[0]
    total_cols = df.shape[1]
    lineas.append(f"Total de filas en el dataset : {total_filas}")
    lineas.append(f"Total de columnas            : {total_cols}")
    lineas.append("")

    # Valores faltantes por columna
    lineas.append("-" * 55)
    lineas.append("VALORES FALTANTES POR COLUMNA")
    lineas.append("-" * 55)
    for col, cantidad in conteo_faltantes.items():
        estado = f"{cantidad} faltante(s)" if cantidad > 0 else "sin faltantes"
        lineas.append(f"  {col:<20}: {estado}")
    lineas.append("")

    # Filas con valores faltantes
    lineas.append("-" * 55)
    lineas.append("FILAS CON AL MENOS UN VALOR FALTANTE")
    lineas.append("-" * 55)
    if filas_con_faltantes:
        for nombre in filas_con_faltantes:
            lineas.append(f"  - {nombre}")
    else:
        lineas.append("  (ninguna fila tiene valores faltantes)")
    lineas.append("")

    # Valores fuera de rango
    lineas.append("-" * 55)
    lineas.append("VALORES FUERA DEL RANGO ESPERADO")
    lineas.append("-" * 55)
    if anomalias:
        for anomalia in anomalias:
            lineas.append(anomalia)
    else:
        lineas.append("  (no se detectaron valores fuera de rango)")
    lineas.append("")

    lineas.append("=" * 55)
    lineas.append("Fin del reporte.")
    lineas.append("=" * 55)

    contenido: str = "\n".join(lineas)
    with open(ruta_salida, "w", encoding="utf-8") as archivo:
        archivo.write(contenido)

    print(f"Reporte de validación guardado en: {ruta_salida}")


def guardar_csv_validado(df: pl.DataFrame, ruta_salida: str) -> None:
    """Guarda el DataFrame validado (con la columna tiene_faltantes) en disco."""
    df.write_csv(ruta_salida)
    print(f"CSV validado guardado en: {ruta_salida}")


def main() -> None:
    """Función principal que ejecuta el flujo completo de validación."""
    # Crear directorio de salida si no existe, usando la ruta absoluta
    interim_dir: str = os.path.join(PROJECT_ROOT, "data", "interim")
    os.makedirs(interim_dir, exist_ok=True)

    print("Leyendo dataset de entrada...")
    df = leer_dataset(INPUT_PATH)

    print("Agregando columna de valores faltantes...")
    df = agregar_columna_faltantes(df)

    print("Analizando calidad de los datos...")
    conteo_faltantes = contar_faltantes_por_columna(df)
    filas_con_faltantes = obtener_filas_con_faltantes(df)
    anomalias = detectar_valores_fuera_de_rango(df)

    print("Guardando CSV validado...")
    guardar_csv_validado(df, OUTPUT_CSV)

    print("Generando reporte de validación...")
    generar_reporte(
        df, conteo_faltantes, filas_con_faltantes, anomalias, OUTPUT_REPORTE
    )

    print("Script validar.py finalizado correctamente.")


if __name__ == "__main__":
    main()
