"""validar.py
Lee data/raw/estudiantes.csv. Produce dos archivos:
• data/interim/validado.csv: el dataset completo con una columna adicional tiene_faltantes
(True/False) que indica si esa fila tiene algún valor nulo. No elimina ninguna fila.
• data/interim/reporte_validacion.txt: un reporte en texto plano que detalla cuántos
valores faltantes hay por columna, qué filas los tienen y cualquier valor fuera del rango
esperado
"""

import polars as pl

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
    #Lee el CSV con los datos de notas y asistencias y lo retorna como DataFrame de polars
    df = pl.read_csv(ruta, null_values=[""])
    return df


def agregar_columna_faltantes(df: pl.DataFrame) -> pl.DataFrame:
    #Agrega la columna tiene_faltantes: se asigna True si la fila tiene algún dato faltante
    columnas_datos: list[str] = ["nota1", "nota2", "nota3", "asistencia"]

    # Para cada columna se verifica si tiene un valor nulo
    tiene_faltantes = pl.lit(False) # Por defecto se asigna False (sin valores nulos)
    for col in columnas_datos:
        #Si al menos una columna tiene datos faltantes, entonces se asigna True
        tiene_faltantes = tiene_faltantes | pl.col(col).is_null()

    df_tiene_faltantes = df.with_columns(tiene_faltantes.alias("tiene_faltantes"))
    return df_tiene_faltantes

#Cuenta cuantos valores nulos hay en cada columna
def contar_faltantes_por_columna(df: pl.DataFrame) -> dict[str, int]:
    conteo: dict[str, int] = {}
    for col in df.columns:
        n_nulos = df[col].null_count()
        conteo[col] = n_nulos
    return conteo

#Retorna una lista solamente con el nombre de los estudiantes que tienen al menos un valor nulo
def obtener_filas_con_faltantes(df: pl.DataFrame) -> list[str]:
    filas_con_nulos = df.filter(pl.col("tiene_faltantes"))
    nombres: list[str] = filas_con_nulos["nombre"].to_list()
    return nombres

#Detecta si hay valores fuera del rango esperado: notas: 1.0 al 7.0 ; asistencia 0 al 100
#Retorna una lista con errores encontrados
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
                #Si la nota no se encuentra dentro de los limites, se genera un mensaje de error.
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
            #Si la asistencia no se encuentra dentro del rango, se genera un mensaje de error
            if valor_asistencia < ASISTENCIA_MIN or valor_asistencia > ASISTENCIA_MAX:
                error_asistencia = (
                    f"  Estudiante '{nombre_alumno}': "
                    f"asistencia = {valor_asistencia} "
                    f"(fuera de [{ASISTENCIA_MIN}, {ASISTENCIA_MAX}])"
                )
                datos_invalidos.append(error_asistencia)

    return datos_invalidos

def generar_reporte(
        df: pl.DataFrame,
        conteo_faltantes: dict[str, int],
        filas_con_faltantes: list[str],
        datos_invalidos: list[str],
        ruta_salida: str,
) -> None:
    """
    Crea un archivo de texto con el resumen de la validación.
    """
    # Usaremos esta lista para ir guardando cada renglón del reporte
    lineas_reporte = []

    # 1. Información básica del archivo
    numero_filas = df.shape[0]
    numero_columnas = df.shape[1]

    lineas_reporte.append("Información Dataset:")
    lineas_reporte.append(f"Total de columnas: {numero_columnas}")
    lineas_reporte.append(f"Total de filas   : {numero_filas}")
    lineas_reporte.append("")  # Línea en blanco para separar

    # 2. Sección de valores faltantes
    lineas_reporte.append("Valores faltantes por columna")

    for columna in conteo_faltantes:
        #No se debe mostrar la columna "tiene_faltantes"
        if columna == "tiene_faltantes":
            continue

        cantidad = conteo_faltantes[columna]

        if cantidad > 0:
            estado_faltantes= f"{cantidad} faltante(s)"
        else:
            estado_faltantes = "sin faltantes"

        lineas_reporte.append(f"    {columna}: {estado_faltantes}")

    lineas_reporte.append("")

    # 3. Sección de nombres con datos nulos
    lineas_reporte.append("Entradas de estudiantes con al menos un valor faltante")
    lineas_reporte.append("")

    if filas_con_faltantes:
        for nombre in filas_con_faltantes:
            lineas_reporte.append(f"  - {nombre}")
    else:
        lineas_reporte.append("  (Ninguna fila tiene valores faltantes)")

    lineas_reporte.append("")

    # 4. Sección de errores de notas o asistencia
    lineas_reporte.append("Valores fuera de rango")
    lineas_reporte.append("")

    if datos_invalidos:
        for mensaje_error in datos_invalidos:
            lineas_reporte.append(mensaje_error)
    else:
        lineas_reporte.append("  No se detectaron valores fuera de rango")

    lineas_reporte.append("")

    # 5. Guarda todo el texto acumulado en el archivo
    # Unimos todas las líneas con un salto de línea
    texto_final = "\n".join(lineas_reporte)

    with open(ruta_salida, mode="w", encoding="utf-8") as archivo_texto:
        archivo_texto.write(texto_final)

    print(f"Reporte de validación guardado en: {ruta_salida}")

def guardar_csv_validado(df: pl.DataFrame, ruta_salida: str) -> None:
    """Guarda el DataFrame validado (con la columna tiene_faltantes) en disco."""
    df.write_csv(ruta_salida)
    print(f"CSV validado guardado en: {ruta_salida}")


def main() -> None:
    """Función principal que ejecuta el flujo completo de validación."""
    import os

    # Crear directorio de salida si no existe
    os.makedirs("data/interim", exist_ok=True)

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
