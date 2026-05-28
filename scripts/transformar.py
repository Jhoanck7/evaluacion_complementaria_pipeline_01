"""Módulo en el cual se agregan atributos, tales como el promedio, los estudiantes
aprobados y las categorias en la que se encuentran.

Este script lee los datos imputados, realiza transformaciones utilizando Polars
y exporta los resultados procesados a la carpeta correspondiente.
"""

import polars as pl

ruta_entrada = "data/interim/imputado.csv"
ruta_salida = "data/processed/transformado.csv"


def agregar_promedio(df: pl.DataFrame) -> pl.DataFrame:
    """Función que suma las columnas de notas de los estudiantes, dividendolo entre la
    la cantidad total, obtener el promedio, y se guarda esto con la función
    .with_columns()
    """
    df_con_promedio = df.with_columns(
        ((pl.col("nota1") + pl.col("nota2") + pl.col("nota3")) / 3)
        .round(2)
        .alias("promedio")
    )
    return df_con_promedio


def agregar_aprobado(df: pl.DataFrame) -> pl.DataFrame:
    """Función que guarda un booleano True o False, el estado de aprobado de los
    estudiantes, y se guarda esto con la función
    .with_columns()
    """
    df_con_aprobado = df.with_columns((pl.col("promedio") >= 4.0).alias("aprobado"))
    return df_con_aprobado


def agregar_categoria(df: pl.DataFrame) -> pl.DataFrame:
    """Función que guarda el estado del estudiante dependiendo su nota, esto lo hace con
     .when() y .then() que funciona como condicionales y se guarda esto con la función
    .with_columns()
    """
    df_con_categoria = df.with_columns(
        pl.when(pl.col("promedio") >= 6.0)
        .then(pl.lit("Destacado"))
        .when(pl.col("promedio") >= 4.0)
        .then(pl.lit("Aprobado"))
        .otherwise(pl.lit("Reprobado"))
        .alias("categoria")
    )
    return df_con_categoria


def cargar_datos(ruta: str) -> pl.DataFrame:
    """Carga los datos en modo Lazy y los recolecta en un DataFrame."""
    # Usamos scan_csv().collect() para el uso idiomático y obtener el DataFrame
    return pl.scan_csv(ruta).collect()


def main() -> None:
    """Función principal que ejecuta el pipeline de transformación."""

    # 1. Cargar
    df = cargar_datos(ruta_entrada)

    # 2. Transformar secuencialmente
    df = agregar_promedio(df)
    df = agregar_aprobado(df)
    df = agregar_categoria(df)

    # 3. Guardar el resultado final
    df.write_csv(ruta_salida)
    print(f"¡Transformación completada con éxito en: {ruta_salida}!")


if __name__ == "__main__":
    main()
