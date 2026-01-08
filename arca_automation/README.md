# Sistema de Automatización ARCA

Sistema automatizado para actualización de parámetros impositivos (Ganancias y Bienes Personales) desde fuentes oficiales de ARCA.

---

## 📋 Características

- ✅ **Cache inteligente**: Genera JSONs una vez y los reutiliza (actualizables con `--force`)
- ✅ **Sin hardcodeos**: Toda la configuración centralizada
- ✅ **Logging detallado**: Registra cada paso del proceso
- ✅ **Validación automática**: Verifica completitud y rangos esperados
- ✅ **Integración Excel**: Actualiza directamente hojas de parámetros
- ✅ **Manejo de subperíodos**: Soporta años con múltiples escalas (ej: 2023)
- ✅ **CLI completo**: Comandos para todas las operaciones

---

## 📦 Instalación

```bash
# 1. Clonar/copiar el proyecto
cd /ruta/del/proyecto

# 2. Instalar dependencias
pip install -r requirements.txt
```

### Dependencias necesarias
```txt
requests
beautifulsoup4
pdfplumber
openpyxl
```

---

## 🔧 Configuración

### 1. Configurar path de archivos

Editar `config/settings.py`:

```python
# Directorio donde están los PDFs de ARCA
FILES_DIR = Path(r"C:\Users\franl\Desktop\impuestos\files")
```

### 2. Variables de entorno (opcional)

```bash
# Windows (CMD)
set ARCA_FILES_DIR=C:\ruta\a\archivos\arca
set ARCA_DEBUG=true

# Linux/Mac
export ARCA_FILES_DIR=/ruta/a/archivos/arca
export ARCA_DEBUG=true
```

---

## 🚀 Uso

### Comando 1: Actualizar parámetros de un año

```bash
# Generar parámetros 2024 (usa cache si existe)
python main.py update --year 2024

# Forzar regeneración (ignorar cache)
python main.py update --year 2024 --force

# Actualizar Excel directamente
python main.py update --year 2024 --excel "C:\ruta\al\Excel_Cliente.xlsx"

# Rebuild completo del Excel (borrar todo y reescribir)
python main.py update --year 2024 --excel "archivo.xlsx" --rebuild
```

### Comando 2: Actualizar rango de años

```bash
# Generar cache para 2019-2024
python main.py update-range --from 2019 --to 2024

# Con force refresh
python main.py update-range --from 2019 --to 2024 --force
```

### Comando 3: Información de cache

```bash
python main.py cache-info
```

**Salida:**
```
======================================================================
INFORMACIÓN DE CACHE
======================================================================

Total años en cache: 3
Tamaño total: 0.45 MB

Detalle por año:
----------------------------------------------------------------------

Año 2022:
  Creado: 2024-01-07T14:30:15.123456
  Registros: 42
  Tamaño: 15.23 KB

Año 2023:
  Creado: 2024-01-07T14:32:18.654321
  Registros: 44
  Tamaño: 16.11 KB

Año 2024:
  Creado: 2024-01-07T14:35:42.987654
  Registros: 45
  Tamaño: 16.78 KB
```

### Comando 4: Invalidar cache

```bash
# Eliminar cache de un año específico
python main.py invalidate-cache --year 2024
```

### Comando 5: Validar Excel

```bash
# Verificar que el Excel tenga la estructura correcta
python main.py validate-excel "C:\ruta\al\Excel_Base.xlsx"
```

---

## 📊 Estructura del Excel

El sistema espera una hoja llamada **"Parametros ARCA"** con esta estructura:

| CONCEPTO | IMPUESTO | AÑO | VALOR | DESDE | HASTA | MONTO_FIJO | PORCENTAJE | EXCEDENTE_DESDE | UNIDAD | FUENTE | ORIGEN |
|----------|----------|-----|-------|-------|-------|------------|------------|-----------------|--------|--------|--------|
| BP_MINIMO_NO_IMPONIBLE | BIENES_PERSONALES | 2024 | 292994964.89 | | | | | | ARS | ARCA | HTML_DETERMINATIVA |
| GAN_ESCALA_TRAMO_1 | GANANCIAS | 2024 | | 0 | 1360200 | 0 | 5 | 0 | ARS/% | ARCA | PDF_ART_94 |

