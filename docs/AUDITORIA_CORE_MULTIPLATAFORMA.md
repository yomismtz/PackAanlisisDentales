# Auditoría inicial del núcleo de AVIS

Fecha: 2026-11-24  
Rama auditada: `feature/avis-multiplatform-local`

## Objetivo y límites

Esta auditoría identifica qué lógica puede convertirse en núcleo reutilizable para Windows, web y Android. No modifica fórmulas clínicas, tablas de referencia ni resultados existentes. Los cálculos deben conservar su comportamiento hasta que exista una validación clínica y una batería de equivalencia.

## Inventario observado

| Área | Código actual | Estado para reutilización |
|---|---|---|
| Edad cronológica y referencias CS1–CS6 | `app/age_calculation.py` | Funciones Python independientes de Qt; candidata a extracción directa |
| Geometría fotográfica | `avis_core/geometry.py` (puente de escritorio: `app/photo_geometry.py`) | **Extraída como primer módulo puro**; conserva las cuatro funciones públicas y sus pruebas de regresión |
| Geometría y Steiner | `app/cephalometry.py` | Funciones de geometría y cálculo independientes de Qt; candidata a siguiente extracción |
| Nolla | `app/nolla.py` | Tabla, suma e interpolación independientes de Qt; revisar procedencia/versión de la tabla antes de uso clínico |
| Moyers 75 % | `app/moyers.py` | Funciones puras presentes, pero el mismo archivo importa PySide6; separar módulo de cálculo de la interfaz |
| Índice de Little | `app/little.py` | `little_measurements` es cálculo puro, pero vive junto a widgets Qt |
| Levandoski | `app/levandoski.py` | Interfaz y cálculo están mezclados; requiere identificar y extraer funciones sin alterar convenciones |
| Análisis fotográfico | `app/photo_analysis.py` | Configuración, geometría y presentación están mezcladas; requiere extracción por fórmula y pruebas |
| Panorámica | `app/panoramic_form.py` | Archivo de formulario extenso; separar lógica de presentación después de inventariar fórmulas |
| Persistencia | `app/database.py`, `app/storage.py` | Actualmente orientada al escritorio/SQLite; web y Android requieren adaptadores locales propios |
| Informes | `app/export_report.py`, `app/reports.py` | ReportLab está ligado a Python; definir un contrato de informe independiente de la plataforma |

## Hallazgos que condicionan la migración

1. Se creó el paquete inicial `avis_core/`. La geometría fotográfica ya vive en `avis_core/geometry.py`; `app/photo_geometry.py` solo reexporta las funciones para no romper la interfaz actual. Esto inicia el núcleo Python para escritorio, pero no constituye todavía un núcleo ejecutable en navegador/Capacitor.
2. El cliente web React/TypeScript y una app Android con Capacitor no pueden ejecutar automáticamente los módulos Python. Para web/Android se debe crear una implementación TypeScript o seleccionar explícitamente un runtime compatible. La ruta elegida debe validarse con vectores de entrada/salida idénticos; no se afirmará paridad hasta que esas pruebas pasen.
3. El cálculo de Little devuelve píxeles relativos y advierte que no equivale a milímetros sin calibración 1:1. Esa unidad y advertencia deben conservarse.
4. Moyers ya define interpolación y discrepancia como funciones separadas, pero su módulo importa Qt. Es un candidato claro para separar en una siguiente modificación controlada.
5. Nolla documenta que su tabla procede de material aportado por la propietaria del proyecto. La tabla no debe sustituirse ni presentarse como validación universal.
6. El propio código de fotografía contiene normas y referencias embebidas. No deben corregirse silenciosamente durante la migración: primero se documentan y contrastan con las fuentes clínicas del proyecto.
7. El README/arquitectura actual indica almacenamiento local sin cifrado de aplicación ni autenticación. No usar datos identificables reales hasta implementar y revisar medidas de protección adecuadas.

## Progreso de la extracción

- `avis_core/geometry.py` contiene inclinación de línea, diferencia angular, proporciones de segmentos y diferencia bilateral.
- `app/photo_geometry.py` mantiene la ruta de importación anterior y delega en el núcleo.
- `tests/test_photo_geometry.py` conserva la regresión existente; `tests/test_core_geometry.py` comprueba el contrato público del nuevo paquete.
- `pyproject.toml` declara ambos paquetes (`app` y `avis_core`) para instalación; CI también se activa ante cambios en `avis_core/**`.
- No se modificaron fórmulas, unidades ni resultados esperados.

## Secuencia técnica recomendada

- Etapa A: mantener el EXE y la rama estable; añadir CI de pruebas para la rama AVIS.
- Etapa B: extraer cálculos puros a módulos sin dependencias de Qt, conservando funciones públicas y resultados; añadir pruebas de regresión.
- Etapa C: crear vectores de prueba neutrales (entradas, salidas, unidades, versión de algoritmo) para validar cualquier puerto TypeScript.
- Etapa D: implementar persistencia local web con IndexedDB y pruebas CRUD; usar datos ficticios.
- Etapa E: empaquetar la misma experiencia web con Capacitor y sustituir/respaldar IndexedDB con SQLite nativo, verificando acceso a archivos e imágenes.
- Etapa F: exportación/importación manual de respaldos cifrados, sin sincronización ni nube.

## Criterio de aceptación

Un cálculo solo se considera migrado cuando:
- su módulo no importa Qt ni componentes de interfaz;
- mantiene casos de prueba de regresión del escritorio;
- tiene casos límite y unidades explícitas;
- la implementación web/Android pasa los mismos vectores de prueba;
- las referencias clínicas y su versión están identificadas.

Esta auditoría es técnica. No constituye validación clínica de los métodos, tablas o normas.
