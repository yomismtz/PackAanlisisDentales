# Pack Análisis Dentales

Aplicación de escritorio para Windows, en español, para expediente odontológico, captura de estudios y registro de análisis ortodóncicos.

## Flujo de trabajo
1. Crear un expediente con datos del paciente, o buscar y abrir un registro anterior.
2. Dentro del expediente, subir archivos o capturar imágenes con una cámara conectada.
3. Organizar radiografías, fotografías extraorales e intraorales y vistas de modelos por posición.
4. Abrir los análisis disponibles para el estudio cargado; guardar mediciones, observaciones, estado y conclusión profesional.
5. Exportar un resumen del expediente a PDF.

## Estudios organizados
- Radiografía lateral de cráneo y panorámica.
- Fotografías extraorales frontal en reposo, frontal sonriendo y perfil.
- Fotografías intraorales: lateral derecha, lateral izquierda, frontal en oclusión, oclusal superior, oclusal inferior y vista adicional.
- Modelos superiores e inferiores: laterales, frontal y oclusal.
- Modelos en oclusión: lateral derecha, lateral izquierda y frontal.
- Radiografía carpal opcional.

## Análisis disponibles
Steiner; posición craneofacial y postura cráneo-cervical; maduración vertebral cervical CS1–CS6; revisión sistemática panorámica; Levandoski; edad dental por Nolla; integración de maduración; relaciones intermaxilares; Moyers I (75 %); Nance y Carey; Tanaka-Johnston; Baumé; altura del paladar; análisis facial frontal y de perfil; líneas medias; sonrisa y simetrías horizontales; radiografía carpal.


## Edad dental por Nolla

El módulo permite elegir un cuadrante y registrar los estadios 0–10 de sus siete dientes permanentes, excluyendo terceros molares. Usa la tabla de sumatorias aportada por la propietaria del proyecto, con columnas por sexo y la misma referencia para cuadrantes maxilares y mandibulares. La edad se estima por interpolación entre las dos filas de referencia que contienen la sumatoria; no se extrapola fuera del intervalo de la tabla. La estimación debe interpretarse como apoyo didáctico y validarse por el profesional responsable.

## Maduración vertebral cervical

El módulo CS1–CS6 reutiliza la radiografía lateral de cráneo cargada en el expediente y guía el registro de la morfología de C2–C4, el periodo de maduración, la interpretación y la conducta propuesta. La selección del estadio es manual y debe confirmarse visualmente.

Los campos y referencias numéricas transcritos se basan en el documento de referencia aportado. No se automatizan tablas incompletas, fórmulas no especificadas o criterios que no aparecen en el documento. La ficha panorámica sistemática es editable y queda pendiente de completar con el protocolo clínico definitivo.

## Instalación en Windows
Instala Python 3.11 de 64 bits. En PowerShell, desde la carpeta del proyecto:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup.ps1
.\.venv\Scripts\python.exe run.py
```

Para crear el ejecutable:

```powershell
.\scripts\build.ps1
```

## Datos y seguridad
La base SQLite y los archivos se guardan localmente en `%LOCALAPPDATA%\PackAnalisisDentales`. Cada importación se copia al expediente. Las imágenes editadas se guardan como derivadas y no reemplazan el original. Las versiones anteriores de una vista se conservan.

La corrección de perspectiva endereza la imagen, pero no calibra su escala. Las distancias solo pueden interpretarse en milímetros cuando existe una calibración válida, documentada y asociada al estudio. La eliminación de fondo es una estimación que requiere inspección visual.

## Estado
Base funcional inicial: expedientes locales, catálogo de estudios, captura por cámara, carga de archivos, ajustes de imagen, rectificación de perspectiva, formularios de análisis y exportación de resumen PDF. Se requiere prueba de ejecución y empaquetado en Windows antes de considerar estable esta versión. Los análisis y conclusiones deben ser validados por el profesional responsable.

## Seguridad

La primera versión guarda datos en el perfil local de Windows, pero todavía no cifra a nivel de aplicación la base SQLite ni los archivos clínicos y no incorpora autenticación propia. Consulta [SECURITY.md](SECURITY.md) antes de usarla con información identificable de pacientes. No debe considerarse una solución clínica de producción hasta implementar y validar esos controles.

## Sistema de color

Toda la aplicación utiliza una sola paleta institucional de exactamente ocho colores, centralizada en `app/theme.py`: primario, secundario, acento, fondo, superficie, superficie alternativa, texto y texto secundario. Botones, paneles, formularios, tablas, pestañas y herramientas visuales reutilizan esos ocho valores. No deben añadirse colores hexadecimales aislados en componentes.
