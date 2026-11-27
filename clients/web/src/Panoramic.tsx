import React, { useMemo, useRef, useState } from "react";
import { buildPhotoReportPdf, loadAvisLogoDataUrl, loadAvisBirdIconDataUrl, loadAvisBirdWatermarkDataUrl, loadYomDentalLogoDataUrl, loadYomDentalWatermarkDataUrl } from "./pdfReport";
import { renderPhotoReportImage } from "./reportImage";
import { getAvisPalette } from "./themePalettes";
import Levandoski from "./Levandoski";

type ReviewField = { id: string; title: string; prompt: string; options: string[] };
const REVIEW: ReviewField[] = [
  { id: "quality", title: "1. Calidad técnica", prompt: "Nitidez, contraste, densidad, posicionamiento y cobertura", options: ["Adecuada", "Limitada: movimiento", "Limitada: posicionamiento", "Limitada: exposición / contraste", "Cobertura incompleta", "No valorable"] },
  { id: "orientation", title: "2. Orientación e identificación", prompt: "Orientación, lateralidad y referencias anatómicas", options: ["Adecuada", "Orientación dudosa", "Lateralidad no identificable", "Distorsión / magnificación relevante", "No valorable"] },
  { id: "maxilla", title: "3. Maxilar superior", prompt: "Senos maxilares, cavidad nasal, piso nasal y procesos alveolares", options: ["Sin alteraciones evidentes", "Hallazgo por describir", "Superposición anatómica", "Región no valorable"] },
  { id: "mandible", title: "4. Mandíbula", prompt: "Ramas, cuerpo, ángulos, sínfisis, cóndilos y apófisis coronoides", options: ["Sin alteraciones evidentes", "Hallazgo por describir", "Asimetría aparente", "Región no valorable"] },
  { id: "dentition", title: "5. Inventario dentario", prompt: "Presencia, ausencia, erupción, posición y número dental (FDI)", options: ["Sin hallazgos relevantes", "Ausencia / agenesia por confirmar", "Diente retenido / incluido", "Erupción ectópica", "Alteración de número", "Hallazgo por describir"] },
  { id: "bone", title: "6. Soporte óseo alveolar", prompt: "Altura, patrón trabecular, lámina dura y cresta alveolar", options: ["Sin alteraciones evidentes", "Pérdida ósea horizontal aparente", "Pérdida ósea vertical aparente", "Patrón trabecular alterado", "Hallazgo por describir", "No valorable"] },
  { id: "third_molars", title: "7. Terceros molares", prompt: "Posición, angulación, desarrollo y relación anatómica", options: ["Ausentes", "Erupcionados", "Incluidos / retenidos", "En desarrollo", "Hallazgo por describir", "No valorables"] },
  { id: "adjacent", title: "8. Estructuras anatómicas adyacentes", prompt: "ATM, conducto mandibular, forámenes, canal incisivo y estructuras vecinas", options: ["Sin alteraciones evidentes", "Hallazgo por describir", "Superposición / limitación", "No valorables"] },
  { id: "integration", title: "9. Integración anatómica", prompt: "Continuidad, simetría, relaciones y correlación de estructuras", options: ["Sin discrepancias aparentes", "Asimetría por analizar", "Discontinuidad por confirmar", "Hallazgo por describir", "No concluyente"] },
  { id: "radiolucent", title: "10. Hallazgos radiolúcidos", prompt: "Localización, límites, forma, número y relación con dientes/estructuras", options: ["No identificados", "Un hallazgo", "Múltiples hallazgos", "Requiere estudio complementario", "No valorable"] },
  { id: "radiopaque", title: "11. Hallazgos radiopacos / mixtos", prompt: "Localización, densidad, límites, forma y relación anatómica", options: ["No identificados", "Radiopaco", "Mixto", "Requiere estudio complementario", "No valorable"] },
  { id: "periapical", title: "12. Región periapical", prompt: "Espacio periodontal, lámina dura y cambios periapicales", options: ["Sin alteraciones evidentes", "Ensanchamiento del espacio periodontal", "Alteración periapical por estudiar", "Superposición / no valorable"] },
  { id: "resorption", title: "13. Reabsorciones", prompt: "Reabsorción interna o externa, dientes involucrados y extensión", options: ["No identificadas", "Sospecha de reabsorción externa", "Sospecha de reabsorción interna", "Requiere proyección complementaria", "No valorable"] },
  { id: "roots", title: "14. Morfología radicular", prompt: "Número, longitud, curvatura, dilaceración y desarrollo radicular", options: ["Sin alteraciones evidentes", "Dilaceración / curvatura", "Morfología atípica", "Desarrollo incompleto", "Hallazgo por describir"] },
  { id: "periodontium", title: "15. Periodonto", prompt: "Crestas, espacio periodontal, furcas y soporte periodontal", options: ["Sin alteraciones evidentes", "Hallazgo periodontal por describir", "Pérdida de soporte aparente", "No valorable"] },
  { id: "cortices", title: "16. Corticales y límites óseos", prompt: "Continuidad y contorno de corticales y límites anatómicos", options: ["Continuidad conservada", "Alteración / discontinuidad por estudiar", "Asimetría aparente", "No valorable"] },
];


