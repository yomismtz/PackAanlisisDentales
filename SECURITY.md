# Seguridad y datos clínicos

## Estado de seguridad de la versión inicial

- Los expedientes, la base SQLite y los archivos de imagen se guardan en el perfil local del usuario de Windows.
- Esta versión no implementa cifrado de aplicación ni control de acceso propio. La protección depende de la cuenta y los permisos del equipo.
- No se implementa sincronización ni envío de imágenes a un servicio remoto.
- Las imágenes originales se copian al expediente y las imágenes editadas se guardan como derivados.

## Recomendaciones antes de usar con pacientes reales

1. Utilizar una cuenta de Windows individual y protegida; no compartir la sesión.
2. Mantener activo BitLocker o el cifrado de dispositivo de Windows.
3. Realizar copias de seguridad cifradas en un medio controlado y comprobar que se puedan restaurar.
4. Limitar el acceso a la carpeta de datos local.
5. Evitar incluir datos identificables en capturas de pantalla, issues o repositorios públicos.
6. Revisar y validar cada medición e interpretación con el odontólogo responsable.

## Pendientes para una versión clínica de producción

Cifrado de datos a nivel de aplicación, autenticación y roles, bitácora de auditoría inmutable, gestión de respaldos/restauración, políticas de retención y eliminación, y revisión de cumplimiento normativo aplicable en el lugar de uso.
