# Protocolo metodológico y diccionario de datos — Estudio AVIS-100

## 1. Título de trabajo
Distribución espacial de puntos anatómicos y variabilidad de mediciones en análisis cefalométricos y panorámicos realizados mediante AVIS.

## 2. Diseño
Estudio observacional, descriptivo y transversal, con 100 radiografías: 50 laterales de cráneo para análisis cefalométrico y 50 panorámicas para análisis de Levandoski. Una sola evaluadora realizará todos los trazados. Se realizará una colocación final por caso. No habrá repetición de casos ni segundo evaluador.

La población es mixta en edad y etapa dentaria. La edad se registrará en años y meses adicionales; la etapa dentaria se registrará como temporal, mixta temprana, mixta tardía, permanente o no registrada. Sexo y equipo/centro de adquisición se registrarán solo si están disponibles. No se recogerán nombres, números de expediente, CURP, fecha completa de nacimiento ni identificadores directos.

## 3. Muestra y codificación
- CEF-001 a CEF-050: radiografías laterales de cráneo.
- PAN-001 a PAN-050: radiografías panorámicas con análisis de Levandoski.
- Cada código será único y no se reutilizará.
- La inclusión de cada imagen se decidirá antes de colocar los puntos.
- Se registrará si una imagen presenta limitaciones técnicas o puntos anatómicos no identificables.

## 4. Procedimiento
1. Desidentificar las imágenes antes de cargarlas en AVIS.
2. Asignar el código consecutivo del estudio.
3. Registrar edad, etapa dentaria y metadatos disponibles.
4. Cargar la imagen original y conservar sus dimensiones.
5. Colocar los puntos anatómicos una sola vez. Se permite revisar y corregir durante la sesión de trazado, antes de finalizar el caso.
6. Al finalizar, AVIS bloquea la edición de puntos en esa sesión y registra localmente el código para evitar reutilizarlo.
7. Exportar inmediatamente JSON, CSV, trazado PNG e imagen original PNG.
8. Registrar cualquier incidencia en la bitácora externa del estudio.

La restricción de un único trazado final es una regla de protocolo. El registro local de códigos duplicados es una ayuda operativa y no sustituye el control maestro de la base de datos del estudio.

## 5. Variables y estructura de exportación

### Variables comunes
- study: identificador AVIS-100.
- case.caseId: código anónimo CEF-### o PAN-###.
- case.ageYears y case.ageMonths: edad al momento de la radiografía, sin fecha de nacimiento.
- case.sex: sexo registrado, si está disponible.
- case.dentition: etapa dentaria.
- case.imageDevice: equipo o centro, opcional y sin identificadores personales.
- image.width y image.height: dimensiones de la imagen original.
- landmarks / points: código anatómico, etiqueta y coordenadas X/Y en píxeles de la imagen original.
- measurements: valores calculados y unidades.
- placementProtocol: una colocación final por caso y una evaluadora.
- createdAt: fecha/hora de exportación.

### Cefalometría
El JSON conserva los puntos manuales, los puntos derivados, las mediciones existentes, las unidades y la calibración cuando exista. Las mediciones lineales se distinguen de las angulares; las lineales no calibradas no deben interpretarse como milímetros.

### Panorámica — Levandoski
El JSON conserva los 22 puntos anatómicos, coordenadas originales, ocho pares de mediciones bilaterales, diferencias porcentuales, lado de mayor dimensión y resúmenes vertical/horizontal. Las distancias en píxeles son relativas a la misma imagen y no equivalen a distancias anatómicas reales.

### Archivos por caso
- `<ID>_datos.json`: registro estructurado completo.
- `<ID>_datos.csv`: puntos y mediciones en formato tabular.
- `<ID>_trazado.png`: imagen con puntos y segmentos.
- `<ID>_original.png`: imagen cargada sin trazos.

Los archivos se descargan individualmente. El usuario debe reunirlos en una carpeta por código de caso y conservar una copia de respaldo cifrada y con acceso restringido.

## 6. Plan de análisis
Analizar cefalometrías y panorámicas por separado. No combinar coordenadas de modalidades distintas.

Para cada punto: media, desviación estándar, mediana, rango intercuartílico, mínimo y máximo de X/Y. Para resumir la distribución espacial, reportar coordenadas absolutas y normalizadas por ancho/alto de imagen; no comparar coordenadas absolutas entre imágenes sin una estrategia de registro/alineación previamente especificada y validada.

Para Levandoski: describir por cada par las distancias en píxeles derecha/izquierda, diferencia porcentual, lado mayor y datos faltantes. Estratificar descriptivamente por edad y etapa dentaria cuando el tamaño de cada estrato lo permita. Informar el número de observaciones disponibles por variable.

Para cefalometría: resumir cada medición con media, desviación estándar, mediana, rango intercuartílico y valores mínimo/máximo; estratificar por edad y etapa dentaria cuando sea pertinente. No asumir que referencias cefalométricas de una población son normas válidas para todos los subgrupos de la muestra.

## 7. Alcance y limitaciones
Con una sola colocación por caso y una evaluadora no es posible estimar reproducibilidad intraobservador ni interobservador. La dispersión entre imágenes mezcla diferencias anatómicas reales, variación de adquisición, magnificación, distorsión, superposición y decisiones de identificación. Por tanto, se reportará como variabilidad observada, no como error de medición ni exactitud validada de AVIS.

La panorámica es una proyección bidimensional con magnificación y distorsión diferencial; las comparaciones en píxeles no se interpretarán como longitudes anatómicas reales ni como umbrales diagnósticos. El criterio operativo de compensación de 1% mostrado por la interfaz de Levandoski no es un umbral clínico validado.

## 8. Control de calidad y ética
Antes de iniciar los 100 casos, realizar una prueba técnica con imágenes de ensayo que no formen parte de la muestra definitiva. Verificar que JSON/CSV/PNG se descarguen, que las coordenadas correspondan a la imagen original y que los datos se puedan reconstruir.

Confirmar autorización institucional, consentimiento o dispensa aplicable y aprobación ética cuando corresponda. Mantener la tabla de correspondencia entre códigos e identidad del paciente separada del conjunto analítico y bajo custodia autorizada. No cargar imágenes identificables en AVIS ni incluir datos personales en los archivos exportados.

## 9. Estado de implementación
La rama de trabajo incorpora metadatos de investigación, bloqueo tras finalización, control local de códigos usados y exportación individual JSON/CSV/PNG para cefalometría y Levandoski. El registro local no es una base de datos central ni garantiza por sí solo que no se repita un paciente en otro dispositivo o navegador. La compilación y las pruebas de aceptación deben confirmarse en el deployment de vista previa antes de usarlo para la muestra definitiva.
