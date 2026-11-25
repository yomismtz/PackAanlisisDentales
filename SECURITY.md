# Seguridad y datos clínicos

## Controles implementados en esta rama

- Los expedientes permanecen en SQLite local y los archivos se copian al almacenamiento local del dispositivo.
- La base conserva migraciones aditivas con versión de esquema; las migraciones agregan columnas y tablas sin borrar los registros anteriores.
- Los medios nuevos registran SHA-256, tamaño, MIME y dimensiones cuando el formato puede leerse.
- Los análisis nuevos admiten versión de algoritmo e identificador del conjunto de referencias. Los registros heredados se identifican explícitamente como `unversioned`; no se les asigna una versión histórica inventada.
- Las calibraciones pueden persistirse asociadas al expediente y, opcionalmente, a un medio/estudio.
- No hay sincronización ni envío automático de expedientes a un servicio remoto.

## Límites que siguen vigentes

- **No hay cifrado de aplicación** para SQLite ni para los archivos clínicos. SHA-256 sirve para identificar cambios/integridad; no cifra ni protege la confidencialidad.
- **No hay autenticación ni roles propios**, ni bitácora inmutable de acceso/consulta/cambio.
- Los campos de versión de algoritmo y referencias son trazabilidad disponible para nuevos guardados; los módulos todavía deben pasar sus identificadores reales al guardar. Los análisis anteriores permanecen como `unversioned`.
- La protección del directorio depende de los controles del sistema operativo y de la cuenta local.
- No se ha demostrado todavía una restauración cifrada ni una política de retención/eliminación.

## Recomendaciones antes de usar con pacientes reales

1. Utilizar una cuenta de Windows individual y protegida; no compartir la sesión.
2. Mantener activo BitLocker o el cifrado de dispositivo de Windows.
3. Realizar copias de seguridad cifradas en un medio controlado y comprobar que se puedan restaurar.
4. Limitar el acceso a la carpeta de datos local.
5. Evitar incluir datos identificables en capturas de pantalla, issues o repositorios públicos.
6. Revisar y validar cada medición e interpretación con el odontólogo responsable.

## Pendientes para una versión clínica de producción

Cifrado de datos a nivel de aplicación, autenticación y roles, bitácora de auditoría inmutable, gestión de respaldos/restauración, políticas de retención y eliminación, evaluación de amenazas y revisión de cumplimiento normativo aplicable en el lugar de uso.

La aplicación no debe considerarse una solución clínica de producción mientras esos controles y la validación clínica de los algoritmos no estén completos.
