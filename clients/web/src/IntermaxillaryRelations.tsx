import React, { useEffect, useMemo, useRef, useState } from "react";
import { buildPhotoReportPdf, loadAvisLogoDataUrl } from "./pdfReport";
import { getAvisPalette } from "./themePalettes";

type XY = { x: number; y: number };
type Dentition = "permanente" | "mixta" | "temporal";
type ViewKey =
  | "occlusion_frontal" | "occlusion_right" | "occlusion_left"
  | "upper_occlusal" | "upper_frontal" | "upper_right" | "upper_left"
  | "lower_occlusal" | "lower_frontal" | "lower_right" | "lower_left";
type ImageInfo = { url: string; name: string; width: number; height: number };
type ImageMap = Partial<Record<ViewKey, ImageInfo>>;
type PointMap = Partial<Record<ViewKey, Record<string, XY>>>;

const VIEW_GROUPS: Array<{ title: string; items: Array<{ key: ViewKey; label: string }> }> = [
  { title: "Modelos en oclusión", items: [
    { key: "occlusion_frontal", label: "Oclusión · frontal" },
    { key: "occlusion_right", label: "Oclusión · lateral derecha" },
    { key: "occlusion_left", label: "Oclusión · lateral izquierda" },
  ]},
  { title: "Modelo superior individual", items: [
    { key: "upper_occlusal", label: "Superior · oclusal" },
    { key: "upper_frontal", label: "Superior · frontal" },
    { key: "upper_right", label: "Superior · lateral derecha" },
    { key: "upper_left", label: "Superior · lateral izquierda" },
  ]},
  { title: "Modelo inferior individual", items: [
    { key: "lower_occlusal", label: "Inferior · oclusal" },
    { key: "lower_frontal", label: "Inferior · frontal" },
    { key: "lower_right", label: "Inferior · lateral derecha" },
    { key: "lower_left", label: "Inferior · lateral izquierda" },
  ]},
];
const ALL_VIEWS = VIEW_GROUPS.flatMap(group => group.items);
const LABELS: Record<string, string> = {
  molarUpper: "Cúspide mesiovestibular del primer molar superior",
  molarLower: "Surco vestibular del primer molar inferior",
  canineUpper: "Cúspide del canino superior",
  canineLower: "Cúspide del canino inferior",
  terminalUpper: "Punto más distal del segundo molar temporal superior",
  terminalLower: "Punto más distal del segundo molar temporal inferior",
  overjetUpper: "Borde incisal del incisivo central superior",
  overjetLower: "Borde incisal del incisivo central inferior",
  upperIncisal: "Borde incisal del incisivo central superior",
  lowerIncisal: "Borde incisal del incisivo central inferior",
  upperGingival: "Límite gingival del incisivo central superior",
  lowerGingival: "Límite gingival del incisivo central inferior",
};
const anteriorCoordinate = (point: XY, direction: "left" | "right") => direction === "left" ? -point.x : point.x;
function pointOptions(view: ViewKey, dentition: Dentition): Array<[string, string]> {
  if (view === "occlusion_right" || view === "occlusion_left") {
    const result: Array<[string, string]> = dentition === "temporal"
      ? [["terminalUpper", LABELS.terminalUpper], ["terminalLower", LABELS.terminalLower], ["overjetUpper", LABELS.overjetUpper], ["overjetLower", LABELS.overjetLower]]
      : [["molarUpper", LABELS.molarUpper], ["molarLower", LABELS.molarLower], ["canineUpper", LABELS.canineUpper], ["canineLower", LABELS.canineLower], ["overjetUpper", LABELS.overjetUpper], ["overjetLower", LABELS.overjetLower]];
    return result;
  }
  if (view === "occlusion_frontal") return [["upperIncisal", LABELS.upperIncisal], ["lowerIncisal", LABELS.lowerIncisal]];
  if (view === "upper_frontal") return [["upperGingival", LABELS.upperGingival], ["upperIncisal", LABELS.upperIncisal]];
  if (view === "lower_frontal") return [["lowerGingival", LABELS.lowerGingival], ["lowerIncisal", LABELS.lowerIncisal]];
  return [];
}
function classifyAnglePair(upper: XY | undefined, lower: XY | undefined, direction: "left" | "right", tolerance: number): string {
  if (!upper || !lower) return "Pendiente";
  const delta = anteriorCoordinate(upper, direction) - anteriorCoordinate(lower, direction);
  if (Math.abs(delta) <= tolerance) return "Clase I";
  return delta > 0 ? "Clase II" : "Clase III";
}
function terminalPlane(upper: XY | undefined, lower: XY | undefined, direction: "left" | "right", tolerance: number): string {
  if (!upper || !lower) return "Pendiente";
  const delta = anteriorCoordinate(lower, direction) - anteriorCoordinate(upper, direction);
  if (Math.abs(delta) <= tolerance) return "Escalón recto";
  return delta > 0 ? "Escalón mesial" : "Escalón distal";
}
function px(value: number | null): string {
  return value === null || !Number.isFinite(value) ? "Pendiente" : value.toFixed(1) + " px";
}

