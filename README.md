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



## Cefalometría de Steiner simplificada

La radiografía lateral de cráneo abre un trazador interactivo. El estudiante coloca manualmente S, N, A, B, D, Ar, Go, Gn, Me, Pog, Co y los puntos del incisivo superior. El programa dibuja planos, calcula SNA, SNB, ANB, SND, Ar-Go-Me, Go-Gn/SN, AB-Go-Gn e IS-SN, y calcula SL/SE solo cuando existe calibración con una distancia conocida. SL utiliza la proyección perpendicular de Pog sobre SN; SE utiliza la proyección perpendicular del contorno posterior condilar sobre SN. Las coordenadas y la escala se guardan con el análisis.

## Edad dental por Nolla

El módulo permite elegir un cuadrante y registrar los estadios 0–10 de sus siete dientes permanentes, excluyendo terceros molares. Usa la tabla de sumatorias aportada por la propietaria del proyecto, con columnas por sexo y la misma referencia para cuadrantes maxilares y mandibulares. La edad se estima por interpolación entre las dos filas de referencia que contienen la sumatoria; no se extrapola fuera del intervalo de la tabla. La estimación debe interpretarse como apoyo didáctico y validarse por el profesional responsable.

## Maduración vertebral cervical

El módulo CS1–CS6 reutiliza la radiografía lateral de cráneo cargada en el expediente y guía el registro de la morfología de C2–C4, el periodo de maduración, la interpretación y la conducta propuesta. La selección del estadio es manual y debe confirmarse visualmente.

Los campos y referencias numéricas transcritos se basan en el documento de referencia aportado. No se automatizan tablas incompletas, fórmulas no especificadas o criterios que no aparecen en el documento. La ficha panorámica sistemática utiliza un formulario académico seleccionable organizado en 16 fases del protocolo: calidad técnica, orientación, anatomía maxilar y mandibular, anatomía e inventario dentario, soporte óseo, terceros molares, anatomía adyacente, integración, hallazgos radiolúcidos/radiopacos, región periapical, reabsorciones, morfología radicular, periodonto y corticales. El alumno registra principalmente mediante opciones de selección única, multiselección de regiones y dientes FDI, y fichas repetibles para hallazgos múltiples. Los comentarios y la conclusión son campos breves opcionales; las selecciones se conservan en el análisis y se presentan estructuradas en el informe académico PDF. Las fases 17–20 se incorporarán cuando se complete su contenido didáctico. La panorámica no permite confirmar por sí sola todos los hallazgos y el informe requiere revisión docente/profesional.


## Informes académicos

La pestaña «Informes» agrupa cuatro bloques: cefalometría, panorámica, modelos y edad. Solo habilita bloques con al menos un análisis guardado como «Completo»; al generar el PDF incluye únicamente los análisis completos dentro de los bloques seleccionados. El estudiante registra su nombre y el correo del docente. El PDF incorpora datos del expediente, resultados, observaciones, conclusiones guardadas e imágenes disponibles asociadas a cada módulo. Cada versión generada queda registrada localmente con sus apartados seleccionados, los datos de entrega y la ruta del PDF. La generación y apertura del documento funcionan sin conexión; el correo se conserva como destinatario, pero el envío automático y la revisión del docente requieren la futura conexión al servicio en línea.

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
