"""Módulo para generar el resumen estadístico del curso."""

import polars as pl

# Ruta de los archivos
INPUT_PATH: str = "data/processed/transformado.csv"
OUTPUT_PATH: str = "data/processed/resumen.txt"


def generar_estadisticas(df: pl.DataFrame) -> str:
    """Calcula las métricas requeridas utilizando expresiones de Polars.

    Retorna un string formateado listo para ser escrito en el archivo final.
    """
    # 1. Obtener métricas simples usando expresiones básicas
    total_estudiantes = df.height
    promedio_general = df["promedio"].mean()
    nota_minima = df["promedio"].min()
    nota_maxima = df["promedio"].max()
    promedio_asistencia = df["asistencia"].mean()

    # 2. Calcular porcentaje de aprobados
    cantidad_aprobados = df.filter(pl.col("aprobado")).height
    porcentaje_aprobados = (cantidad_aprobados / total_estudiantes) * 100
    # 3. Contar categorías (Destacado / Aprobado / Reprobado)
    conteo_destacados = df.filter(pl.col("categoria") == "Destacado").height
    conteo_aprobados = df.filter(pl.col("categoria") == "Aprobado").height
    conteo_reprobados = df.filter(pl.col("categoria") == "Reprobado").height

    # 4. Construir el reporte en texto plano (f-string)
    reporte = (
        f"--- RESUMEN DEL CURSO ---\n"
        f"Total de estudiantes procesados: {total_estudiantes}\n"
        f"Promedio general del curso: {promedio_general:.2f}\n"
        f"Nota miníma y máxima del curso: {nota_minima} y {nota_maxima}\n"
        f"Porcentaje de estudiantes aprobados: {porcentaje_aprobados}\n"
        f"Conteo por categoria:\n"
        f"  - Destacado: {conteo_destacados}\n"
        f"  - Aprobado: {conteo_aprobados}\n"
        f"  - Reprobado: {conteo_reprobados}\n"
        f"Promedio de asistencia del curso: {promedio_asistencia}"
    )

    return reporte


def main() -> None:
    """Función principal del script."""

    # Lectura y recolección
    df: pl.DataFrame = pl.scan_csv(INPUT_PATH).collect()

    # Generar el reporte
    contenido_reporte: str = generar_estadisticas(df)

    # Escritura en el archivo de texto
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(contenido_reporte)


if __name__ == "__main__":
    main()
