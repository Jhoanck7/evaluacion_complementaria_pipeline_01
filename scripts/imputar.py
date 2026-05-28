import polars as pl

# Rutas de entrada y salida
INPUT_PATH: str = "data/interim/validado.csv"
OUTPUT_PATH: str = "data/interim/imputado.csv"

# Columnas de notas
COLUMNAS_NOTAS: list[str] = ["nota1", "nota2", "nota3"]

# Columna de asistencia
COLUMNA_ASISTENCIA: str = "asistencia"


# Lee validado.csv y lo retorna como dataframe de polars
def leer_dataset(ruta: str) -> pl.DataFrame:
    df = pl.read_csv(ruta, null_values=[""])
    return df


# Imputa los valores faltantes en las columnas de notas con la mediana de cada columna.
def imputar_notas_con_mediana(df: pl.DataFrame) -> pl.DataFrame:

    # Lista de expresiones, una por cada columna de notas,
    # que indican la tarea a realizar en cada columna
    instrucciones_imputacion = []

    for columna in COLUMNAS_NOTAS:
        # Calcula la mediana de la columna
        mediana = df[columna].median()

        # Crea la expresión: si el valor es nulo, se reemplaza por la mediana
        instruccion_columna = pl.col(columna).fill_null(mediana).alias(columna)
        instrucciones_imputacion.append(instruccion_columna)

    # Se aplican todas las instrucciones almacenadas al dataset
    df_imputado = df.with_columns(instrucciones_imputacion)
    # Retorna el nuevo dataset con los Null reemplazados
    return df_imputado


# Imputa los valores faltantes de asistencia con la media redondeada de la columna
def imputar_asistencia_con_media(df: pl.DataFrame) -> pl.DataFrame:

    # Cálculo de la media redondeada al entero más cercano
    media_asistencia = df[COLUMNA_ASISTENCIA].mean()
    media_redondeada = round(media_asistencia)

    # Reemplazamos los nulos de la columna de asistencia por la media redondeada
    df_imputado = df.with_columns(
        pl.col(COLUMNA_ASISTENCIA).fill_null(media_redondeada).alias(COLUMNA_ASISTENCIA)
    )
    # Retorna el nuevo dataset con los Null reemplazados
    return df_imputado


# Guarda el dataset con los null reemplazados en el disco duro en formato csv
def guardar_csv(df: pl.DataFrame, ruta: str) -> None:
    df.write_csv(ruta)
    print(f"CSV imputado guardado en: {ruta}")


# Ejecuta todas las funciones del archivo
def main() -> None:
    # Lee dataset original
    df = leer_dataset(INPUT_PATH)

    # Reemplaza los datos Null por la mediana y media
    df = imputar_notas_con_mediana(df)
    df = imputar_asistencia_con_media(df)

    # Guarda el archivo csv en la ruta definida
    guardar_csv(df, OUTPUT_PATH)

    print(" imputar.py se ejecutó correctamente")


# El codigo se ejecuta solo si es corrido directamente
if __name__ == "__main__":
    main()