### Columnas:

- **CONCEPTO**: Identificador único (ej: `GAN_DED_GANANCIA_NO_IMPONIBLE`)
- **IMPUESTO**: `GANANCIAS` o `BIENES_PERSONALES`
- **AÑO**: Año fiscal
- **VALOR**: Para conceptos simples (deducciones, mínimos, cotizaciones)
- **DESDE/HASTA**: Para escalas y alícuotas (rangos)
- **MONTO_FIJO/PORCENTAJE/EXCEDENTE_DESDE**: Para cálculo de escalas
- **UNIDAD**: `ARS` o `ARS/%`
- **FUENTE**: Siempre `ARCA`
- **ORIGEN**: Identificador de fuente (PDF_ART_30, HTML_ALICUOTAS, etc.)

---

## 📁 Estructura de Archivos

```
arca_automation/
├── config/
│   ├── settings.py         # Configuración centralizada
│   └── constants.py        # URLs, constantes, mapeos
├── core/
│   ├── orchestrator.py     # Orquestador principal
│   ├── cache_manager.py    # Gestión de cache
│   └── year_resolver.py    # (futuro) Resolución de años
├── parsers/
│   ├── base.py             # Parser base abstracto
│   ├── art30_parser.py     # Deducciones (Art. 30)
│   ├── art94_parser.py     # Escalas (Art. 94)
│   ├── bp_parsers.py       # Alícuotas y mínimo BP (HTML)
│   └── monedas_parser.py   # Cotización dólar
├── normalizers/
│   └── arca_normalizer.py  # Normaliza a formato Excel
├── adapters/
│   └── excel_adapter.py    # Actualización de Excel
├── utils/
│   └── logger.py           # Sistema de logging
├── outputs/
│   ├── cache/              # JSONs por año
│   ├── logs/               # Logs de ejecución
│   ├── raw/                # Datos crudos (temporal)
│   └── normalized/         # (opcional) JSONs intermedios
├── main.py                 # Entry point CLI
├── requirements.txt        # Dependencias
└── README.md              # Esta documentación
```

---

## 🔍 Conceptos Generados

### Ganancias

**Deducciones (Art. 30):**
- `GAN_DED_GANANCIA_NO_IMPONIBLE`
- `GAN_DED_CARGAS_FAMILIA_CONYUGE`
- `GAN_DED_CARGAS_FAMILIA_HIJO`
- `GAN_DED_CARGAS_FAMILIA_HIJO_INCAPAZ`
- `GAN_DED_DEDUCCION_ESPECIAL_AP1`
- `GAN_DED_DEDUCCION_ESPECIAL_AP1_NUEVO`
- `GAN_DED_DEDUCCION_ESPECIAL_AP2`

**Escalas (Art. 94):**
- `GAN_ESCALA_TRAMO_1` a `GAN_ESCALA_TRAMO_9`

### Bienes Personales

**Mínimo:**
- `BP_MINIMO_NO_IMPONIBLE`

**Alícuotas:**
- `BP_ALICUOTA_GENERAL_TRAMO_1` a `BP_ALICUOTA_GENERAL_TRAMO_4`
- `BP_ALICUOTA_CUMPLIDORES_TRAMO_1` a `BP_ALICUOTA_CUMPLIDORES_TRAMO_4`

**Cotizaciones:**
- `BP_DOLAR_BILLETE_COMP_31_12`
- `BP_DOLAR_BILLETE_VEND_31_12`
- `BP_DOLAR_DIVISA_COMP_31_12`
- `BP_DOLAR_DIVISA_VEND_31_12`

---

## 🐛 Troubleshooting

### Error: "PDF no encontrado"

**Problema:** El sistema no encuentra los PDFs de ARCA.

