# Cliente Android AVIS

Android se empaquetará desde `clients/web` con Capacitor. Esta carpeta contiene decisiones y configuración nativa futura; todavía no es un proyecto APK compilable.

Requisitos para el siguiente hito:
- Capacitor CLI y plataforma Android.
- SQLite nativo para metadatos; archivos en sandbox privado.
- Cámara/selector nativos.
- Sin servidor remoto ni URL remota requerida para iniciar.
- Pruebas en modo avión y después de reiniciar el dispositivo.

No usar IndexedDB como única persistencia para expedientes e imágenes en Android: la documentación de Capacitor advierte que el almacenamiento web puede ser desalojado; SQLite es más adecuado para datos voluminosos y consultas.