type AnswerMap = Record<string, string>;

export default function Panoramic({ onBack }: { onBack: () => void }) {
  const [analysisType, setAnalysisType] = useState<"select" | "systematic" | "levandoski">("select");
  const [fileName, setFileName] = useState("");
  const [photoDataUrl, setPhotoDataUrl] = useState("");
  const [imageSize, setImageSize] = useState<{ width: number; height: number } | null>(null);
  const [answers, setAnswers] = useState<AnswerMap>({});
  const [details, setDetails] = useState<AnswerMap>({});
  const [presentTeeth, setPresentTeeth] = useState<string[]>([]);
  const [observations, setObservations] = useState("");
  const [conclusion, setConclusion] = useState("");
  const [status, setStatus] = useState("En proceso");
  const [format, setFormat] = useState<"pdf" | "jpeg" | "png">("pdf");
  const [error, setError] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  const completed = useMemo(() => REVIEW.filter((item) => Boolean(answers[item.id])).length, [answers]);
  const conclusions = useMemo(() => REVIEW.flatMap((item) => {
    const answer = answers[item.id];
    if (!answer || answer === "Sin alteraciones evidentes" || answer === "Sin hallazgos relevantes" || answer === "No identificados" || answer === "Adecuada" || answer === "Continuidad conservada" || answer === "Sin discrepancias aparentes") return [];
    return [`${item.title}: ${answer}.${details[item.id] ? " " + details[item.id] : ""}`];
  }), [answers, details]);

  if (analysisType === "levandoski") return <Levandoski onBack={() => setAnalysisType("select")} />;
  if (analysisType === "select") return <section className="analysis-page">
    <div className="analysis-heading"><div><button className="text-button" onClick={onBack}>← Volver al inicio</button><p className="eyebrow">AVIS · ANÁLISIS PANORÁMICO</p><h1>Radiografía panorámica</h1><p>Selecciona el tipo de análisis que deseas realizar.</p></div></div>
    <div className="workspace">
      <button className="panel" style={{textAlign:"left",cursor:"pointer",minHeight:180}} onClick={() => setAnalysisType("systematic")}><h2>Análisis sistemático</h2><p>Revisión estructurada en 16 fases: calidad técnica, orientación, anatomía, dentición, soporte óseo y hallazgos.</p><strong>Iniciar revisión sistemática →</strong></button>
      <button className="panel" style={{textAlign:"left",cursor:"pointer",minHeight:180}} onClick={() => setAnalysisType("levandoski")}><h2>Análisis de Levandoski</h2><p>Colocación de puntos anatómicos, trazado de líneas, mediciones bilaterales y cálculo de discrepancias derecha-izquierda.</p><strong>Iniciar análisis de Levandoski →</strong></button>
    </div>
  </section>;
  function loadImage(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    if (file.type && !file.type.startsWith("image/")) { setError("Selecciona una imagen compatible."); return; }
    const reader = new FileReader();
    reader.onload = () => {
      const url = String(reader.result ?? "");
      const image = new Image();
      image.onload = () => {
        const normalized = document.createElement("canvas");
        normalized.width = image.naturalWidth;
        normalized.height = image.naturalHeight;
        const context = normalized.getContext("2d");
        if (!context) { setError("No fue posible preparar la imagen panorámica."); return; }
        context.drawImage(image, 0, 0);
        setPhotoDataUrl(normalized.toDataURL("image/jpeg", 0.94));
        setImageSize({ width: image.naturalWidth, height: image.naturalHeight });
        setFileName(file.name);
        setError("");
      };
      image.onerror = () => setError("No fue posible abrir la imagen seleccionada.");
      image.src = url;
    };
    reader.onerror = () => setError("No fue posible leer el archivo.");
    reader.readAsDataURL(file);
    event.target.value = "";
  }

  function exportJson() {
    const payload = {
      application: "AVIS",
      analysis: "Revisión sistemática de radiografía panorámica",
      fileName, imageSize, status, review: REVIEW.map((item) => ({ phase: item.title, finding: answers[item.id] ?? "Pendiente", detail: details[item.id] ?? "" })),
      presentTeethFDI: presentTeeth,
      observations, professionalConclusion: conclusion, generatedAt: new Date().toISOString(),
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob); const anchor = document.createElement("a");
    anchor.href = url; anchor.download = "AVIS_Panoramica_resultados.json"; anchor.click(); URL.revokeObjectURL(url);
  }

  async function exportReport() {
    if (!photoDataUrl || !imageSize) { setError("Carga la radiografía panorámica antes de generar el informe."); return; }
    try {
      const paletteId = (() => { try { return window.localStorage.getItem("avis.palette") ?? "colibri"; } catch { return "colibri"; } })();
      const activePalette = getAvisPalette(paletteId);
      const palette = activePalette.colors;
      const results = REVIEW.map((item) => ({ label: item.title, value: answers[item.id] ?? "Pendiente", reference: details[item.id] || item.prompt }));
      const reportConclusions = [
        ...conclusions,
        `Revisión sistemática: ${completed} de ${REVIEW.length} fases registradas.`,
        presentTeeth.length ? "Dientes presentes (FDI): " + presentTeeth.join(", ") : "No se registraron dientes presentes en el odontograma.",
        observations ? "Observaciones: " + observations : "",
        conclusion ? "Conclusión profesional: " + conclusion : "",
        "La panorámica es un estudio bidimensional con superposición y distorsión. Los hallazgos deben correlacionarse con exploración clínica y, cuando esté indicado, con proyecciones intraorales o CBCT. No se genera diagnóstico autónomo.",
      ].filter(Boolean);
      const input = {
        title: "Radiografía panorámica · Revisión sistemática",
        mode: "panoramic",
        fileName,
        status,
        photoDataUrl,
        photoWidth: imageSize.width,
        photoHeight: imageSize.height,
        horizontalGuides: false,
        points: {},
        results,
        conclusions: reportConclusions,
        visualAssessment: {},
        observations,
        professionalConclusion: conclusion,
        generatedAt: new Date(),
        palette,
        paletteName: activePalette.name,
        logoDataUrl: await loadAvisLogoDataUrl(),clinicLogoDataUrl:await loadYomDentalLogoDataUrl(activePalette.colors, activePalette.clinicLogoImage),clinicWatermarkDataUrl:await loadYomDentalWatermarkDataUrl(activePalette.colors, activePalette.clinicLogoImage),
        birdIconDataUrl: await loadAvisBirdIconDataUrl(activePalette.birdImage),
        birdWatermarkDataUrl: await loadAvisBirdWatermarkDataUrl(activePalette.birdImage),
        reportLabel: "Reporte panorámico",
      };
      let blob: Blob;
      let extension: string;
      if (format === "pdf") {
        const bytes = buildPhotoReportPdf(input);
        const buffer = new Uint8Array(bytes).buffer as ArrayBuffer;
        blob = new Blob([buffer], { type: "application/pdf" });
        extension = "pdf";
      } else {
        blob = await renderPhotoReportImage(input, format);
        extension = format === "jpeg" ? "jpg" : "png";
      }
      const url = URL.createObjectURL(blob); const anchor = document.createElement("a");
      anchor.href = url; anchor.download = `AVIS_Panoramica_reporte.${extension}`; anchor.click();
      window.setTimeout(() => URL.revokeObjectURL(url), 2000); setError("");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No fue posible generar el informe.");
    }
  }

  return <section className="analysis-page">
    <div className="analysis-heading"><div><button className="text-button" onClick={() => setAnalysisType("select")}>← Cambiar tipo de análisis</button><p className="eyebrow">AVIS · HERRAMIENTA WEB</p><h1>Revisión sistemática panorámica</h1><p>Registra los hallazgos en las 16 fases. La imagen y los datos se procesan localmente.</p></div><span className="module-count">{completed}/16 fases </span></div>
    <div className="guide"><strong>Revisión panorámica sistemática</strong><p>Registra calidad técnica, anatomía, dentición, soporte óseo y hallazgos. Selecciona una opción por fase y añade localización o descripción cuando sea necesario. Las fases son una guía académica, no una lectura diagnóstica automática.</p></div>
    <div className="workspace">
      <section className="panel photo-panel">
        <div className="panel-heading"><div><h2>Imagen panorámica</h2><p>Carga el archivo original para incorporarlo al reporte.</p></div></div>
        <label className="upload-control"><span>＋ Cargar radiografía panorámica</span><input ref={fileRef} type="file" accept="image/*" onChange={loadImage}/></label>
        {fileName && imageSize && <div className="file-meta"><strong>{fileName}</strong><span>{imageSize.width} × {imageSize.height} px</span></div>}
        {photoDataUrl ? <div className="image-viewport"><img src={photoDataUrl} alt="Radiografía panorámica cargada" style={{ display: "block", maxWidth: "none", width: "100%", height: "auto" }}/></div> : <div className="image-empty"><span>▧</span><strong>Radiografía no cargada</strong><p>La imagen se conserva en esta sesión del navegador y se incorpora al informe al exportarlo.</p></div>}
        <div className="form-field">
          <label>Dentición · Odontograma FDI</label>
          <p className="clinical-note">Selecciona los dientes presentes en la radiografía. Los dientes no seleccionados permanecen sin color; al seleccionarlos se resaltan.</p>
          <div style={{display:"grid",gridTemplateColumns:"repeat(4,minmax(0,1fr))",gap:12,marginTop:10}}>
            {([
              {name:"Permanente superior",left:["18","17","16","15","14","13","12","11"],right:["21","22","23","24","25","26","27","28"]},
              {name:"Temporal superior",left:["55","54","53","52","51"],right:["61","62","63","64","65"]},
              {name:"Temporal inferior",left:["85","84","83","82","81"],right:["71","72","73","74","75"]},
              {name:"Permanente inferior",left:["48","47","46","45","44","43","42","41"],right:["31","32","33","34","35","36","37","38"]}
            ] as const).map((row) => (
              <div key={row.name} style={{gridColumn:"span 4",border:"1px solid var(--avis-border,#d8dce3)",borderRadius:12,padding:10}}>
                <strong style={{display:"block",fontSize:13,marginBottom:8}}>{row.name}</strong>
                <div style={{display:"flex",justifyContent:"center",gap:5,flexWrap:"wrap"}}>
                  {[...row.left,...row.right].map((tooth) => {
                    const selected=presentTeeth.includes(tooth);
                    return <button key={tooth} type="button" aria-pressed={selected} aria-label={`Diente ${tooth} ${selected?"presente":"no seleccionado"}`} onClick={()=>setPresentTeeth(prev=>selected?prev.filter(x=>x!==tooth):[...prev,tooth])} style={{width:36,height:42,borderRadius:7,border:selected?"2px solid var(--avis-primary,#6D45A6)":"1px solid #aeb7c2",background:selected?"var(--avis-accent,#22B8B0)":"transparent",color:selected?"#fff":"var(--avis-text,#354052)",fontWeight:700,cursor:"pointer",opacity:selected?1:.62,transition:"background .15s,border-color .15s"}}>{tooth}</button>;
                  })}
                </div>
              </div>
            ))}
          </div>
          <p className="clinical-note">Dientes marcados como presentes: {presentTeeth.length ? presentTeeth.slice().sort((a,b)=>Number(a)-Number(b)).join(", ") : "ninguno"}.</p>
        </div>
        <div className="form-field"><label htmlFor="pano-observations">Observaciones generales</label><textarea id="pano-observations" rows={3} value={observations} onChange={(e) => setObservations(e.target.value)} placeholder="Describe distribución, límites, relación anatómica y correlación clínica…"/></div>
        <div className="form-field"><label htmlFor="pano-conclusion">Conclusión profesional / docente</label><textarea id="pano-conclusion" rows={3} value={conclusion} onChange={(e) => setConclusion(e.target.value)} placeholder="Integra la interpretación revisada por el profesional responsable…"/></div>
      </section>
      <aside className="panel results-panel">
        <div className="panel-heading"><div><h2>Revisión sistemática</h2><p>{completed} de 16 fases registradas.</p></div></div>
        <div className="table-wrap"><table><thead><tr><th>Fase</th><th>Registro</th></tr></thead><tbody>{REVIEW.map((item) => <tr key={item.id}><td>{item.title}<div className="clinical-note">{item.prompt}</div></td><td><select aria-label={item.title} value={answers[item.id] ?? ""} onChange={(e) => setAnswers((prev) => ({ ...prev, [item.id]: e.target.value }))}><option value="">Pendiente</option>{item.options.map((option) => <option key={option}>{option}</option>)}</select><textarea aria-label={"Detalle " + item.title} rows={2} value={details[item.id] ?? ""} onChange={(e) => setDetails((prev) => ({ ...prev, [item.id]: e.target.value }))} placeholder="Localización, límites, dimensiones y descripción…"/></td></tr>)}</tbody></table></div>
        <div className="form-field"><label htmlFor="pano-status">Estado del análisis</label><select id="pano-status" value={status} onChange={(e) => setStatus(e.target.value)}><option>Pendiente</option><option>En proceso</option><option>Completo</option></select></div>
        <div className="form-field"><label htmlFor="pano-format">Formato del informe</label><select id="pano-format" value={format} onChange={(e) => setFormat(e.target.value as "pdf" | "jpeg" | "png")}><option value="pdf">PDF · Informe completo</option><option value="jpeg">JPEG · Imagen del informe</option><option value="png">PNG · Imagen del informe</option></select></div>
        {error && <p className="error-text" role="alert">{error}</p>}
        <button className="primary download-button" onClick={exportReport} disabled={!photoDataUrl}>Descargar reporte {format.toUpperCase()}</button>
        <button className="secondary download-button" onClick={exportJson}>Descargar datos (JSON)</button>
        <p className="clinical-note">La panorámica presenta magnificación, distorsión y superposición. No permite confirmar por sí sola todos los hallazgos. Correlaciona con exploración clínica y estudios complementarios indicados.</p>
      </aside>
    </div>
  </section>;
}