**Solución:**
```bash
# 1. Verificar que FILES_DIR esté bien configurado
# 2. Verificar que los PDFs tengan el nombre correcto:
#    - Deducciones-personales-art-30-liquidacion-anual-{año}.pdf
#    - Tabla-art-94-liquidacion-anual-final-{año}.pdf
#    - Valuaciones-{año}-Moneda-Extranjera.pdf
```

### Error: "Hoja 'Parametros ARCA' no encontrada"

**Problema:** El Excel no tiene la estructura esperada.

**Solución:**
```bash
# Validar estructura del Excel
python main.py validate-excel ruta/al/excel.xlsx

# Verificar que:
# 1. Exista una hoja llamada "Parametros ARCA" (exacto)
# 2. Tenga las columnas CONCEPTO, IMPUESTO, AÑO
```

### Warning: "Extracción incompleta"

**Problema:** El parser no pudo extraer todos los datos esperados de un PDF.

**Solución:**
- El sistema usa valores oficiales como fallback (para 2024)
- Si es otro año, revisar manualmente el PDF
- Activar modo DEBUG para ver más detalles

### Activar modo DEBUG

```bash
# Windows
set ARCA_DEBUG=true
python main.py update --year 2024

# Linux/Mac
export ARCA_DEBUG=true
python main.py update --year 2024
```

---

## 📝 Logs

Los logs se guardan en `outputs/logs/` con formato:

```
arca_update_YYYYMMDD_HHMMSS.log
```

**Ejemplo:**
```
2024-01-07 14:30:15 - INFO - Inicializando orquestador para año 2024
2024-01-07 14:30:15 - INFO - ✓ Using cache existente (45 registros)
2024-01-07 14:30:16 - INFO - Actualizando Excel: Cliente_A_2024.xlsx
2024-01-07 14:30:16 - INFO - ✓ Excel actualizado:
2024-01-07 14:30:16 - INFO -    Actualizados: 45
2024-01-07 14:30:16 - INFO -    Insertados: 0
```

---

## 🔐 Cache

El cache se almacena en `outputs/cache/{año}/`:

```
outputs/cache/
  └── 2024/
      ├── parametros_arca_2024.json    # Datos
      └── .metadata.json               # Metadata (fecha, hash, uso)
```

**Política de cache:**
- Cache es "eterno" - se crea una vez y no se actualiza automáticamente
- Para actualizar: usar `--force`
- Cada uso del cache se registra en metadata

---

## 🎯 Próximos pasos (para cuando subas a SharePoint)

1. **Actualizar paths en `config/settings.py`:**
```python
# Cambiar de local a SharePoint
FILES_DIR = Path(r"\\servidor\SharePoint\Impuestos\Files")
CACHE_DIR = Path(r"\\servidor\SharePoint\Impuestos\Cache")
```

2. **Crear macro VBA en Excel:**
```vba
Sub ActualizarParametrosARCA()
    Dim pythonPath As String
    Dim scriptPath As String
    Dim excelPath As String
    Dim year As Integer
    
    pythonPath = "C:\Python\python.exe"
    scriptPath = "\\servidor\arca_automation\main.py"
    excelPath = ThisWorkbook.FullName
    year = Range("A1").Value  ' O donde esté el año
    
    Dim cmd As String
    cmd = pythonPath & " " & scriptPath & " update --year " & year & " --excel """ & excelPath & """"
    
    Shell cmd, vbNormalFocus
End Sub
```

3. **Agregar botón en Excel:**
- Insertar > Formas > Botón
- Asignar macro `ActualizarParametrosARCA`

---

## 📞 Soporte

Para problemas o dudas:
1. Revisar logs en `outputs/logs/`
2. Activar modo DEBUG
3. Validar estructura de Excel con `validate-excel`

---

## ✅ Validación Post-Instalación

```bash
# 1. Verificar instalación
python main.py --help

# 2. Ver cache disponible
python main.py cache-info

# 3. Generar datos de prueba
python main.py update --year 2024

# 4. Validar Excel de prueba
python main.py validate-excel test.xlsx

# 5. Actualizar Excel de prueba
python main.py update --year 2024 --excel test.xlsx
```

Si todos estos comandos funcionan, el sistema está listo para producción.
