import polars as pl
import os

# Rutas de entrada y salida
INPUT_PATH: str = "data/raw/estudiantes.csv"
OUTPUT_CSV: str = "data/interim/validado.csv"
OUTPUT_REPORTE: str = "data/interim/reporte_validacion.txt"

# Rango válido para las notas
NOTA_MIN: float = 1.0
NOTA_MAX: float = 7.0

# Rango válido para asistencia (porcentaje)
ASISTENCIA_MIN: float = 0.0
ASISTENCIA_MAX: float = 100.0

# Columnas que corresponden a notas
COLUMNAS_NOTAS: list[str] = ["nota1", "nota2", "nota3"]


def leer_dataset(ruta: str) -> pl.DataFrame:
    # Lee el CSV con los datos de notas y asistencias y lo retorna como DataFrame
    # de polars
    df = pl.read_csv(ruta, null_values=[""])
    return df


def agregar_columna_faltantes(df: pl.DataFrame) -> pl.DataFrame:
    # Agrega la columna tiene_faltantes: se asigna True si la fila tiene algún
    # dato faltante
    columnas_datos: list[str] = ["nota1", "nota2", "nota3", "asistencia"]

    # Para cada columna se verifica si tiene un valor nulo
    tiene_faltantes = pl.lit(False)  # Por defecto se asigna False (sin valores nulos)
    for col in columnas_datos:
        # Si al menos una columna tiene datos faltantes, entonces se asigna True
        tiene_faltantes = tiene_faltantes | pl.col(col).is_null()

    df_tiene_faltantes = df.with_columns(tiene_faltantes.alias("tiene_faltantes"))
    return df_tiene_faltantes


# Cuenta cuantos valores nulos hay en cada columna
def contar_faltantes_por_columna(df: pl.DataFrame) -> dict[str, int]:
    conteo: dict[str, int] = {}
    for col in df.columns:
        n_nulos = df[col].null_count()
        conteo[col] = n_nulos
    return conteo


# Retorna una lista solamente con el nombre de los estudiantes que tienen
# al menos un valor nulo
def obtener_filas_con_faltantes(df: pl.DataFrame) -> list[str]:
    filas_con_nulos = df.filter(pl.col("tiene_faltantes"))
    nombres: list[str] = filas_con_nulos["nombre"].to_list()
    return nombres


# Detecta si hay valores fuera del rango esperado: notas: 1.0 al 7.0 ; asistencia 0 al
# 100 Retorna una lista con errores encontrados
def detectar_valores_fuera_de_rango(df: pl.DataFrame) -> list[str]:

    datos_invalidos = []

    datos = df.to_dicts()

    for fila in datos:
        nombre_alumno = fila["nombre"]

        # Revisa las notas
        for columna_nota in COLUMNAS_NOTAS:
            valor_nota = fila[columna_nota]

            # Solo se revisa si la nota no es nula
            if valor_nota is not None:
                # Si la nota no se encuentra dentro de los limites,
                # se genera un mensaje de error.
                if valor_nota < NOTA_MIN or valor_nota > NOTA_MAX:
                    error = (
                        f"  Estudiante '{nombre_alumno}': "
                        f"{columna_nota} = {valor_nota} "
                        f"(fuera de [{NOTA_MIN}, {NOTA_MAX}])"
                    )
                    datos_invalidos.append(error)

        # Revisa la asistencia
        valor_asistencia = fila["asistencia"]

        # Revisa solo valores no nulos
        if valor_asistencia is not None:
            # Si la asistencia no se encuentra dentro del rango,
            # se genera un mensaje de error
            if valor_asistencia < ASISTENCIA_MIN or valor_asistencia > ASISTENCIA_MAX:
                error_asistencia = (
                    f"  Estudiante '{nombre_alumno}': "
                    f"asistencia = {valor_asistencia} "
                    f"(fuera de [{ASISTENCIA_MIN}, {ASISTENCIA_MAX}])"
                )
                datos_invalidos.append(error_asistencia)

    return datos_invalidos


"""""
Reporte que detalla cuántos valores faltantes hay por columna, 
qué filas los tienen y cualquier valor fuera del rango
esperado.
"""


