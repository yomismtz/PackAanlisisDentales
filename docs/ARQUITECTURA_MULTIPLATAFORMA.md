# AVIS — Arquitectura multiplataforma independiente

## Decisión de producto

AVIS tendrá tres distribuciones: web instalable (PWA), escritorio Windows (EXE) y Android (APK). El modelo de datos es **independiente por dispositivo**: no habrá cuentas obligatorias, servidor central, sincronización entre dispositivos ni transferencia automática de expedientes. Cada instalación mantiene sus propios datos y respaldos.

Usuarios objetivo: estudiantes, docentes y profesionales. La aplicación es una herramienta de registro, análisis y apoyo educativo/profesional; no emite diagnósticos autónomos.

## Principios no negociables

1. Paridad funcional: mismos nombres de análisis, fórmulas, unidades, referencias y reglas de validación en las tres plataformas.
2. Datos locales: expedientes, imágenes, análisis y PDF permanecen en el dispositivo o navegador donde se crearon.
3. Sin dependencia de red: después de instalar/cargar la aplicación, las funciones principales operan sin conexión.
4. Portabilidad voluntaria: exportación e importación manual de respaldos cifrados; esto no es sincronización y nunca se ejecuta en segundo plano.
5. Privacidad por diseño: minimizar datos, no enviar telemetría clínica, proteger respaldos y advertir antes de exportar información identificable.
6. Trazabilidad: conservar imagen original, derivadas, fecha, calibración, versión de algoritmo y referencias usadas.

## Arquitectura objetivo

### Núcleo de dominio Python

Conservar y aislar los módulos actuales de cálculo (Steiner, Nolla, Levandoski, Moyers, análisis panorámico, fotográfico y maduración). Mover gradualmente reglas puras a `avis_core/` sin dependencias de interfaz. Añadir contratos de entrada/salida tipados, validación de unidades y pruebas de referencia. No reescribir fórmulas durante la migración de interfaz.

### Windows EXE

Mantener PySide6 como interfaz de escritorio y PyInstaller como empaquetador. Usar almacenamiento en `%LOCALAPPDATA%/AVIS/`, con SQLite y directorio privado de medios. El modo offline es completo. La aplicación no debe requerir navegador ni servicio local.

### Web PWA

Crear cliente React + TypeScript + Vite. PWA con service worker para cachear el shell y recursos estáticos. IndexedDB para expedientes, metadatos y resultados; archivos binarios en Blob/IndexedDB o almacenamiento del navegador. La disponibilidad offline depende de que el usuario haya instalado/abierto la PWA y de las cuotas y políticas del navegador. Incluir exportación/importación local y avisos de espacio/limpieza del navegador. No alojar datos clínicos en servidor.

### Android APK

Empaquetar la misma interfaz web mediante Capacitor. Usar almacenamiento persistente nativo (SQLite para metadatos y archivos en sandbox privado) mediante plugins mantenidos; cámara y selector de archivos nativos. El APK no dependerá de una URL remota para abrir. La exportación/compartición de archivos será explícita y mediada por el usuario.

## Separación de capas

- Dominio: cálculos, referencias, validación, interpretación descriptiva.
- Aplicación: casos de uso (crear expediente, adjuntar estudio, guardar análisis, generar informe).
- Adaptadores de persistencia: SQLite local en Windows/Android; IndexedDB en PWA.
- Presentación: PySide6 en Windows; React en web/Android.
- Exportación: PDF generado localmente; respaldo manual versionado.

## Modelo local de datos

Entidades existentes a conservar: Patient, Media, Analysis, Report. Añadir:
- `schema_version` para migraciones locales.
- `algorithm_version` y `reference_set_id` en cada análisis.
- `original_sha256`, dimensiones, tipo MIME y orientación para medios.
- Registro de calibración con unidad, distancia conocida, escala y estudio asociado.
- Preferencias locales y consentimiento/avisos.
Los identificadores UUID se generan en cada instalación. No se asume que expedientes con el mismo nombre sean la misma persona.

## Respaldo y traslado manual

Formato propuesto `.avisbackup`: ZIP con manifiesto JSON versionado, base SQLite exportada consistentemente, medios y PDF. Cifrado autenticado antes de escribir el archivo (p. ej. AES-256-GCM mediante biblioteca mantenida), derivación de clave con Argon2id y contraseña que el usuario elige. No almacenar la contraseña. Verificar integridad y versión antes de restaurar. La importación nunca sobrescribe silenciosamente: mostrar resumen y pedir confirmación. La restauración crea una copia local independiente.

## Seguridad y límites

- Windows: cifrado de respaldos y considerar cifrado de base/medios en reposo; permisos del perfil de usuario y bloqueo opcional.
- Web: IndexedDB no equivale a cifrado seguro; depender del perfil del navegador y del sistema operativo. No usar almacenamiento compartido ni analytics.
- Android: sandbox de aplicación, bloqueo del dispositivo y cifrado de respaldos; evitar permisos amplios.
- No utilizar datos identificables reales en pruebas automatizadas.
- Antes de uso clínico real: evaluación de privacidad y cumplimiento normativo aplicable, revisión de amenazas, pruebas de recuperación y validación clínica de cada algoritmo.

## Estrategia de migración por etapas

1. **Fundación (rama actual):** documentar arquitectura, contratos de plataforma, configuración de PWA/Capacitor y decisiones de almacenamiento local. No alterar fórmulas clínicas.
2. **Núcleo compartido:** extraer cálculos independientes de Qt y añadir pruebas de equivalencia.
3. **Web PWA:** crear expedientes y adjuntar imágenes en IndexedDB, primero con paridad de expediente y luego análisis.
4. **Android:** compilar el cliente Capacitor con almacenamiento SQLite/archivos nativos y cámara.
5. **Windows:** mantener PySide6 y migrar almacenamiento a un directorio AVIS versionado; conservar compatibilidad con datos existentes.
6. **Calidad:** pruebas de regresión cruzada, restauración de respaldos, modo avión, cierre inesperado, espacio insuficiente y pruebas de usabilidad.

## Criterios de aceptación por plataforma

- **Web:** puede abrirse en modo avión después de instalación/caché inicial; crea expediente, importa foto, guarda análisis y exporta PDF; los datos sobreviven al cierre normal del navegador.
- **Windows:** EXE inicia en equipo limpio, sin Python instalado; opera sin internet; guarda datos después de reiniciar.
- **Android:** APK instala en teléfono/tablet compatible; cámara y selector funcionan; datos sobreviven al cierre y reinicio; opera en modo avión.
- **Todas:** no hay comunicación de expedientes a servidores; fórmulas y resultados coinciden con casos de referencia; el usuario puede crear y restaurar respaldo manual.

## Decisiones explícitas

- No habrá sincronización, login, nube, API de expedientes ni colaboración en tiempo real en esta etapa.
- La PWA y Android comparten interfaz, pero no comparten automáticamente su almacenamiento.
- Los datos creados en EXE, navegador y APK son independientes. Para moverlos, el usuario exporta e importa un respaldo manual.
- La rama de trabajo no sustituye todavía la rama estable ni el EXE ya generado.