export default function IntermaxillaryRelations({ onBack, paletteId }: { onBack: () => void; paletteId: string }) {
  const [dentition, setDentition] = useState<Dentition | "">("");
  const [images, setImages] = useState<ImageMap>({});
  const [points, setPoints] = useState<PointMap>({});
  const [activeView, setActiveView] = useState<ViewKey>("occlusion_frontal");
  const [selectedPoint, setSelectedPoint] = useState("upperIncisal");
  const [placing, setPlacing] = useState(false);
  const [error, setError] = useState("");
  const [zoom, setZoom] = useState(1);
  const [tolerance, setTolerance] = useState("0");
  const [anteriorDirection, setAnteriorDirection] = useState<Record<string, "left" | "right">>({
    occlusion_right: "left", occlusion_left: "right",
  });
  const [rightMolarUnavailable, setRightMolarUnavailable] = useState(false);
  const [leftMolarUnavailable, setLeftMolarUnavailable] = useState(false);
  const [rightCanineUnavailable, setRightCanineUnavailable] = useState(false);
  const [leftCanineUnavailable, setLeftCanineUnavailable] = useState(false);
  const [rightTerminalUnavailable, setRightTerminalUnavailable] = useState(false);
  const [leftTerminalUnavailable, setLeftTerminalUnavailable] = useState(false);
  const [rightOpenBite, setRightOpenBite] = useState("No");
  const [leftOpenBite, setLeftOpenBite] = useState("No");
  const [posteriorCrossbite, setPosteriorCrossbite] = useState("No valorable");
  const [anteriorCrossbite, setAnteriorCrossbite] = useState("No valorable");
  const [scissorBite, setScissorBite] = useState("No valorable");
  const [brodieBite, setBrodieBite] = useState("No valorable");
  const [scaleComparable, setScaleComparable] = useState(false);
  const [overbiteMin, setOverbiteMin] = useState("");
  const [overbiteMax, setOverbiteMax] = useState("");
  const [observations, setObservations] = useState("");
  const [conclusion, setConclusion] = useState("");
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const objectUrls = useRef<Set<string>>(new Set());

  const image = images[activeView];
  const options = pointOptions(activeView, dentition || "permanente");
  const currentPoints = points[activeView] || {};
  const uploadedCount = Object.keys(images).length;
  const allImagesLoaded = ALL_VIEWS.every(view => Boolean(images[view.key]));
  const threshold = Math.max(0, Number(tolerance) || 0);

  useEffect(() => () => {
    objectUrls.current.forEach(url => URL.revokeObjectURL(url));
    objectUrls.current.clear();
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !image) return;
    const img = new Image();
    img.onload = () => {
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      const ctx = canvas.getContext("2d");
      if (!ctx) return;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0);
      const selected = points[activeView] || {};
      ctx.font = "bold " + Math.max(13, img.naturalWidth / 90) + "px system-ui";
      ctx.lineWidth = Math.max(2, img.naturalWidth / 1000);
      for (const [code, point] of Object.entries(selected)) {
        ctx.beginPath();
        ctx.arc(point.x, point.y, Math.max(4, img.naturalWidth / 500), 0, Math.PI * 2);
        ctx.fillStyle = "#FFFFFF";
        ctx.fill();
        ctx.strokeStyle = getAvisPalette(paletteId).colors.primary;
        ctx.stroke();
        ctx.fillStyle = getAvisPalette(paletteId).colors.plum;
        ctx.fillText(code, point.x + 7, point.y - 8);
      }
    };
    img.src = image.url;
  }, [image, activeView, points, paletteId]);

  function loadImage(view: ViewKey, event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files && event.target.files[0];
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      setError("El archivo seleccionado no es una imagen.");
      event.target.value = "";
      return;
    }
    const url = URL.createObjectURL(file);
    objectUrls.current.add(url);
    const img = new Image();
    img.onload = () => {
      setImages(previous => {
        const old = previous[view];
        if (old) {
          URL.revokeObjectURL(old.url);
          objectUrls.current.delete(old.url);
        }
        return { ...previous, [view]: { url, name: file.name, width: img.naturalWidth, height: img.naturalHeight } };
      });
      setPoints(previous => ({ ...previous, [view]: {} }));
      setError("");
    };
    img.onerror = () => {
      URL.revokeObjectURL(url);
      objectUrls.current.delete(url);
      setError("No fue posible abrir la imagen seleccionada.");
    };
    img.src = url;
    event.target.value = "";
  }

  function canvasClick(event: React.MouseEvent<HTMLCanvasElement>) {
    if (!image || !placing || !selectedPoint) return;
    const rect = event.currentTarget.getBoundingClientRect();
    const point = {
      x: (event.clientX - rect.left) / rect.width * image.width,
      y: (event.clientY - rect.top) / rect.height * image.height,
    };
    setPoints(previous => ({ ...previous, [activeView]: { ...(previous[activeView] || {}), [selectedPoint]: point } }));
    setPlacing(false);
    setError("");
  }

  function chooseView(next: ViewKey) {
    setActiveView(next);
    const nextOptions = pointOptions(next, dentition || "permanente");
    setSelectedPoint(nextOptions[0] ? nextOptions[0][0] : "");
    setPlacing(false);
  }

  const sides = useMemo(() => {
    const rows = [] as Array<{ side: "Derecha" | "Izquierda"; view: ViewKey; molar: string; canine: string; terminal: string; overjet: number | null }>;
    for (const [side, view, unavailableMolar, unavailableCanine, unavailableTerminal] of [
      ["Derecha", "occlusion_right", rightMolarUnavailable, rightCanineUnavailable, rightTerminalUnavailable],
      ["Izquierda", "occlusion_left", leftMolarUnavailable, leftCanineUnavailable, leftTerminalUnavailable],
    ] as const) {
      const p = points[view] || {};
      const direction = anteriorDirection[view] || (side === "Derecha" ? "left" : "right");
      rows.push({
        side, view,
        molar: unavailableMolar ? "No valorable" : classifyAnglePair(p.molarUpper, p.molarLower, direction, threshold),
        canine: dentition === "temporal" ? "No aplica en dentición temporal" : unavailableCanine ? "No valorable" : classifyAnglePair(p.canineUpper, p.canineLower, direction, threshold),
        terminal: dentition === "temporal" ? unavailableTerminal ? "No valorable" : terminalPlane(p.terminalUpper, p.terminalLower, direction, threshold) : "No aplica",
        overjet: p.overjetUpper && p.overjetLower
          ? anteriorCoordinate(p.overjetUpper, direction) - anteriorCoordinate(p.overjetLower, direction)
          : null,
      });
    }
    return rows;
  }, [points, anteriorDirection, dentition, threshold, rightMolarUnavailable, leftMolarUnavailable, rightCanineUnavailable, leftCanineUnavailable, rightTerminalUnavailable, leftTerminalUnavailable]);

  const vertical = useMemo(() => {
    const upper = points.occlusion_frontal?.upperIncisal;
    const lower = points.occlusion_frontal?.lowerIncisal;
    const upperHeight = points.upper_frontal?.upperGingival && points.upper_frontal?.upperIncisal
      ? Math.abs(points.upper_frontal.upperIncisal.y - points.upper_frontal.upperGingival.y) : null;
    const lowerHeight = points.lower_frontal?.lowerGingival && points.lower_frontal?.lowerIncisal
      ? Math.abs(points.lower_frontal.lowerIncisal.y - points.lower_frontal.lowerGingival.y) : null;
    const overlap = upper && lower ? lower.y - upper.y : null;
    const percentage = overlap !== null && lowerHeight && scaleComparable ? overlap / lowerHeight * 100 : null;
    const min = Number(overbiteMin);
    const max = Number(overbiteMax);
    const interpretation = overlap === null ? "Pendiente"
      : overlap < 0 ? "Separación incisal en esta vista"
      : percentage === null ? "Porcentaje no calculado: escala no homologada"
      : !Number.isFinite(min) || !Number.isFinite(max) || min > max || overbiteMin.trim() === "" || overbiteMax.trim() === "" ? "Rango de referencia no configurado o inválido"
      : percentage >= min && percentage <= max ? "Dentro del rango configurado"
      : percentage < min ? "Cobertura menor al rango configurado" : "Cobertura mayor al rango configurado";
    return { upperHeight, lowerHeight, overlap, percentage, interpretation };
  }, [points, scaleComparable, overbiteMin, overbiteMax]);

  const results = useMemo(() => {
    const rows: Array<{ label: string; value: string; reference: string }> = [];
    for (const side of sides) {
      if (dentition === "temporal") {
        rows.push({ label: "Plano terminal · " + side.side, value: side.terminal, reference: "Relación distal de segundos molares temporales" });
      } else {
        rows.push({ label: "Relación molar · " + side.side, value: side.molar, reference: "Cúspide mesiovestibular superior respecto al surco vestibular inferior" });
        rows.push({ label: "Relación canina · " + side.side, value: side.canine, reference: "Relación sagital de cúspides caninas" });
      }
      rows.push({ label: "Overjet · " + side.side, value: side.overjet === null ? "Pendiente" : px(Math.abs(side.overjet)) + (side.overjet >= 0 ? " · positivo" : " · negativo"), reference: "Diferencia horizontal en la vista lateral; signo según orientación anterior" });
    }
    rows.push({ label: "Altura incisivo central superior", value: px(vertical.upperHeight), reference: "Medición vertical en fotografía superior frontal" });
    rows.push({ label: "Altura incisivo central inferior", value: px(vertical.lowerHeight), reference: "Medición vertical en fotografía inferior frontal" });
    rows.push({ label: "Overbite · solapamiento vertical", value: px(vertical.overlap), reference: "Medición en oclusión frontal; positivo = cobertura" });
    rows.push({ label: "Overbite · porcentaje", value: vertical.percentage === null ? "No calculable" : vertical.percentage.toFixed(1) + " %", reference: "Solo al confirmar escala equivalente entre fotografías" });
    rows.push({ label: "Overbite · interpretación", value: vertical.interpretation, reference: "Rango editable en el formulario; verificar según dentición y referencia" });
    rows.push({ label: "Mordida abierta posterior derecha", value: rightOpenBite, reference: "Registro visual Sí / No / No valorable" });
    rows.push({ label: "Mordida abierta posterior izquierda", value: leftOpenBite, reference: "Registro visual Sí / No / No valorable" });
    rows.push({ label: "Mordida cruzada posterior", value: posteriorCrossbite, reference: "Registro transversal" });
    rows.push({ label: "Mordida cruzada anterior", value: anteriorCrossbite, reference: "Inversión de la relación incisiva; no se denomina Brodie bite" });
    rows.push({ label: "Mordida en tijera", value: scissorBite, reference: "Relación transversal posterior" });
    rows.push({ label: "Brodie bite", value: brodieBite, reference: "Mordida en tijera extensa; confirmar extensión clínica" });
    return rows;
  }, [sides, dentition, vertical, rightOpenBite, leftOpenBite, posteriorCrossbite, anteriorCrossbite, scissorBite, brodieBite]);

  function exportJson() {
    const payload = {
      application: "AVIS · Análisis Odontológico Integral",
      analysis: "Relaciones intermaxilares · Análisis de modelos",
      dentition,
      views: ALL_VIEWS.map(view => ({
        key: view.key, label: view.label,
        image: images[view.key] ? { fileName: images[view.key]!.name, width: images[view.key]!.width, height: images[view.key]!.height } : null,
        points: points[view.key] || {},
      })),
      orientation: anteriorDirection,
      pixelTolerance: threshold,
      measurements: results,
      verticalReference: { lowerPercent: overbiteMin, upperPercent: overbiteMax, comparableImageScaleConfirmed: scaleComparable },
      posteriorOpenBite: { right: rightOpenBite, left: leftOpenBite },
      transverse: { posteriorCrossbite, anteriorCrossbite, scissorBite, brodieBite },
      observations, professionalConclusion: conclusion,
      limitations: "Las distancias se expresan en píxeles. No se convierten a milímetros. Las distancias entre fotografías solo se comparan si se confirma que la escala de captura es equivalente.",
      generatedAt: new Date().toISOString(),
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "AVIS_Relaciones_Intermaxilares.json";
    anchor.click();
    window.setTimeout(() => URL.revokeObjectURL(url), 1500);
  }

  async function exportPdf() {
    const canvas = canvasRef.current;
    if (!canvas || !image || !allImagesLoaded) {
      setError("Carga las once fotografías antes de generar el informe.");
      return;
    }
    try {
      const photo = canvas.toDataURL("image/jpeg", 0.92);
      const imageRows = ALL_VIEWS.map(view => {
        const current = images[view.key]!;
        return { label: "Fotografía · " + view.label, value: current.name, reference: current.width + " × " + current.height + " px" };
      });
      const pdf = buildPhotoReportPdf({
        title: "Relaciones intermaxilares · " + dentition,
        mode: "models-intermaxillary",
        fileName: image.name,
        status: results.every(row => row.value !== "Pendiente") ? "Registrado" : "En proceso",
        photoDataUrl: photo,
        photoWidth: image.width,
        photoHeight: image.height,
        horizontalGuides: false,
        points: currentPoints,
        results: [...results, ...imageRows],
        conclusions: [
          "Análisis organizado en los planos sagital, vertical y transversal.",
          "Dentición seleccionada: " + dentition + ".",
          "Las relaciones molares y caninas se clasifican por la posición relativa de los puntos colocados en cada fotografía lateral.",
          "La clasificación y los hallazgos deben verificarse clínicamente; las imágenes son fotografías de modelos y sus distancias se expresan en píxeles.",
          observations, conclusion,
        ].filter(Boolean),
        visualAssessment: {},
        observations,
        professionalConclusion: conclusion || "Registro de apoyo clínico y docente. Verificar el paralelismo, orientación y escala equivalente de las fotografías antes de interpretar medidas entre vistas.",
        generatedAt: new Date(),
        palette: getAvisPalette(paletteId).colors,
        logoDataUrl: await loadAvisLogoDataUrl(),
        reportLabel: "Relaciones intermaxilares",
      });
      const blob = new Blob([new Uint8Array(pdf).buffer as ArrayBuffer], { type: "application/pdf" });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "AVIS_Relaciones_Intermaxilares.pdf";
      anchor.click();
      window.setTimeout(() => URL.revokeObjectURL(url), 1500);
      setError("");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No fue posible generar el PDF.");
    }
  }

  const hasAnalysis = Boolean(dentition && allImagesLoaded);
  const activeOptions = options.length ? options : [];
  const relationStatus = (value: string) => value === "Pendiente" ? "Pendiente" : value;

  return <section className="analysis-page">
    <div className="analysis-heading">
      <div>
        <button className="text-button" onClick={onBack}>← Volver a métodos de modelos</button>
        <p className="eyebrow">AVIS · MODELOS DENTALES</p>
        <h1>Relaciones intermaxilares</h1>
        <p>Fotografías estandarizadas, registro de puntos y evaluación sagital, vertical y transversal.</p>
      </div>
      <span className="module-count">{uploadedCount}/11 fotografías</span>
    </div>

    {!dentition ? <section className="panel">
      <div className="panel-heading"><div><h2>1. Selección de dentición</h2><p>Elige el tipo de dentición antes de cargar las fotografías.</p></div></div>
      <div className="visual-grid">
        {(["permanente", "mixta", "temporal"] as Dentition[]).map(value =>
          <button key={value} className="secondary" onClick={() => setDentition(value)}>
            <strong>{value === "permanente" ? "Dentición permanente" : value === "mixta" ? "Dentición mixta" : "Dentición temporal"}</strong>
            <span style={{ display: "block", marginTop: 6, fontSize: 11 }}>Seleccionar</span>
          </button>
        )}
      </div>
    </section> : <>
      <div className="mode-row">
        <label htmlFor="dentition-change">Dentición</label>
        <select id="dentition-change" value={dentition} onChange={event => { const next = event.target.value as Dentition; setDentition(next); setPoints({}); setSelectedPoint(pointOptions(activeView, next)[0]?.[0] || ""); }}>
          <option value="permanente">Permanente</option><option value="mixta">Mixta</option><option value="temporal">Temporal</option>
        </select>
        <button className="secondary" onClick={() => { setDentition(""); setImages({}); setPoints({}); }}>Reiniciar selección</button>
      </div>
      <section className="panel">
        <div className="panel-heading"><div><h2>2. Carga de las once fotografías</h2><p>Las once vistas son obligatorias y se reutilizan en los tres planos del análisis.</p></div></div>
        {VIEW_GROUPS.map(group => <div key={group.title} style={{ marginBottom: 18 }}>
          <h3>{group.title}</h3>
          <div className="visual-grid">
            {group.items.map(view => <label className="visual-field" key={view.key}>
              <span>{view.label}</span>
              <input type="file" accept="image/*" onChange={event => loadImage(view.key, event)} />
              <small className="clinical-note">{images[view.key] ? "✓ " + images[view.key]!.name + " · " + images[view.key]!.width + " × " + images[view.key]!.height + " px" : "Fotografía pendiente"}</small>
            </label>)}
          </div>
        </div>)}
        <div className="unit-notice">Unidad de medición: píxeles (px). No hay calibración ni conversión a milímetros. Para comparar porcentajes entre fotografías, confirma que las vistas frontales tengan escala de captura equivalente.</div>
      </section>

      {allImagesLoaded ? <>
        <div className="guide"><strong>3. Registro de puntos</strong><p>Selecciona una fotografía, elige el punto y pulsa sobre la imagen. En las vistas laterales, conserva la orientación de la cara o configura hacia dónde apunta la región anterior.</p></div>
        <div className="workspace">
          <section className="panel photo-panel">
            <div className="panel-heading"><div><h2>Fotografía activa</h2><p>{ALL_VIEWS.find(view => view.key === activeView)?.label}</p></div></div>
            <div className="form-field">
              <label htmlFor="relations-view">Vista para colocar puntos</label>
              <select id="relations-view" value={activeView} onChange={event => chooseView(event.target.value as ViewKey)}>
                {VIEW_GROUPS.map(group => <optgroup key={group.title} label={group.title}>{group.items.map(view => <option key={view.key} value={view.key}>{view.label}</option>)}</optgroup>)}
              </select>
            </div>
            {image && <>
              <div className="file-meta"><strong>{image.name}</strong><span>{image.width} × {image.height} px</span></div>
              <div className="zoom-row"><label>Zoom</label><input type="range" min="0.3" max="2" step="0.05" value={zoom} onChange={event => setZoom(Number(event.target.value))}/><span>{Math.round(zoom * 100)} %</span><button className="small-button" onClick={() => setZoom(1)}>Restablecer</button></div>
              <div className="image-viewport"><canvas ref={canvasRef} onClick={canvasClick} style={{ width: (image.width * zoom) + "px", height: (image.height * zoom) + "px", maxWidth: "none", cursor: placing ? "crosshair" : "default" }} /></div>
            </>}
            {activeOptions.length ? <>
              <div className="point-controls">
                <label htmlFor="relations-point">Punto anatómico</label>
                <select id="relations-point" value={selectedPoint} onChange={event => setSelectedPoint(event.target.value)}>
                  {activeOptions.map(([code, label]) => <option key={code} value={code}>{code} · {label}</option>)}
                </select>
                <div className="point-actions">
                  <button className="primary" disabled={!image} onClick={() => setPlacing(true)}>Colocar / corregir punto</button>
                  <button className="secondary" disabled={!currentPoints[selectedPoint]} onClick={() => setPoints(previous => {
                    const next = { ...(previous[activeView] || {}) };
                    delete next[selectedPoint];
                    return { ...previous, [activeView]: next };
                  })}>Eliminar punto</button>
                  <span className="point-progress">{Object.keys(currentPoints).length}/{activeOptions.length} puntos</span>
                </div>
                <div className="point-list">{activeOptions.map(([code]) =>
                  <button key={code} className={currentPoints[code] ? "point-chip point-done" : "point-chip"} onClick={() => setSelectedPoint(code)}>{currentPoints[code] ? "✓ " : ""}{code}</button>
                )}</div>
              </div>
            </> : <p className="clinical-note">Esta vista se utiliza para la inspección visual transversal y no requiere colocar puntos.</p>}
            {activeView === "occlusion_right" || activeView === "occlusion_left" ? <div className="form-field">
              <label htmlFor="anterior-direction">Orientación anterior de esta fotografía</label>
              <select id="anterior-direction" value={anteriorDirection[activeView] || "left"} onChange={event => setAnteriorDirection(previous => ({ ...previous, [activeView]: event.target.value as "left" | "right" }))}>
                <option value="left">Anterior hacia la izquierda</option><option value="right">Anterior hacia la derecha</option>
              </select>
            </div> : null}
            {error && <p className="error-text" role="alert">{error}</p>}
          </section>

          <aside className="panel results-panel">
            <div className="panel-heading"><div><h2>4. Resultados sagitales</h2><p>Clasificación por lado y medición en píxeles.</p></div></div>
            {dentition === "temporal" ? <>
              <table><thead><tr><th>Lado</th><th>Plano terminal</th><th>Valoración</th></tr></thead><tbody>{sides.map(side => <tr key={side.side}><td>{side.side}</td><td className="result-value">{relationStatus(side.terminal)}</td><td><select value={side.side === "Derecha" ? (rightTerminalUnavailable ? "No valorable" : "Valorar puntos") : (leftTerminalUnavailable ? "No valorable" : "Valorar puntos")} onChange={event => (side.side === "Derecha" ? setRightTerminalUnavailable : setLeftTerminalUnavailable)(event.target.value === "No valorable")}><option>Valorar puntos</option><option>No valorable</option></select></td></tr>)}</tbody></table>
              <p className="clinical-note">En dentición temporal no se calcula relación canina. Marca «No valorable» cuando falte el segundo molar temporal o no pueda identificarse el punto distal.</p>
            </> : <>
              <table><thead><tr><th>Lado</th><th>Clase molar</th><th>Clase canina</th></tr></thead><tbody>{sides.map(side => <tr key={side.side}><td>{side.side}</td><td className="result-value">{relationStatus(side.molar)}</td><td className="result-value">{relationStatus(side.canine)}</td></tr>)}</tbody></table>
              <div className="visual-grid">
                <label className="visual-field"><span>Relación molar derecha</span><select value={rightMolarUnavailable ? "No valorable" : "Valorar puntos"} onChange={event => setRightMolarUnavailable(event.target.value === "No valorable")}><option>Valorar puntos</option><option>No valorable</option></select></label>
                <label className="visual-field"><span>Relación molar izquierda</span><select value={leftMolarUnavailable ? "No valorable" : "Valorar puntos"} onChange={event => setLeftMolarUnavailable(event.target.value === "No valorable")}><option>Valorar puntos</option><option>No valorable</option></select></label>
                <label className="visual-field"><span>Relación canina derecha</span><select value={rightCanineUnavailable ? "No valorable" : "Valorar puntos"} onChange={event => setRightCanineUnavailable(event.target.value === "No valorable")}><option>Valorar puntos</option><option>No valorable</option></select></label>
                <label className="visual-field"><span>Relación canina izquierda</span><select value={leftCanineUnavailable ? "No valorable" : "Valorar puntos"} onChange={event => setLeftCanineUnavailable(event.target.value === "No valorable")}><option>Valorar puntos</option><option>No valorable</option></select></label>
              </div>
            </>}
            <div className="form-field"><label htmlFor="pixel-tolerance">Tolerancia de alineación para Clase I / plano recto (px)</label><input id="pixel-tolerance" type="number" min="0" step="1" value={tolerance} onChange={event => setTolerance(event.target.value)}/><small className="clinical-note">AVIS compara la posición mesiodistal de los dos puntos. La tolerancia es configurable y no representa un umbral clínico validado.</small></div>

            <div className="visual-box">
              <h3>5. Análisis vertical</h3>
              <div className="table-wrap"><table><tbody>
                <tr><td>Altura incisivo central superior</td><td className="result-value">{px(vertical.upperHeight)}</td></tr>
                <tr><td>Altura incisivo central inferior</td><td className="result-value">{px(vertical.lowerHeight)}</td></tr>
                <tr><td>Solapamiento vertical</td><td className="result-value">{px(vertical.overlap)}</td></tr>
                <tr><td>Porcentaje de cobertura</td><td className="result-value">{vertical.percentage === null ? "No calculable" : vertical.percentage.toFixed(1) + " %"}</td></tr>
                <tr><td>Interpretación</td><td className="result-value">{vertical.interpretation}</td></tr>
              </tbody></table></div>
              <label className="visual-field" style={{ marginTop: 10 }}><span>Confirmo escala equivalente de las fotos frontales individuales y en oclusión</span><input type="checkbox" checked={scaleComparable} onChange={event => setScaleComparable(event.target.checked)}/></label>
              <div className="visual-grid">
                <label className="visual-field"><span>Porcentaje mínimo de referencia</span><input type="number" min="0" max="100" value={overbiteMin} onChange={event => setOverbiteMin(event.target.value)}/></label>
                <label className="visual-field"><span>Porcentaje máximo de referencia</span><input type="number" min="0" max="100" value={overbiteMax} onChange={event => setOverbiteMax(event.target.value)}/></label>
              </div>
              <p className="clinical-note">Configura el intervalo de referencia que utilizarás para esta dentición y método. No hay un único intervalo porcentual aplicable a todas las edades. Sin escala equivalente, AVIS no declara el porcentaje como válido.</p>
              <div className="visual-grid">
                <label className="visual-field"><span>Mordida abierta posterior derecha</span><select value={rightOpenBite} onChange={event => setRightOpenBite(event.target.value)}><option>Sí</option><option>No</option></select></label>
                <label className="visual-field"><span>Mordida abierta posterior izquierda</span><select value={leftOpenBite} onChange={event => setLeftOpenBite(event.target.value)}><option>No valorable</option><option>Sí</option><option>No</option></select></label>
              </div>
            </div>

            <div className="visual-box">
              <h3>6. Análisis transversal / horizontal</h3>
              <div className="form-field"><label htmlFor="posterior-crossbite">Mordida cruzada posterior</label><select id="posterior-crossbite" value={posteriorCrossbite} onChange={event => setPosteriorCrossbite(event.target.value)}><option>No valorable</option><option>No presenta</option><option>Derecha</option><option>Izquierda</option><option>Bilateral</option></select></div>
              <div className="form-field"><label htmlFor="anterior-crossbite">Mordida cruzada anterior</label><select id="anterior-crossbite" value={anteriorCrossbite} onChange={event => setAnteriorCrossbite(event.target.value)}><option>No valorable</option><option>Sí</option><option>No</option></select></div>
              <div className="form-field"><label htmlFor="scissor-bite">Mordida en tijera posterior</label><select id="scissor-bite" value={scissorBite} onChange={event => setScissorBite(event.target.value)}><option>No valorable</option><option>No presenta</option><option>Derecha</option><option>Izquierda</option><option>Bilateral</option></select></div>
              <div className="form-field"><label htmlFor="brodie-bite">Brodie bite (mordida en tijera extensa)</label><select id="brodie-bite" value={brodieBite} onChange={event => setBrodieBite(event.target.value)}><option>No valorable</option><option>Sí</option><option>No</option></select></div>
              <p className="clinical-note">La inversión de la relación incisiva se registra como mordida cruzada anterior. Brodie bite describe una relación transversal posterior extrema tipo tijera.</p>
            </div>
            <div className="form-field"><label htmlFor="relations-observations">Observaciones</label><textarea id="relations-observations" rows={3} value={observations} onChange={event => setObservations(event.target.value)}/></div>
            <div className="form-field"><label htmlFor="relations-conclusion">Conclusión profesional / docente</label><textarea id="relations-conclusion" rows={3} value={conclusion} onChange={event => setConclusion(event.target.value)}/></div>
            <button className="primary download-button" onClick={exportPdf} disabled={!hasAnalysis}>Descargar informe PDF</button>
            <button className="secondary download-button" onClick={exportJson} disabled={!hasAnalysis}>Exportar análisis completo (JSON)</button>
            <p className="clinical-note">El PDF incluye la vista seleccionada con los puntos y el cuadro integral de resultados. El JSON incluye puntos y metadatos de las once fotografías.</p>
          </aside>
        </div>
      </> : <div className="unit-notice">Se han cargado {uploadedCount} de 11 fotografías. Completa las once vistas para habilitar el análisis.</div>}
    </>}
  </section>;
}
