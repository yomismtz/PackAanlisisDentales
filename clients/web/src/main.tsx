import React, { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";
import { buildPhotoReportPdf, loadAvisLogoDataUrl, loadAvisBirdIconDataUrl, loadAvisBirdWatermarkDataUrl, loadYomDentalLogoDataUrl, loadYomDentalWatermarkDataUrl } from "./pdfReport";
import { renderPhotoReportImage } from "./reportImage";
import { AVIS_PALETTES, applyAvisPalette, getAvisPalette } from "./themePalettes";
import { playBirdCall, stopBirdCall } from "./birdAudio";
import Cephalometry from "./Cephalometry";
import Panoramic from "./Panoramic";
import ModelAnalysis from "./ModelAnalysis";
import DentalAge from "./DentalAge";
import {
  calculatePhotoResults,
  PHOTO_CONFIG,
  PHOTO_GUIDES,
  summarizePhotoAnalysis,
  VISUAL_OPTIONS,
  type PhotoMode,
  type Point,
  type PointMap,
} from "./photoAnalysis";

const PHOTO_MODES = Object.keys(PHOTO_CONFIG) as PhotoMode[];

function App() {
  const [screen, setScreen] = useState<"home" | "photo" | "cephalometry" | "panoramic" | "models" | "age">("home");
  const [mode, setMode] = useState<PhotoMode>("facial_frontal");
  const [imageUrl, setImageUrl] = useState("");
  const [fileName, setFileName] = useState("");
  const [imageSize, setImageSize] = useState<{ width: number; height: number } | null>(null);
  const [zoom, setZoom] = useState(0.7);
  const [imageError, setImageError] = useState("");
  const [points, setPoints] = useState<PointMap>({});
  const [selectedPoint, setSelectedPoint] = useState("");
  const [activePoint, setActivePoint] = useState("");
  const [visualValues, setVisualValues] = useState<Record<string, string>>({});
  const [observations, setObservations] = useState("");
  const [conclusion, setConclusion] = useState("");
  const [status, setStatus] = useState("En proceso");
  const [reportFormat, setReportFormat] = useState<"pdf" | "png" | "jpeg">("pdf");
  const [paletteAudioNotice, setPaletteAudioNotice] = useState("");
  const [paletteId, setPaletteId] = useState(() => {
    try {
      return window.localStorage.getItem("avis.palette") ?? "colibri";
    } catch {
      return "colibri";
    }
  });
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imageRef = useRef<HTMLImageElement | null>(null);
  const objectUrlRef = useRef("");

  const config = PHOTO_CONFIG[mode];
  const activePalette = getAvisPalette(paletteId);

  function changePalette(nextId: string) {
    const nextPalette = getAvisPalette(nextId);
    setPaletteId(nextPalette.id);
    setPaletteAudioNotice("");
    void playBirdCall(nextPalette.id).catch(() => {
      setPaletteAudioNotice("No fue posible reproducir el canto. Activa el sonido del dispositivo y vuelve a seleccionar la paleta.");
    });
  }
  const visualFields = VISUAL_OPTIONS[config.formula] ?? {};
  const results = useMemo(() => calculatePhotoResults(mode, points), [mode, points]);
  const automaticConclusions = useMemo(
    () => summarizePhotoAnalysis(mode, points, visualValues),
    [mode, points, visualValues],
  );
  const placedCount = Object.keys(points).length;
  const missingPhotoPoints = config.points.filter((point) => !points[point.code]).map((point) => point.code);
  const pendingVisualFields = Object.keys(visualFields).filter((label) => !visualValues[label] || visualValues[label] === "Sin evaluar");
  const canComplete = missingPhotoPoints.length === 0 && pendingVisualFields.length === 0;

  useEffect(() => {
    applyAvisPalette(activePalette);
    try {
      window.localStorage.setItem("avis.palette", activePalette.id);
    } catch {
      // La selección sigue activa durante esta sesión aunque el navegador bloquee el almacenamiento local.
    }
  }, [activePalette]);

  useEffect(() => {
    return () => {
      if (objectUrlRef.current) URL.revokeObjectURL(objectUrlRef.current);
    };
  }, []);

  useEffect(() => {
    if (status === "Completo" && !canComplete) setStatus("En proceso");
  }, [status, canComplete]);

  useEffect(() => {
    const canvas = canvasRef.current;
    const image = imageRef.current;
    if (!canvas || !image || !imageSize) return;
    canvas.width = imageSize.width;
    canvas.height = imageSize.height;
    const context = canvas.getContext("2d");
    if (!context) return;
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.drawImage(image, 0, 0, imageSize.width, imageSize.height);
    context.lineWidth = Math.max(1, imageSize.width / 1600);
    context.strokeStyle = activePalette.colors.accent;
    context.fillStyle = activePalette.colors.accent;
    context.font = `bold ${Math.max(7, imageSize.width / 180)}px system-ui, sans-serif`;
    context.textBaseline = "middle";

    if (mode === "smile") {
      for (const [a, b] of [["PUP_R", "PUP_L"], ["LC_R", "LC_L"]]) {
        const first = points[a];
        const second = points[b];
        if (first && second) {
          context.beginPath();
          context.moveTo(first.x, first.y);
          context.lineTo(second.x, second.y);
          context.stroke();
        }
      }
    }
    for (const [code, point] of Object.entries(points)) {
      const radius = Math.max(2, imageSize.width / 600);
      context.beginPath();
      context.arc(point.x, point.y, radius, 0, Math.PI * 2);
      context.fillStyle = "#FFFFFF";
      context.fill();
      context.lineWidth = Math.max(1, imageSize.width / 1600);
      context.strokeStyle = activePalette.colors.accent;
      context.stroke();
      context.fillStyle = activePalette.colors.plum;
      context.fillText(code, point.x + radius + 5, point.y - radius - 8);
    }
  }, [imageUrl, imageSize, points, mode, activePalette.id]);

  function clearImage() {
    if (objectUrlRef.current) URL.revokeObjectURL(objectUrlRef.current);
    objectUrlRef.current = "";
    imageRef.current = null;
    setImageUrl("");
    setFileName("");
    setImageSize(null);
    setImageError("");
  }

  function openPhotoAnalysis(nextMode: PhotoMode = "facial_frontal") {
    clearImage();
    setMode(nextMode);
    setPoints({});
    setSelectedPoint("");
    setActivePoint("");
    setVisualValues({});
    setObservations("");
    setConclusion("");
    setStatus("En proceso");
    setZoom(0.7);
    setScreen("photo");
  }

  function changeMode(nextMode: PhotoMode) {
    setMode(nextMode);
    setPoints({});
    setSelectedPoint("");
    setActivePoint("");
    setVisualValues({});
    clearImage();
  }

  function handleImage(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    clearImage();
    if (file.type && !file.type.startsWith("image/")) {
      setImageError("El archivo seleccionado no está identificado como una imagen compatible con el navegador.");
      return;
    }
    const url = URL.createObjectURL(file);
    const image = new Image();
    image.onload = () => {
      imageRef.current = image;
      objectUrlRef.current = url;
      setFileName(file.name);
      setImageSize({ width: image.naturalWidth, height: image.naturalHeight });
      setImageUrl(url);
      setImageError("");
    };
    image.onerror = () => {
      URL.revokeObjectURL(url);
      setImageError("El navegador no pudo abrir esta imagen. Prueba con JPEG, PNG, WebP, BMP o TIFF compatible.");
    };
    image.src = url;
    event.target.value = "";
  }

  function activatePlacement() {
    if (!imageUrl) {
      setImageError("Primero carga la fotografía correspondiente.");
      return;
    }
    if (!selectedPoint) {
      setImageError("Selecciona primero el punto anatómico que vas a colocar.");
      return;
    }
    setImageError("");
    setActivePoint(selectedPoint);
  }

  function placePoint(event: React.MouseEvent<HTMLCanvasElement>) {
    if (!activePoint || !imageSize) return;
    const rectangle = event.currentTarget.getBoundingClientRect();
    const x = ((event.clientX - rectangle.left) / rectangle.width) * imageSize.width;
    const y = ((event.clientY - rectangle.top) / rectangle.height) * imageSize.height;
    if (x < 0 || y < 0 || x > imageSize.width || y > imageSize.height) return;
    const next: Point = { x, y };
    setPoints((previous) => ({ ...previous, [activePoint]: next }));
    setActivePoint("");
    setImageError("");
  }

  function deletePoint() {
    if (!selectedPoint) return;
    setPoints((previous) => {
      const next = { ...previous };
      delete next[selectedPoint];
      return next;
    });
    setActivePoint("");
  }

  function createAnnotatedPhoto() {
    const source = imageRef.current;
    if (!source) throw new Error("Primero carga la fotografía del análisis.");

    const maxDimension = 1800;
    const scale = Math.min(1, maxDimension / source.naturalWidth, maxDimension / source.naturalHeight);
    const width = Math.max(1, Math.round(source.naturalWidth * scale));
    const height = Math.max(1, Math.round(source.naturalHeight * scale));
    const canvas = document.createElement("canvas");
    canvas.width = width;
    canvas.height = height;
    const context = canvas.getContext("2d");
    if (!context) throw new Error("No fue posible preparar la fotografía para el reporte.");

    context.drawImage(source, 0, 0, width, height);

    // En el análisis facial frontal se proyecta una guía horizontal por cada punto colocado.
    if (mode === "facial_frontal") {
      context.save();
      context.strokeStyle = activePalette.colors.plum + "99";
      context.lineWidth = Math.max(1, width / 1400);
      context.setLineDash([Math.max(5, width / 150), Math.max(4, width / 220)]);
      const horizontalPoints = Object.entries(points).sort((a, b) => a[1].y - b[1].y);
      for (const [, point] of horizontalPoints) {
        const y = point.y * scale;
        context.beginPath();
        context.moveTo(0, y);
        context.lineTo(width, y);
        context.stroke();
      }
      context.restore();
    }

    if (mode === "smile") {
      context.save();
      context.strokeStyle = activePalette.colors.accent;
      context.lineWidth = Math.max(1.2, width / 1300);
      for (const [a, b] of [["PUP_R", "PUP_L"], ["LC_R", "LC_L"]]) {
        const first = points[a];
        const second = points[b];
        if (first && second) {
          context.beginPath();
          context.moveTo(first.x * scale, first.y * scale);
          context.lineTo(second.x * scale, second.y * scale);
          context.stroke();
        }
      }
      context.restore();
    }

    const radius = Math.max(3, Math.min(6, width / 450));
    context.font = `bold ${Math.max(14, width / 110)}px system-ui, sans-serif`;
    context.textBaseline = "middle";
    for (const [code, point] of Object.entries(points)) {
      const x = point.x * scale;
      const y = point.y * scale;
      context.beginPath();
      context.arc(x, y, radius, 0, Math.PI * 2);
      context.fillStyle = "#FFFFFF";
      context.fill();
      context.lineWidth = Math.max(1, width / 1600);
      context.strokeStyle = activePalette.colors.accent;
      context.stroke();
      context.fillStyle = activePalette.colors.plum;
      context.fillText(code, x + radius + 5, y - radius - 8);
    }

    return {
      dataUrl: canvas.toDataURL("image/jpeg", 0.92),
      width,
      height,
    };
  }

  async function downloadReport() {
    if (!imageRef.current || !imageSize) {
      setImageError("Carga la fotografía antes de generar el reporte.");
      return;
    }
    try {
      const photo = createAnnotatedPhoto();
      const input = {
        title: config.title,
        mode,
        fileName,
        status,
        photoDataUrl: photo.dataUrl,
        photoWidth: photo.width,
        photoHeight: photo.height,
        horizontalGuides: mode === "facial_frontal",
        points,
        results,
        conclusions: automaticConclusions,
        visualAssessment: visualValues,
        observations,
        professionalConclusion: conclusion,
        generatedAt: new Date(),
        palette: activePalette.colors,
        paletteName: activePalette.name,
        logoDataUrl: await loadAvisLogoDataUrl(),
        clinicLogoDataUrl: await loadYomDentalLogoDataUrl(activePalette.colors, activePalette.clinicLogoImage),
        clinicWatermarkDataUrl: await loadYomDentalWatermarkDataUrl(activePalette.colors, activePalette.clinicLogoImage),
        birdIconDataUrl: await loadAvisBirdIconDataUrl(activePalette.birdImage),
        birdWatermarkDataUrl: await loadAvisBirdWatermarkDataUrl(activePalette.birdImage),
      };

      let blob: Blob;
      let extension: string;
      if (reportFormat === "pdf") {
        const pdfBytes = buildPhotoReportPdf(input);
        const pdfBuffer = pdfBytes.buffer.slice(
          pdfBytes.byteOffset,
          pdfBytes.byteOffset + pdfBytes.byteLength,
        ) as ArrayBuffer;
        blob = new Blob([pdfBuffer], { type: "application/pdf" });
        extension = "pdf";
      } else {
        blob = await renderPhotoReportImage(input, reportFormat);
        extension = reportFormat === "jpeg" ? "jpg" : "png";
      }

      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `AVIS_${mode}_reporte.${extension}`;
      anchor.click();
      window.setTimeout(() => URL.revokeObjectURL(url), 2000);
      setImageError("");
    } catch (error) {
      setImageError(error instanceof Error ? error.message : "No fue posible generar el reporte.");
    }
  }

  function downloadResults() {
    const payload = {
      application: "AVIS · Análisis Odontológico Integral",
      palette: activePalette.name,
      paletteColors: activePalette.colors,
      analysis: mode,
      title: config.title,
      status,
      image: {
        fileName,
        width: imageSize?.width ?? null,
        height: imageSize?.height ?? null,
        note: "El archivo de imagen no se incluye en este JSON.",
      },
      unit: "px_relativos",
      points,
      measurements: results,
      automaticConclusions,
      visualAssessment: visualValues,
      observations,
      professionalConclusion: conclusion,
      generatedAt: new Date().toISOString(),
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `AVIS_${mode}_resultados.json`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  function returnHome() {
    stopBirdCall();
    clearImage();
    setScreen("home");
  }

  return (
    <main className="shell">
      <header className="topbar">
        <button className="brand-button" onClick={returnHome} aria-label="Volver al inicio">
          <img className="brand-mark" src="/avis-icon.svg" alt="" />
          <span className="brand-copy"><strong>AVIS</strong><small>ANÁLISIS ODONTOLÓGICO INTEGRAL</small></span>
        </button>
        <div className="yomdental-mark" role="img" aria-label="YomDental · consultorio de la Dra. Yomira Salgado Martínez" />
        <div className="topbar-actions">
          <label className="palette-control" htmlFor="palette-select">
            <span>PALETA</span>
            <img className="palette-bird-icon" src={activePalette.birdImage} alt={`Ave de la paleta ${activePalette.name}`} />
            <select
              id="palette-select"
              value={paletteId}
              onChange={(event) => changePalette(event.target.value)}
              aria-label="Seleccionar paleta de colores"
            >
              {AVIS_PALETTES.map((palette) => (
                <option key={palette.id} value={palette.id}>{palette.name}</option>
              ))}
            </select>
            <span className="palette-swatches" aria-label="Colores de la paleta activa">
              {activePalette.swatches.map((value, index) => (
                <i key={`${activePalette.id}-${index}`} style={{ backgroundColor: value }} />
              ))}
            </span>
          </label>
          <span className="local"><i /> DATOS LOCALES</span>
        </div>
      </header>
      {paletteAudioNotice && <p className="audio-notice" role="status">{paletteAudioNotice}</p>}

      {screen === "home" ? (
        <>
          <section className="hero">
            <img className="hero-logo" src="/avis-logo.svg" alt="AVIS · Análisis Odontológico Integral" />
            <h1 className="hero-slogan">Observa <span>·</span> Analiza <span>·</span> Integra</h1>
            <p className="hero-description">Herramientas de análisis odontológico en un solo entorno. Los estudios se procesan localmente en este navegador.</p>
          </section>
          <section className="grid">
            <article className="module-card module-card-active">
              <span>02</span><h2>Radiografía lateral</h2>
              <p>Trazado de Steiner, puntos anatómicos, mediciones angulares y calibración para SL y SE.</p>
              <button className="primary" onClick={() => setScreen("cephalometry")}>Abrir análisis lateral</button>
            </article>
            <article className="module-card module-card-active">
              <span>03</span><h2>Análisis fotográfico</h2>
              <p>Nueve modalidades con carga de fotografía, colocación de puntos, mediciones y criterios visuales.</p>
              <button className="primary" onClick={() => openPhotoAnalysis()}>Abrir análisis fotográfico</button>
            </article>
            <article className="module-card">
              <span>04</span><h2>Panorámica</h2>
              <p>Formulario sistemático y trazado de Levandoski. En integración para web.</p>
              <button className="primary" onClick={() => setScreen("panoramic")}>Abrir análisis panorámico</button>
            </article>
            <article className="module-card module-card-active">
              <span>05</span><h2>Modelos dentales</h2>
              <p>Little, Moyers, Tanaka-Johnston, Carey y relaciones intermaxilares. Carga de las 11 vistas y reportes.</p>
              <button className="primary" onClick={() => setScreen("models")}>Abrir análisis de modelos</button>
            </article>
            <article className="module-card module-card-active">
              <span>06</span><h2>Edad dental</h2>
              <p>Registro de maduración dental mediante Nolla y Demirjian.</p>
              <button className="primary" onClick={() => setScreen("age")}>Abrir análisis de edad</button>
            </article>
          </section>
          <footer className="home-footer">Versión web de prueba. Utiliza fotografías ficticias o desidentificadas.</footer>
        </>
      ) : screen === "cephalometry" ? (
        <Cephalometry onBack={returnHome} />
      ) : screen === "panoramic" ? (
        <Panoramic onBack={returnHome} />
      ) : screen === "models" ? (
        <ModelAnalysis onBack={returnHome} paletteId={paletteId} />
      ) : screen === "age" ? (
        <DentalAge onBack={returnHome} />
      ) : (
        <section className="analysis-page">
          <div className="analysis-heading">
            <div>
              <button className="text-button" onClick={returnHome}>← Volver al inicio</button>
              <p className="eyebrow">AVIS · HERRAMIENTA WEB</p>
              <h1>Análisis fotográfico</h1>
              <p>Selecciona el tipo de análisis, carga la fotografía indicada y coloca los puntos anatómicos para obtener las mediciones.</p>
            </div>
            <span className="module-count">9 modalidades disponibles</span>
          </div>

          <div className="mode-row">
            <label htmlFor="mode-select">Tipo de análisis</label>
            <select id="mode-select" value={mode} onChange={(event) => changeMode(event.target.value as PhotoMode)}>
              {PHOTO_MODES.map((key) => <option key={key} value={key}>{PHOTO_CONFIG[key].title}</option>)}
            </select>
          </div>

          <div className="guide"><strong>{config.slot === "extra_frontal" ? "Fotografía frontal en reposo" : config.slot === "extra_profile" ? "Fotografía lateral de perfil" : "Fotografía frontal sonriendo"}</strong><p>{PHOTO_GUIDES[config.slot]}</p></div>

          <div className="workspace">
            <section className="panel photo-panel">
              <div className="panel-heading"><div><h2>Fotografía y puntos</h2><p>Selecciona un punto y después haz clic sobre la imagen.</p></div></div>
              <label className="upload-control">
                <span>＋ Cargar fotografía</span>
                <input type="file" accept="image/*" onChange={handleImage} />
              </label>
              {fileName && imageSize && <div className="file-meta"><strong>{fileName}</strong><span>{imageSize.width} × {imageSize.height} px</span></div>}
              {imageError && <p className="error-text" role="alert">{imageError}</p>}
              {imageUrl && imageSize ? (
                <>
                  <div className="zoom-row"><label htmlFor="zoom">Zoom</label><input id="zoom" type="range" min="0.25" max="2.5" step="0.05" value={zoom} onChange={(event) => setZoom(Number(event.target.value))} /><span>{Math.round(zoom * 100)} %</span><button className="small-button" onClick={() => setZoom(0.7)}>Restablecer</button></div>
                  <div className="image-viewport">
                    <canvas ref={canvasRef} onClick={placePoint} style={{ width: imageSize.width * zoom, height: imageSize.height * zoom, cursor: activePoint ? "crosshair" : "default" }} aria-label="Fotografía para colocación de puntos anatómicos" />
                  </div>
                  {activePoint && <p className="placement-hint">Coloca ahora el punto <strong>{activePoint}</strong> haciendo clic en la fotografía.</p>}
                </>
              ) : (
                <div className="image-empty"><span>▧</span><strong>Fotografía no cargada</strong><p>Selecciona un archivo de imagen compatible con tu navegador. La imagen se procesa localmente y no se guarda en un servidor.</p></div>
              )}

              <div className="point-controls">
                <label htmlFor="point-select">Punto anatómico</label>
                <select id="point-select" value={selectedPoint} onChange={(event) => setSelectedPoint(event.target.value)}>
                  <option value="">Selecciona un punto…</option>
                  {config.points.map((point) => <option key={point.code} value={point.code}>{point.code} · {point.label}</option>)}
                </select>
                <div className="point-actions">
                  <button className="primary" onClick={activatePlacement} disabled={!imageUrl}>Colocar / corregir punto</button>
                  <button className="secondary" onClick={deletePoint} disabled={!selectedPoint || !points[selectedPoint]}>Eliminar punto</button>
                  <span className="point-progress">{placedCount} / {config.points.length} puntos</span>
                </div>
                <div className="point-list">
                  {config.points.map((point) => (
                    <button key={point.code} className={points[point.code] ? "point-chip point-done" : "point-chip"} onClick={() => setSelectedPoint(point.code)} title={point.label}>
                      {points[point.code] ? "✓ " : ""}{point.code}
                    </button>
                  ))}
                </div>
              </div>
            </section>

            <aside className="panel results-panel">
              <div className="panel-heading"><div><h2>Mediciones y resultados</h2><p>Los resultados se actualizan al colocar o corregir puntos.</p></div></div>
              <div className="unit-notice">Las distancias se expresan en píxeles relativos de la fotografía. No equivalen a milímetros y no se aplica calibración física en estos análisis.</div>
              <div className="table-wrap">
                <table>
                  <thead><tr><th>Medición</th><th>Resultado</th><th>Referencia / comparación</th></tr></thead>
                  <tbody>
                    {results.length ? results.map((row, index) => <tr key={index}><td>{row.label}</td><td className="result-value">{row.value}</td><td>{row.reference}</td></tr>) : <tr><td colSpan={3} className="empty-row">Coloca los puntos requeridos para calcular resultados.</td></tr>}
                  </tbody>
                </table>
              </div>

              <section className="automatic-conclusions" aria-live="polite">
                <div className="conclusions-heading">
                  <h3>Conclusiones descriptivas automáticas</h3>
                  <span>Interpretación de la tabla</span>
                </div>
                {automaticConclusions.length ? (
                  <ul>
                    {automaticConclusions.map((item, index) => <li key={index}>{item}</li>)}
                  </ul>
                ) : (
                  <p className="empty-conclusions">Coloca los puntos anatómicos para generar conclusiones a partir de las mediciones.</p>
                )}
                <button
                  className="secondary copy-conclusions"
                  onClick={() => setConclusion((previous) =>
                    [previous.trim(), ...automaticConclusions].filter(Boolean).join("\n")
                  )}
                  disabled={!automaticConclusions.length}
                >
                  Incorporar al registro profesional
                </button>
              </section>

              {Object.keys(visualFields).length > 0 && (
                <div className="visual-box">
                  <h3>Criterios de evaluación visual</h3>
                  <div className="visual-grid">
                    {Object.entries(visualFields).map(([label, options]) => (
                      <label className="visual-field" key={label}><span>{label}</span><select value={visualValues[label] ?? "Sin evaluar"} onChange={(event) => setVisualValues((previous) => ({ ...previous, [label]: event.target.value }))}><option>Sin evaluar</option>{options.map((option) => <option key={option}>{option}</option>)}</select></label>
                    ))}
                  </div>
                </div>
              )}

              <div className="form-field"><label htmlFor="status">Estado</label><select id="status" value={status} onChange={(event) => setStatus(event.target.value)}><option>Pendiente</option><option>En proceso</option><option value="Completo" disabled={!canComplete}>Completo</option></select>{!canComplete && <small className="completion-hint">{missingPhotoPoints.length ? "Faltan puntos: " + missingPhotoPoints.slice(0, 6).join(", ") + (missingPhotoPoints.length > 6 ? "…" : "") : ""}{missingPhotoPoints.length && pendingVisualFields.length ? " · " : ""}{pendingVisualFields.length ? "Criterios sin evaluar: " + pendingVisualFields.slice(0, 4).join(", ") + (pendingVisualFields.length > 4 ? "…" : "") : ""}</small>}</div>
              <div className="form-field"><label htmlFor="observations">Observaciones</label><textarea id="observations" rows={3} value={observations} onChange={(event) => setObservations(event.target.value)} placeholder="Registra observaciones…" /></div>
              <div className="form-field"><label htmlFor="conclusion">Conclusión profesional</label><textarea id="conclusion" rows={3} value={conclusion} onChange={(event) => setConclusion(event.target.value)} placeholder="Integra aquí tu interpretación profesional…" /></div>
              <div className="form-field">
                <label htmlFor="report-format">Formato de descarga del reporte</label>
                <select id="report-format" value={reportFormat} onChange={(event) => setReportFormat(event.target.value as "pdf" | "png" | "jpeg")}>
                  <option value="pdf">PDF · Documento de dos páginas</option>
                  <option value="png">PNG · Imagen larga de alta calidad</option>
                  <option value="jpeg">JPEG · Imagen comprimida</option>
                </select>
              </div>
              <button className="primary download-button" onClick={downloadReport}>Descargar reporte {reportFormat.toUpperCase()}</button>
              <button className="secondary download-button json-download" onClick={downloadResults}>Descargar resultados (JSON)</button>
              <p className="clinical-note">Herramienta de apoyo para medición y registro. No emite diagnóstico autónomo ni sustituye la valoración profesional. El archivo JSON contiene puntos y resultados, no la fotografía.</p>
            </aside>
          </div>
        </section>
      )}
      <footer className="yomdental-footer">
        <strong>YomDental</strong> · Este sistema fue generado por la Dra. Yomira Salgado Martínez
        <span>Cirujano Dentista · Especialidad en Ortodoncia · Maestría en Ciencias Odontológicas · Doctorado en Educación</span>
      </footer>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(<React.StrictMode><App /></React.StrictMode>);
