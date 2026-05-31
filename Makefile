# ==============================================================================
# MAKEFILE - Pipeline Evaluacion complementaria 01
# ==============================================================================

# ==============================================================================
# VARIABLES Y PARÁMETROS CRÍTICOS
# ==============================================================================
PYTHON        = python
DATA_DIR      = data
RAW_DIR       = $(DATA_DIR)/raw
INTERIM_DIR   = $(DATA_DIR)/interim
PROCESSED_DIR = $(DATA_DIR)/processed
REPORTS_DIR   = reports
SRC_DIR       = scripts

# Nodos del Flujo de Datos 
DATA_RAW      = $(RAW_DIR)/estudiantes.csv
DATA_VALIDADO = $(INTERIM_DIR)/validado.csv
REP_VALID     = $(INTERIM_DIR)/reporte_validacion.txt
DATA_IMPUTADO = $(INTERIM_DIR)/imputado.csv
DATA_TRANSF   = $(PROCESSED_DIR)/transformado.csv
DATA_RESUMEN  = $(PROCESSED_DIR)/resumen.txt
REPORTE_FINAL = $(REPORTS_DIR)/reporte_final.md

# ==============================================================================
# OBJETIVO PRINCIPAL
# ==============================================================================
# "make" o "make all" ejecuta primero el control de calidad estricto.
# Si el código no pasa el linter, Make fallará antes de ejecutar el pipeline.
all: lint $(REPORTE_FINAL)
	@echo ""
	@echo "=================================================================="
	@echo "Pipeline completado exitosamente sin errores de calidad."
	@echo "Producto final generado en: $(REPORTE_FINAL)"
	@echo "=================================================================="

# ==============================================================================
# PASOS ENCADENADOS DEL PIPELINE
# ==============================================================================

# Script 1: Validación - Regla Agrupada para múltiples salidas atómicas
$(DATA_VALIDADO) $(REP_VALID) &: $(DATA_RAW) $(SRC_DIR)/validar.py
	@echo "[Etapa 1] Validando consistencia y rangos de datos crudos..."
	$(PYTHON) $(SRC_DIR)/validar.py

# Script 2: Imputación - Reemplazo de nulos empleando Polars
$(DATA_IMPUTADO): $(DATA_VALIDADO) $(SRC_DIR)/imputar.py
	@echo "[Etapa 2] Imputando valores faltantes (Mediana en notas / Media en asistencia)..."
	$(PYTHON) $(SRC_DIR)/imputar.py

# Script 3: Transformation - Ingeniería de atributos con Polars Lazy API
$(DATA_TRANSF): $(DATA_IMPUTADO) $(SRC_DIR)/transformar.py
	@echo "[Etapa 3] Ejecutando ingeniería de atributos (Promedios y Categorías)..."
	$(PYTHON) $(SRC_DIR)/transformar.py

# Script 4: Resumen Estadístico - Extracción de métricas macro agregadas
$(DATA_RESUMEN): $(DATA_TRANSF) $(SRC_DIR)/resumir.py
	@echo "[Etapa 4] Calculando estadísticas globales del curso..."
	$(PYTHON) $(SRC_DIR)/resumir.py

# Script 5: Reporte Consolidado - Dependencia bidireccional estricta
$(REPORTE_FINAL): $(DATA_TRANSF) $(DATA_RESUMEN) $(SRC_DIR)/reporte.py
	@echo "[Etapa 5] Consolidando matriz y resumen estadístico en reporte Markdown..."
	$(PYTHON) $(SRC_DIR)/reporte.py

# ==============================================================================
# REGLAS DE UTILIDAD (Control de Calidad y Entorno)
# ==============================================================================

# Automatiza la verificación de Ruff según las exigencias de la rúbrica (ANN, PEP 8)
lint:
	@echo "Verificando estándares de calidad con Ruff (PEP 8 y Tipado Estático)..."
	ruff check $(SRC_DIR)/
	ruff format --check $(SRC_DIR)/

# Restaura el laboratorio eliminando de forma segura todos los artefactos intermedios
limpiar:
	@echo "Eliminando archivos generados en el pipeline..."
	rm -f $(DATA_VALIDADO) $(REP_VALID) $(DATA_IMPUTADO) $(DATA_TRANSF) $(DATA_RESUMEN) $(REPORTE_FINAL)
	@echo "El entorno científico esta limpio. Puede ejecutar 'make' de nuevo."

# Diagnóstico analítico inmediato del estado de presencia de los archivos del sistema
estado:
	@echo "=================================================================="
	@echo "Estado de los Componentes del Pipeline"
	@echo "=================================================================="
	@echo "[ DATOS CRUDOS ]"
	@if [ -f $(DATA_RAW) ]; then echo "  OK -> $(DATA_RAW)"; else echo "  FALTANTE -> $(DATA_RAW)"; fi
	@echo "[ ETAPA INTERMEDIA ]"
	@if [ -f $(DATA_VALIDADO) ]; then echo "  OK -> $(DATA_VALIDADO)"; else echo "  No generado -> $(DATA_VALIDADO)"; fi
	@if [ -f $(REP_VALID) ]; then echo "  OK -> $(REP_VALID)"; else echo "  No generado -> $(REP_VALID)"; fi
	@if [ -f $(DATA_IMPUTADO) ]; then echo "  OK -> $(DATA_IMPUTADO)"; else echo "  No generado -> $(DATA_IMPUTADO)"; fi
	@echo "[ ETAPA PROCESADA ]"
	@if [ -f $(DATA_TRANSF) ]; then echo "  OK -> $(DATA_TRANSF)"; else echo "  No generado -> $(DATA_TRANSF)"; fi
	@if [ -f $(DATA_RESUMEN) ]; then echo "  OK -> $(DATA_RESUMEN)"; else echo "  No generado -> $(DATA_RESUMEN)"; fi
	@echo "[ ENTREGABLES FINAL ]"
	@if [ -f $(REPORTE_FINAL) ]; then echo "  OK -> $(REPORTE_FINAL)"; else echo "  No generado -> $(REPORTE_FINAL)"; fi
	@echo "=================================================================="

# Declaración obligatoria de objetivos abstractos para evitar colisiones en disco
.PHONY: all lint limpiar estado
