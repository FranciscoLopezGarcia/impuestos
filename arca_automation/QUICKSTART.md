# 🚀 Guía Rápida de Inicio

## 1. Instalación (5 minutos)

```bash
# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
python main.py --help
```

## 2. Configurar paths (2 minutos)

Editar `config/settings.py` línea 18:

```python
FILES_DIR = Path(r"C:\TU_RUTA\impuestos\files")
```

## 3. Primer uso (1 minuto)

```bash
# Generar cache para 2024
python main.py update --year 2024

# Ver info
python main.py cache-info
```

## 4. Actualizar Excel (30 segundos)

```bash
python main.py update --year 2024 --excel "Cliente_X_2024.xlsx"
```

---

## Archivos que necesitas en FILES_DIR:

```
📁 C:\TU_RUTA\impuestos\files\
  📄 Deducciones-personales-art-30-liquidacion-anual-2024.pdf
  📄 Tabla-art-94-liquidacion-anual-final-2024.pdf
  📄 Valuaciones-2024-Moneda-Extranjera.pdf
```

**Nota:** Las alícuotas BP y mínimo se descargan automáticamente de la web de ARCA (no necesitan PDFs).

---

## Workflow diario:

1. Usuario abre Excel del cliente
2. Click en botón "Actualizar Parámetros ARCA"
3. Sistema:
   - Verifica si hay cache → lo usa
   - Si no hay cache → descarga y parsea desde ARCA
   - Actualiza Excel
4. ✅ Listo para trabajar

---

## Comandos más usados:

```bash
# Cache para todos los años históricos (una sola vez)
python main.py update-range --from 2019 --to 2024

# Actualizar Excel de cliente
python main.py update --year 2024 --excel "Cliente.xlsx"

# Ver qué hay en cache
python main.py cache-info

# Forzar regeneración (si ARCA actualizó algo)
python main.py update --year 2024 --force

# Validar estructura de Excel
python main.py validate-excel "Excel_Base.xlsx"
```

---

## ❓ FAQ

**P: ¿Cada vez que abro Excel descarga de ARCA?**
R: No. Usa cache que se creó una vez. Solo re-descarga con `--force`.

**P: ¿Dónde están los logs?**
R: En `outputs/logs/arca_update_FECHA_HORA.log`

**P: ¿Puedo usar esto sin Excel?**
R: Sí. Solo ejecuta `update --year 2024` y te genera el JSON en `outputs/cache/2024/parametros_arca_2024.json`

**P: ¿Funciona en Linux/Mac?**
R: Sí, pero los Excel estarán en Windows probablemente.

---

## 🆘 Problemas comunes:

### "PDF no encontrado"
→ Verifica que `FILES_DIR` esté bien configurado y que los PDFs tengan los nombres exactos.

### "Hoja 'Parametros ARCA' no encontrada"
→ Tu Excel no tiene la estructura correcta. Ejecuta:
```bash
python main.py validate-excel tu_excel.xlsx
```

### "Extracción incompleta"
→ El PDF de ARCA cambió de formato. El sistema usa valores oficiales como fallback (para 2024).

### VBA no funciona
→ Asegúrate de que las rutas en la macro estén correctas:
- `pythonPath` → donde está python.exe
- `scriptPath` → donde está main.py

---

## ✅ Checklist de producción:

- [ ] Instaladas todas las dependencias (`pip install -r requirements.txt`)
- [ ] Configurado `FILES_DIR` en `config/settings.py`
- [ ] PDFs de ARCA disponibles en `FILES_DIR`
- [ ] Generado cache inicial: `python main.py update-range --from 2019 --to 2024`
- [ ] Probado con Excel de prueba: `python main.py update --year 2024 --excel test.xlsx`
- [ ] Macro VBA instalada en Excel modelo
- [ ] Botón funcionando en Excel
- [ ] Equipo capacitado en uso del botón

---

## 📞 Si algo falla:

1. Activar DEBUG: `set ARCA_DEBUG=true` (Windows)
2. Ver log completo en `outputs/logs/`
3. Copiar error del log y revisar código
4. Si es problema de parseo, revisar heurísticas en parsers
