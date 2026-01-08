' ========================================================================
' MACRO VBA - Actualización Parámetros ARCA desde Excel
' ========================================================================
'
' INSTALACIÓN:
' 1. Abrir Excel
' 2. Alt + F11 (abre editor VBA)
' 3. Insertar > Módulo
' 4. Pegar este código
' 5. Cerrar editor
' 6. Insertar > Formas > Botón
' 7. Asignar macro "ActualizarParametrosARCA"
'
' CONFIGURACIÓN:
' - Ajustar las rutas de Python y del script según tu instalación
' ========================================================================

Sub ActualizarParametrosARCA()
    ' Configuración
    Dim pythonPath As String
    Dim scriptPath As String
    Dim excelPath As String
    Dim year As Integer
    Dim cmd As String
    
    ' === CONFIGURAR ESTAS RUTAS ===
    pythonPath = "C:\Python\python.exe"  ' Ruta al ejecutable de Python
    scriptPath = "C:\Users\franl\Desktop\impuestos\codigo\arca_automation\main.py"  ' Ruta al main.py
    
    ' Obtener ruta del Excel actual
    excelPath = ThisWorkbook.FullName
    
    ' Obtener año desde el nombre del archivo
    ' Asume formato: Cliente_X_2024.xlsx
    Dim fileName As String
    fileName = ThisWorkbook.Name
    
    ' Extraer año del nombre (últimos 4 dígitos antes de .xlsx)
    Dim yearStr As String
    yearStr = Mid(fileName, InStrRev(fileName, "_") + 1, 4)
    
    If IsNumeric(yearStr) Then
        year = CInt(yearStr)
    Else
        MsgBox "No se pudo detectar el año desde el nombre del archivo." & vbCrLf & _
               "Formato esperado: Cliente_X_YYYY.xlsx", vbExclamation, "Error"
        Exit Sub
    End If
    
    ' Confirmar con usuario
    Dim respuesta As VbMsgBoxResult
    respuesta = MsgBox("Se actualizarán los parámetros ARCA para el año " & year & vbCrLf & vbCrLf & _
                       "Archivo: " & ThisWorkbook.Name & vbCrLf & vbCrLf & _
                       "¿Continuar?", vbYesNo + vbQuestion, "Actualizar Parámetros ARCA")
    
    If respuesta = vbNo Then
        Exit Sub
    End If
    
    ' Construir comando
    cmd = """" & pythonPath & """ """ & scriptPath & """ update --year " & year & " --excel """ & excelPath & """"
    
    ' Mostrar mensaje de progreso
    Application.StatusBar = "Actualizando parámetros ARCA..."
    Application.ScreenUpdating = False
    
    ' Ejecutar comando
    Dim shell As Object
    Set shell = CreateObject("WScript.Shell")
    
    Dim exitCode As Long
    exitCode = shell.Run(cmd, 1, True)  ' 1 = ventana visible, True = esperar
    
    Application.ScreenUpdating = True
    Application.StatusBar = False
    
    ' Verificar resultado
    If exitCode = 0 Then
        MsgBox "Parámetros ARCA actualizados correctamente." & vbCrLf & vbCrLf & _
               "Año: " & year, vbInformation, "Actualización Exitosa"
    Else
        MsgBox "Error al actualizar parámetros ARCA." & vbCrLf & vbCrLf & _
               "Código de error: " & exitCode & vbCrLf & vbCrLf & _
               "Revise el log para más detalles.", vbCritical, "Error"
    End If
    
    ' Limpiar
    Set shell = Nothing
End Sub

' ========================================================================
' MACRO ALTERNATIVA - Forzar actualización (ignorar cache)
' ========================================================================

Sub ActualizarParametrosARCA_ForceRefresh()
    ' Similar a ActualizarParametrosARCA pero con --force
    
    Dim pythonPath As String
    Dim scriptPath As String
    Dim excelPath As String
    Dim year As Integer
    Dim cmd As String
    
    pythonPath = "C:\Python\python.exe"
    scriptPath = "C:\Users\franl\Desktop\impuestos\codigo\arca_automation\main.py"
    excelPath = ThisWorkbook.FullName
    
    Dim fileName As String
    fileName = ThisWorkbook.Name
    
    Dim yearStr As String
    yearStr = Mid(fileName, InStrRev(fileName, "_") + 1, 4)
    
    If IsNumeric(yearStr) Then
        year = CInt(yearStr)
    Else
        MsgBox "No se pudo detectar el año.", vbExclamation, "Error"
        Exit Sub
    End If
    
    Dim respuesta As VbMsgBoxResult
    respuesta = MsgBox("⚠️ FORZAR ACTUALIZACIÓN" & vbCrLf & vbCrLf & _
                       "Se ignorará el cache y se regenerarán todos los datos desde ARCA." & vbCrLf & vbCrLf & _
                       "Año: " & year & vbCrLf & vbCrLf & _
                       "¿Continuar?", vbYesNo + vbExclamation, "Force Refresh")
    
    If respuesta = vbNo Then
        Exit Sub
    End If
    
    ' Comando con --force
    cmd = """" & pythonPath & """ """ & scriptPath & """ update --year " & year & " --excel """ & excelPath & """ --force"
    
    Application.StatusBar = "Regenerando parámetros ARCA (force refresh)..."
    Application.ScreenUpdating = False
    
    Dim shell As Object
    Set shell = CreateObject("WScript.Shell")
    
    Dim exitCode As Long
    exitCode = shell.Run(cmd, 1, True)
    
    Application.ScreenUpdating = True
    Application.StatusBar = False
    
    If exitCode = 0 Then
        MsgBox "Parámetros actualizados exitosamente (force refresh).", vbInformation, "Éxito"
    Else
        MsgBox "Error en actualización. Ver log.", vbCritical, "Error"
    End If
    
    Set shell = Nothing
End Sub

' ========================================================================
' HELPER - Validar estructura del Excel
' ========================================================================

Sub ValidarEstructuraExcel()
    Dim pythonPath As String
    Dim scriptPath As String
    Dim excelPath As String
    Dim cmd As String
    
    pythonPath = "C:\Python\python.exe"
    scriptPath = "C:\Users\franl\Desktop\impuestos\codigo\arca_automation\main.py"
    excelPath = ThisWorkbook.FullName
    
    cmd = """" & pythonPath & """ """ & scriptPath & """ validate-excel """ & excelPath & """"
    
    Dim shell As Object
    Set shell = CreateObject("WScript.Shell")
    
    Dim exitCode As Long
    exitCode = shell.Run(cmd, 1, True)
    
    If exitCode = 0 Then
        MsgBox "✓ Estructura del Excel válida", vbInformation, "Validación"
    Else
        MsgBox "❌ Estructura inválida. Ver detalles en ventana.", vbCritical, "Validación"
    End If
    
    Set shell = Nothing
End Sub
