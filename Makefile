
# ============================================================
# VARIABLES - Completa las rutas que faltan
# ============================================================
PYTHON = python
DATA_DIR = data
RAW_DIR = $(DATA_DIR)/raw
PROCESSED_DIR = $(DATA_DIR)/processed
REPORTS_DIR = reports
SRC_DIR = Scripts

# TODO: define el archivo de datos crudos
DATA_RAW = $(RAW_DIR)/estudiantes.csv

# Archivos de salida de validar.py
VALIDADO        = $(DATA_DIR)/interim/validado.csv
REP_VALIDACION  = $(DATA_DIR)/interim/reporte_validacion.txt

# =============================================================
# Objetivo por defecto
# =============================================================
.PHONY: all
all: $(VALIDADO) $(REP_VALIDACION)

# =============================================================
# Regla para validar.py
# Produce dos archivos: validado.csv y reporte_validacion.txt
# Depende del dato crudo estudiantes.csv
# =============================================================
$(VALIDADO) $(REP_VALIDACION): $(DATA_RAW) $(SRC_DIR)/validar.py
	$(PYTHON) $(SRC_DIR)/validar.py

# =============================================================
# Regla limpiar: elimina los archivos generados
# pero NO toca data/raw/estudiantes.csv
# =============================================================
.PHONY: limpiar
limpiar:
	@if exist "$(VALIDADO)" del /Q "$(VALIDADO)"
	@if exist "$(REP_VALIDACION)" del /Q "$(REP_VALIDACION)"
	@echo Archivos generados eliminados.

# =============================================================
# Regla estado: muestra qué archivos existen y cuáles faltan
# =============================================================
.PHONY: estado
estado:
	@echo === ESTADO DEL PIPELINE ===
	@if exist "$(DATA_RAW)"    (echo [OK]      $(DATA_RAW))    else (echo [FALTA]   $(DATA_RAW))
	@if exist "$(VALIDADO)"       (echo [OK]      $(VALIDADO))       else (echo [FALTA]   $(VALIDADO))
	@if exist "$(REP_VALIDACION)" (echo [OK]      $(REP_VALIDACION)) else (echo [FALTA]   $(REP_VALIDACION))



