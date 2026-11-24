# Auditoría inicial del núcleo de AVIS

Fecha: 2026-11-24  
Rama auditada: `feature/avis-multiplatform-local`

## Objetivo y límites

Esta auditoría identifica qué lógica puede convertirse en núcleo reutilizable para Windows, web y Android. No modifica fórmulas clínicas, tablas de referencia ni resultados existentes. Los cálculos deben conservar su comportamiento hasta que exista una validación clínica y una batería de equivalencia.

## Inventario observado

| Área | Código actual | Estado para reutilización |
|---|---|---|
| Edad cronológica y referencias CS1–CS6 | `app/age_calculation.py` | Funciones Python independientes de Qt; candidata a extracción directa |
| Geometría y Steiner | `app/cephalometry.py` | Funciones de geometría y cálculo independientes de Qt; candidata a núcleo compartido |
| Nolla | `app/nolla.py` | Tabla, suma e interpolación independientes de Qt; revisar procedencia/versión de la tabla antes de uso clínico |
| Moyers 75 % | `app/moyers.py` | Funciones puras presentes, pero el mismo archivo importa PySide6; separar módulo de cálculo de la interfaz |
| Índice de Little | `app/little.py` | `little_measurements` es cálculo puro, pero vive junto a widgets Qt |
| Levandoski | `app/levandoski.py` | Interfaz y cálculo están mezclados; requiere identificar y extraer funciones sin alterar convenciones |
| Análisis fotográfico | `app/photo_analysis.py` | Configuración, geometría y presentación están mezcladas; requiere extracción por fórmula y pruebas |
| Panorámica | `app/panoramic_form.py` | Archivo de formulario extenso; separar lógica de presentación después de inventariar fórmulas |
| Persistencia | `app/database.py`, `app/storage.py` | Actualmente orientada al escritorio/SQLite; web y Android requieren adaptadores locales propios |
| Informes | `app/export_report.py`, `app/reports.py` | ReportLab está ligado a Python; definir un contrato de informe independiente de la plataforma |

## Hallazgos que condicionan la migración

1. No existe todavía un único núcleo Python independiente de la interfaz. Algunos cálculos son puros, pero están en módulos que importan PySide6.
2. El cliente web React/TypeScript y una app Android con Capacitor no pueden ejecutar automáticamente esos módulos Python. Antes de afirmar equivalencia multiplataforma hay que elegir entre un runtime Python compatible (por ejemplo, Pyodide en web, con sus límites) o una implementación TypeScript con pruebas de paridad.
3. El cálculo de Little devuelve píxeles relativos y advierte que no equivale a milímetros sin calibración 1:1. Esa unidad y advertencia deben conservarse.
4. Moyers ya define interpolación y discrepancia como funciones separadas, pero su módulo importa Qt. Es un candidato claro para separar en una siguiente modificación controlada.
5. Nolla documenta que su tabla procede de material aportado por la propietaria del proyecto. La tabla no debe sustituirse ni presentarse como validación universal.
6. El propio código de fotografía contiene normas y referencias embebidas. No deben corregirse silenciosamente durante la migración: primero se documentan y contrastan con las fuentes clínicas del proyecto.
7. El README/arquitectura actual indica almacenamiento local sin cifrado de aplicación ni autenticación. No usar datos identificables reales hasta implementar y revisar medidas de protección adecuadas.

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
