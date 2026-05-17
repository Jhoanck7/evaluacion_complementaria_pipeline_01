import polars as pl


                                  
    
def agregar_promedio(df: pl.DataFrame) -> pl.DataFrame:
    df_con_promedio = df.with_columns(
        ((pl.col("nota1") + pl.col("nota2") + pl.col("nota3")) / 3)
        .roud(2)
        .alias("promedio")
        )
    return df_con_promedio

def agregar_aprobado(df: pl.DataFrame) -> pl.DataFrame:
    df_con_aprobado = df.with_columns(
        (pl.col("promedio") >= 4.0)
        .alias("aprobado")
        )
    return df_con_aprobado
def agregar_categoria(df: pl.DataFrame) -> pl.DataFrame:
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
    return pl.scan_csv

def main() -> None:
    pass

if __name__ == "__main__":
    main()