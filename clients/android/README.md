# Cliente Android AVIS

Android se empaquetará desde `clients/web` con Capacitor. Esta carpeta contiene decisiones y configuración nativa futura; todavía no es un proyecto APK compilable.

Requisitos para el siguiente hito:
- Capacitor CLI y plataforma Android.
- SQLite nativo para metadatos; archivos en sandbox privado.
- Cámara/selector nativos.
- Sin servidor remoto ni URL remota requerida para iniciar.
- Pruebas en modo avión y después de reiniciar el dispositivo.

No usar IndexedDB como única persistencia para expedientes e imágenes en Android: la documentación de Capacitor advierte que el almacenamiento web puede ser desalojado; SQLite es más adecuado para datos voluminosos y consultas.


## Identidad y atribución institucional

La interfaz compartida de AVIS debe mostrar de forma persistente el pie de página:

**YomDental · Generado por la Dra. Yomira Salgado Martínez**

Cirujano Dentista · Especialidad en Ortodoncia · Maestría en Ciencias Odontológicas · Doctorado en Educación.

El mismo texto debe incluirse en los informes PDF exportados desde Android, junto con el logotipo AVIS y la marca de agua de la paleta activa. Esta carpeta todavía no contiene un proyecto Android/Capacitor ni permite compilar un APK; la atribución en APK quedará disponible al crear y empaquetar el cliente nativo desde la interfaz web compartida.