def generar_reporte(
    df: pl.DataFrame,
    conteo_faltantes: dict[str, int],
    filas_con_faltantes: list[str],
    datos_invalidos: list[str],
    ruta_salida: str,
) -> None:
    # Cada linea del reporte se añade a la lista
    lineas_reporte = []

    # El reporte muestra información basica de la base de datos
    numero_filas = df.shape[0]
    numero_columnas = df.shape[1]

    lineas_reporte.append("Información Dataset:")
    lineas_reporte.append(f"Total de columnas: {numero_columnas}")
    lineas_reporte.append(f"Total de filas   : {numero_filas}")
    lineas_reporte.append("")  # Línea en blanco para separar

    lineas_reporte.append("Valores faltantes por columna")
    # En el reporte se muestra la cantidad de faltantes por cada columna
    for columna in conteo_faltantes:
        # No se debe mostrar la columna "tiene_faltantes"
        if columna == "tiene_faltantes":
            continue

        cantidad = conteo_faltantes[columna]

        if cantidad > 0:
            estado_faltantes = f"{cantidad} faltante(s)"
        else:
            estado_faltantes = "sin faltantes"

        lineas_reporte.append(f"    {columna}: {estado_faltantes}")

    lineas_reporte.append("")

    # En el reporte se muestra el nombre de estudiantes con datos faltantes
    lineas_reporte.append("Entradas de estudiantes con al menos un valor faltante")
    lineas_reporte.append("")

    columnas_a_revisar = ["nota1", "nota2", "nota3", "asistencia"]

    # Se filtran solo las filas que tienen True en la columna tiene_faltantes
    estudiantes_con_nulos = df.filter(pl.col("tiene_faltantes"))

    # Variable para controlar si el reporte debe mostrar estudiantes o el mensaje
    # de "ninguno"
    encontro_nulos = False

    # Se recorre la tabla filtrada fila por fila convirtiéndolas en diccionarios para
    #  poder añadir al reporte
    for fila in estudiantes_con_nulos.iter_rows(named=True):
        # Si entramos al bucle, significa que al menos existe un estudiante con
        # faltantes
        encontro_nulos = True
        nombre = fila["nombre"]

        # Se revisa cada una de las columnas de notas y asistencia para este estudiante
        for col in columnas_a_revisar:
            # Si el valor en esa columna es None, se añade el detalle al reporte
            if fila[col] is None:
                lineas_reporte.append(f"  - {nombre}: {col}")

    # Si la variable sigue en False es porque no se encontró ningun valor nulo
    if not encontro_nulos:
        lineas_reporte.append("  (Ninguna entrada tiene valores faltantes)")

    # En reporte muestra si existen valores fuera del rango establecido
    lineas_reporte.append("\n Valores fuera de rango")
    lineas_reporte.append("")

    # Si anteriormente se encontró algún dato invalido, se mostrará este mensaje de
    # error
    if datos_invalidos:
        for mensaje_error in datos_invalidos:
            lineas_reporte.append(mensaje_error)
    else:
        lineas_reporte.append("  No se detectaron valores fuera de rango")

    lineas_reporte.append("")

    # Se unen todas las lineas del reporte
    reporte_validacion = "\n".join(lineas_reporte)
    # Se escribe el reporte final en el disco duro
    with open(ruta_salida, mode="w", encoding="utf-8") as archivo_texto:
        archivo_texto.write(reporte_validacion)

    print(f"Reporte de validación guardado en: {ruta_salida}")


# Guarda la base de datos validada en el disco duro
def guardar_csv_validado(df: pl.DataFrame, ruta_salida: str) -> None:
    df.write_csv(ruta_salida)
    print(f"CSV validado guardado en: {ruta_salida}")


# Ejecuta todas las funciones del archivo
def main() -> None:

    # Crea directorio de salida si no existe
    os.makedirs("data/interim", exist_ok=True)

    # Lee la base de datos de entrada
    df = leer_dataset(INPUT_PATH)

    print("Agregando columna de valores faltantes")
    df = agregar_columna_faltantes(df)

    print("Analizando si existen datos faltantes y/o fuera de rango")
    # Ejecuta todas las funciones para detectar valores faltantes
    conteo_faltantes = contar_faltantes_por_columna(df)
    filas_con_faltantes = obtener_filas_con_faltantes(df)
    datos_fuera_rango = detectar_valores_fuera_de_rango(df)

    print("Guardando CSV validado")
    guardar_csv_validado(df, OUTPUT_CSV)

    print("Generando reporte de validación")
    generar_reporte(
        df, conteo_faltantes, filas_con_faltantes, datos_fuera_rango, OUTPUT_REPORTE
    )

    print("validar.py se ejecutó correctamente")


# El codigo se ejecuta solo si es corrido directamente
if __name__ == "__main__":
    main()
