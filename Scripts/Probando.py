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

        lineas_reporte.append(f"  Columna {columna}: {estado_faltantes}")

    lineas_reporte.append("")

    # 3. Sección de nombres con datos nulos
    lineas_reporte.append("Filas con al menos un valor faltante")
    lineas_reporte.append("")

    if filas_con_faltantes > 0:
        for nombre in filas_con_faltantes:
            lineas_reporte.append(f"  - Estudiante: {nombre}")
    else:
        lineas_reporte.append("  (Ninguna fila tiene valores faltantes)")

    lineas_reporte.append("")

    # 4. Sección de errores de notas o asistencia
    lineas_reporte.append("Valores fuera de rango")
    lineas_reporte.append("")

    if datos_invalidos > 0:
        for mensaje_error in datos_invalidos:
            lineas_reporte.append(mensaje_error)
    else:
        lineas_reporte.append("  (No se detectaron valores fuera de rango)")

    lineas_reporte.append("")

    # 5. Guarda todo el texto acumulado en el archivo
    # Unimos todas las líneas con un salto de línea
    texto_final = "\n".join(lineas_reporte)

    with open(ruta_salida, mode="w", encoding="utf-8") as archivo_texto:
        archivo_texto.write(texto_final)

    print(f"Reporte de validación guardado en: {ruta_salida}")