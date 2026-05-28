import polars as pl
import os
import datetime

# Rutas
INPUT_TRANSFORMADO_CSV: str = "data/processed/transformado.csv"
INPUT_RESUMEN_TXT: str = "data/processed/resumen.txt"
OUTPUT_REPORTE_MD: str = "reports/reporte_final.md"


# Carga el archivo transformado.csv
def cargar_transformado(ruta: str) -> pl.DataFrame:
    df_transformar = pl.read_csv(ruta)
    return df_transformar


# Carga el archivo resumen.txt
def cargar_resumen(ruta: str) -> str:
    with open(ruta, encoding="utf-8") as archivo:
        resumen = archivo.read()
    # Reemplaza cada salto de línea por dos espacios y un salto de línea
    # De manera de permitir integrar el archivo correctamente al formato markdown del
    # reporte
    return resumen.replace("\n", "  \n")


# Identifica los valores imputados para ser utilizados en la sección de observaciones
# del reporte
def seccion_observaciones_imputados(df: pl.DataFrame) -> str:

    # Se filtra solo las entradas que originalmente contenian un dato faltante
    imputados = df.filter(pl.col("tiene_faltantes"))

    if imputados.is_empty():
        return "No se registraron imputaciones."
    else:
        lineas_seccion_imputados = [
            f"Se realizaron imputaciones en {len(imputados)} registro(s):",
            "",
        ]

    """
     Como los valores nulos de notas y asistencia fueron reemplazados por su mediana y
     media respectivamente,se recalculan estos valores para compararlos con los 
     valores de la columna nota1,nota2,nota3 y asistencia,
     de esta manera se obtiene que valor originalmente era nulo y 
     fue reemplazado posteriormente.
    """

    mediana_n1 = df["nota1"].median()
    mediana_n2 = df["nota2"].median()
    mediana_n3 = df["nota3"].median()
    media_asistencia = round(df["asistencia"].mean())

    # Valores de referencia para saber si una entrada contenia un nulo
    # originalmente o no
    referencias = {
        "nota1": mediana_n1,
        "nota2": mediana_n2,
        "nota3": mediana_n3,
        "asistencia": media_asistencia,
    }

    lineas_seccion_imputados.append("| Estudiante | Campo Imputado | Valor Asignado |")
    lineas_seccion_imputados.append("|---|---|---|")

    # Se verifica columna por columna si el valor coincide con la referencia
    for fila in imputados.iter_rows(named=True):
        nombre = fila["nombre"]
        for col, valor_referencia in referencias.items():
            # Si el valor es igual al valor de referencia,
            # significa que ese campo fue el que se imputó.
            if fila[col] == valor_referencia:
                lineas_seccion_imputados.append(f"| {nombre} | {col} | {fila[col]} |")

    return "\n".join(lineas_seccion_imputados)


# Genera una tabla markdown con las notas, asistencia y resultados de cada estudiante
def resultado_estudiantes(df: pl.DataFrame) -> list[str]:

    lineas_resultados: list[str] = []

    lineas_resultados.append(
        "| Nombre | Nota 1 | Nota 2 | Nota 3 | Asistencia | Promedio | Resultado |"
    )

    lineas_resultados.append("|---|---|---|---|---|---|---|")

    # Cada estudiante representa una fila
    for fila in df.iter_rows(named=True):
        linea = (
            f"| {fila['nombre']} "
            f"| {fila['nota1']} "
            f"| {fila['nota2']} "
            f"| {fila['nota3']} "
            f"| {fila['asistencia']}% "
            f"| {fila['promedio']} "
            f"| {fila['categoria']} |"
        )
        lineas_resultados.append(linea)

    return lineas_resultados


# Construye el reporte
def construir_reporte(df_transformar: pl.DataFrame, resumen: str) -> str:
    # El reporte contiene la fecha en la que fue generado
    fecha = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    # Se obtienen las partes de resultados y observaciones del resumen
    tabla_resultados = "\n".join(resultado_estudiantes(df_transformar))
    seccion_observaciones = seccion_observaciones_imputados(df_transformar)

    # Estructura del reporte
    reporte = [
        "# Reporte Estudiantes",
        f"**Fecha de generación:** {fecha}",
        "\n## Tabla de Resultados por Estudiante",
        tabla_resultados,
        "\n## Resumen Estadístico del Curso\n",
        resumen,
        "\n## Observaciones: Datos Imputados\n",
        seccion_observaciones,
    ]

    return "\n".join(reporte)


# Ejecuta todas las funciones del archivo
def main() -> None:
    print("Iniciando generación de reporte")

    # Crea directorio de salida si no existe
    os.makedirs("reports", exist_ok=True)

    print("Leyendo archivo transformado")
    df_transformado = cargar_transformado(INPUT_TRANSFORMADO_CSV)

    print("Leyendo resumen estadístico")
    resumen = cargar_resumen(INPUT_RESUMEN_TXT)

    print("Generando Reporte Final")
    reporte_final = construir_reporte(df_transformado, resumen)

    # Guarda reporte_final.md en el disco
    with open(OUTPUT_REPORTE_MD, mode="w", encoding="utf-8") as f:
        f.write(reporte_final)

    print(f" Reporte final generado exitosamente en {OUTPUT_REPORTE_MD}")


# El codigo se ejecuta solo si es corrido directamente
if __name__ == "__main__":
    main()
