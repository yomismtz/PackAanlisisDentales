import React, { useEffect, useMemo, useRef, useState } from "react";
import { buildPhotoReportPdf, loadAvisLogoDataUrl, loadAvisBirdIconDataUrl, loadAvisBirdWatermarkDataUrl, loadYomDentalLogoDataUrl, loadYomDentalWatermarkDataUrl } from "./pdfReport";
import { getAvisPalette } from "./themePalettes";
import { calculateCephalometry } from "./cephalometryCalculations";

type XY = { x: number; y: number };
type PointMap = Record<string, XY>;
type RefRow = { key: string; label: string; normal: string; min: number; max: number; unit: string; low: string; normalText: string; high: string };
const LANDMARKS: Array<[string, string]> = [
  ["S", "Sella"], ["N", "Nasion"], ["A", "Punto A"], ["B", "Punto B"], ["D", "Punto D"],
  ["Ar", "Articulare"], ["Go", "Gonion"], ["Gn", "Gnathion"], ["Me", "Menton"],
  ["Pog", "Pogonion"], ["Co", "Contorno posterior del cóndilo"],
  ["U1_tip", "Borde incisal del incisivo superior"], ["U1_apex", "Ápice radicular del incisivo superior"],
  ["L1_tip", "Borde incisal del incisivo inferior"], ["L1_apex", "Ápice radicular del incisivo inferior"],
];
const REFERENCES: RefRow[] = [
  {key:"SNA",label:"SNA",normal:"82° ± 2°",min:80,max:84,unit:"°",low:"Tendencia a retrusión maxilar.",normalText:"Posición maxilar dentro del intervalo de referencia.",high:"Tendencia a protrusión maxilar."},
  {key:"SNB",label:"SNB",normal:"80° ± 2°",min:78,max:82,unit:"°",low:"Tendencia a retrusión mandibular.",normalText:"Posición mandibular dentro del intervalo de referencia.",high:"Tendencia a protrusión mandibular."},
  {key:"ANB",label:"ANB",normal:"2° ± 1°",min:1,max:3,unit:"°",low:"Tendencia a relación esquelética Clase III.",normalText:"Relación sagital esquelética Clase I según esta referencia.",high:"Tendencia a relación esquelética Clase II."},
  {key:"SND",label:"SND",normal:"77° ± 2°",min:75,max:79,unit:"°",low:"Tendencia a retrogenismo de la sínfisis mandibular.",normalText:"Posición de la sínfisis dentro del intervalo de referencia.",high:"Tendencia a progenismo de la sínfisis mandibular."},
  {key:"ArGoMe",label:"Ar-Go-Me · ángulo goniaco",normal:"125° ± 5°",min:120,max:130,unit:"°",low:"Configuración goniaca más cerrada.",normalText:"Ángulo goniaco dentro del intervalo de referencia.",high:"Configuración goniaca más abierta."},
  {key:"GoGnSN",label:"Go-Gn / SN",normal:"32° ± 5°",min:27,max:37,unit:"°",low:"Tendencia a patrón horizontal o rotación anterior.",normalText:"Tendencia a patrón mesofacial.",high:"Tendencia a patrón vertical o rotación posterior."},
  {key:"ABGoGn",label:"AB-Go-Gn",normal:"74° ± 2°",min:72,max:76,unit:"°",low:"Tendencia a mordida abierta.",normalText:"Relación vertical maxilomandibular dentro del intervalo.",high:"Tendencia a mordida profunda."},
  {key:"U1SN",label:"Incisivo superior / SN",normal:"104° ± 2°",min:102,max:106,unit:"°",low:"Tendencia a retroinclinación del incisivo superior.",normalText:"Inclinación del incisivo superior dentro del intervalo.",high:"Tendencia a proinclinación del incisivo superior."},
  {key:"L1NB",label:"Incisivo inferior / NB",normal:"25° ± 4°",min:21,max:29,unit:"°",low:"Tendencia a retroinclinación del incisivo inferior respecto a NB.",normalText:"Inclinación del incisivo inferior respecto a NB dentro de la referencia de trabajo.",high:"Tendencia a proinclinación del incisivo inferior respecto a NB."},
  {key:"IMPA",label:"IMPA · incisivo inferior / Go-Gn",normal:"90° ± 5°",min:85,max:95,unit:"°",low:"Incisivo inferior más retroinclinado respecto al plano mandibular.",normalText:"Inclinación del incisivo inferior respecto al plano mandibular dentro de la referencia de trabajo.",high:"Incisivo inferior más proinclinado respecto al plano mandibular."},
  {key:"Interincisal",label:"Ángulo interincisal U1-L1",normal:"131° ± 6°",min:125,max:137,unit:"°",low:"Ángulo interincisal disminuido; mayor convergencia de los ejes incisales.",normalText:"Relación angular interincisal dentro de la referencia de trabajo.",high:"Ángulo interincisal aumentado; menor convergencia de los ejes incisales."},
  {key:"SL",label:"Segmento SL",normal:"51 mm ± 2 mm",min:49,max:53,unit:" mm",low:"Mandíbula corta o posición de Pogonion más retruida.",normalText:"Posición de Pogonion dentro del intervalo de referencia.",high:"Mandíbula larga o posición de Pogonion más adelantada."},
  {key:"SE",label:"Segmento SE",normal:"22 mm ± 2 mm",min:20,max:24,unit:" mm",low:"Cóndilo en posición más adelantada respecto a SN.",normalText:"Posición condilar dentro del intervalo de referencia.",high:"Cóndilo en posición más retrasada respecto a SN."},
];

const distance = (a: XY,b: XY) => Math.hypot(b.x-a.x,b.y-a.y);
function drawExtendedLine(ctx: CanvasRenderingContext2D, a: XY, b: XY, width: number) {
  const dx=b.x-a.x, dy=b.y-a.y;
  if(Math.hypot(dx,dy)<1e-6)return;
  const candidates:XY[]=[];
  if(Math.abs(dx)>1e-9){for(const x of [0,width]){const t=(x-a.x)/dx;const y=a.y+t*dy;if(y>=0&&y<=ctx.canvas.height)candidates.push({x,y});}}
  if(Math.abs(dy)>1e-9){for(const y of [0,ctx.canvas.height]){const t=(y-a.y)/dy;const x=a.x+t*dx;if(x>=0&&x<=width)candidates.push({x,y});}}
  if(candidates.length<2)return;
  let first=candidates[0],last=candidates[1],max=-1;
  for(let i=0;i<candidates.length;i++)for(let j=i+1;j<candidates.length;j++){const d=distance(candidates[i],candidates[j]);if(d>max){max=d;first=candidates[i];last=candidates[j];}}
  ctx.beginPath();ctx.moveTo(first.x,first.y);ctx.lineTo(last.x,last.y);ctx.stroke();
}
export default function Cephalometry({ onBack }: { onBack: () => void }) {
  const [fileName,setFileName]=useState("");
  const [imageUrl,setImageUrl]=useState("");
  const [imageSize,setImageSize]=useState<{width:number;height:number}|null>(null);
  const [points,setPoints]=useState<PointMap>({});
  const [selected,setSelected]=useState("S");
  const [placing,setPlacing]=useState(false);
  const [zoom,setZoom]=useState(0.7);
  const [calibrationMode,setCalibrationMode]=useState(false);
  const [calibrationPoints,setCalibrationPoints]=useState<XY[]>([]);
  const [knownDistance,setKnownDistance]=useState("10");
  const [pxPerMm,setPxPerMm]=useState<number|null>(null);
  const [error,setError]=useState("");
  const [ageYears,setAgeYears]=useState("");const [sex,setSex]=useState("");const [finalized,setFinalized]=useState(false);
  const canvasRef=useRef<HTMLCanvasElement>(null);
  const imageRef=useRef<HTMLImageElement|null>(null);
  const objectUrlRef=useRef("");
  const result=useMemo(()=>calculateCephalometry(points,pxPerMm),[points,pxPerMm]);
  const placed=Object.keys(points).length;
  useEffect(()=>{const canvas=canvasRef.current, image=imageRef.current;if(!canvas||!image||!imageSize)return;
    canvas.width=imageSize.width;canvas.height=imageSize.height;const ctx=canvas.getContext("2d");if(!ctx)return;
    ctx.clearRect(0,0,canvas.width,canvas.height);ctx.drawImage(image,0,0);
    const palette=getComputedStyle(document.documentElement);const accent=palette.getPropertyValue("--avis-accent").trim()||"#22B8B0";const primary=palette.getPropertyValue("--avis-primary").trim()||"#6D45A6";const plum=palette.getPropertyValue("--avis-plum").trim()||"#48263F";
    const lines:Array<[string,string]>=[["S","N"],["N","A"],["N","B"],["N","D"],["Ar","Go"],["Go","Me"],["Go","Gn"],["A","B"],["U1_apex","U1_tip"],["L1_apex","L1_tip"],["N","B"],["Go","Gn"],["S","L"],["S","E"]];
    ctx.lineWidth=Math.max(1,imageSize.width/1400);
    for(const [index,[a,b]] of lines.entries()){
      const p1=points[a]??result.calculated[a],p2=points[b]??result.calculated[b];
      if(p1&&p2){ctx.strokeStyle=index>=8?"#D98A36":accent;drawExtendedLine(ctx,p1,p2,imageSize.width);}
    }
    // Guías de los ejes incisales y planos cefalométricos prolongadas hasta los bordes
    // para hacer visibles sus intersecciones sobre toda la radiografía.
    for(const [code,p] of Object.entries(points)){const r=Math.max(3,imageSize.width/550);ctx.beginPath();ctx.arc(p.x,p.y,r,0,Math.PI*2);ctx.fillStyle="#fff";ctx.fill();ctx.strokeStyle=primary;ctx.lineWidth=Math.max(1,imageSize.width/1500);ctx.stroke();ctx.fillStyle=plum;ctx.font=`bold ${Math.max(12,imageSize.width/100)}px system-ui`;ctx.fillText(code,p.x+r+4,p.y-r-4);}
    for(const [code,p] of Object.entries(result.calculated)){ctx.beginPath();ctx.arc(p.x,p.y,Math.max(3,imageSize.width/600),0,Math.PI*2);ctx.fillStyle="#F4C95D";ctx.fill();}
    if(calibrationPoints.length===2){ctx.strokeStyle="#E07A5F";ctx.beginPath();ctx.moveTo(calibrationPoints[0].x,calibrationPoints[0].y);ctx.lineTo(calibrationPoints[1].x,calibrationPoints[1].y);ctx.stroke();}
  },[imageUrl,imageSize,points,result.calculated,calibrationPoints]);
  useEffect(()=>()=>{if(objectUrlRef.current)URL.revokeObjectURL(objectUrlRef.current);},[]);
  function loadImage(event:React.ChangeEvent<HTMLInputElement>){const file=event.target.files?.[0];if(!file)return;
    if(file.type&&!file.type.startsWith("image/")){setError("Selecciona un archivo de imagen compatible.");return;}
    if(objectUrlRef.current)URL.revokeObjectURL(objectUrlRef.current);
    const url=URL.createObjectURL(file),img=new Image();
    img.onload=()=>{imageRef.current=img;objectUrlRef.current=url;setImageUrl(url);setImageSize({width:img.naturalWidth,height:img.naturalHeight});setFileName(file.name);setPoints({});setCalibrationPoints([]);setPxPerMm(null);setFinalized(false);setError("");};
    img.onerror=()=>{URL.revokeObjectURL(url);setError("No fue posible abrir la imagen.");};img.src=url;event.target.value="";
  }
  function handleCanvasClick(event:React.MouseEvent<HTMLCanvasElement>){if(!imageSize||finalized)return;const rect=event.currentTarget.getBoundingClientRect();const p={x:(event.clientX-rect.left)/rect.width*imageSize.width,y:(event.clientY-rect.top)/rect.height*imageSize.height};
    if(calibrationMode){const next=[...calibrationPoints,p];if(next.length===2){const px=distance(next[0],next[1]),mm=Number(knownDistance);if(px<=0||!Number.isFinite(mm)||mm<=0){setError("La distancia conocida debe ser mayor que cero.");setCalibrationPoints([]);return;}setCalibrationPoints(next);setPxPerMm(px/mm);setCalibrationMode(false);setError("");}else setCalibrationPoints(next);return;}
    if(placing){setPoints(prev=>({...prev,[selected]:p}));setPlacing(false);setError("");}
  }
  function removePoint(){if(finalized)return;setPoints(prev=>{const next={...prev};delete next[selected];return next;});}
  async function exportPdf(){
    const canvas=canvasRef.current;
    if(!canvas||!imageSize){setError("Carga una radiografía antes de generar el informe.");return;}
    try{
      const paletteId=(()=>{try{return window.localStorage.getItem("avis.palette")??"colibri";}catch{return "colibri";}})();
      const activePalette=getAvisPalette(paletteId);
      const palette=activePalette.colors;
      const rows=REFERENCES.map(r=>({label:r.label,value:result.values[r.key]===undefined?"Pendiente":result.values[r.key].toFixed(2)+r.unit,reference:r.normal}));
      const conclusions=REFERENCES.filter(r=>result.values[r.key]!==undefined).map(r=>{const v=result.values[r.key];return `${r.label}: ${v<r.min?r.low:v>r.max?r.high:r.normalText} Resultado: ${v.toFixed(2)}${r.unit}.`;});
      if(!conclusions.length)conclusions.push("No hay mediciones completas. Coloca los puntos anatómicos requeridos para obtener resultados.");
      conclusions.push("Interpretación descriptiva generada a partir de los puntos colocados. Las referencias son orientativas y deben validarse según edad, población, método cefalométrico y criterio profesional.");
      const pdf=buildPhotoReportPdf({title:"Radiografía lateral de cráneo · Análisis cefalométrico",mode:"cephalometry",fileName,status:"En proceso",photoDataUrl:canvas.toDataURL("image/jpeg",0.92),photoWidth:imageSize.width,photoHeight:imageSize.height,horizontalGuides:false,points,results:rows,conclusions,visualAssessment:{},observations:pxPerMm?`Calibración registrada: ${pxPerMm.toFixed(4)} px/mm. Distancia patrón: ${knownDistance} mm.`:"Sin calibración métrica. Las distancias lineales permanecen pendientes.",professionalConclusion:"Informe de apoyo académico y registro cefalométrico. Verificar la identificación de los puntos, la orientación de los ejes y las referencias antes de tomar decisiones clínicas.",generatedAt:new Date(),palette,paletteName:activePalette.name,logoDataUrl:await loadAvisLogoDataUrl(),clinicLogoDataUrl:await loadYomDentalLogoDataUrl(activePalette.colors),clinicWatermarkDataUrl:await loadYomDentalWatermarkDataUrl(activePalette.colors),birdIconDataUrl:await loadAvisBirdIconDataUrl(activePalette.birdImage),birdWatermarkDataUrl:await loadAvisBirdWatermarkDataUrl(activePalette.birdImage),reportLabel:"Análisis cefalométrico"});
      const pdfBuffer=new Uint8Array(pdf).buffer as ArrayBuffer;const blob=new Blob([pdfBuffer],{type:"application/pdf"});const url=URL.createObjectURL(blob);const a=document.createElement("a");a.href=url;a.download="AVIS_Reporte_Cefalometria_Lateral.pdf";a.click();URL.revokeObjectURL(url);setError("");
    }catch(e){setError(e instanceof Error?e.message:"No fue posible generar el informe PDF.");}
  }
  function csvCell(value:unknown){const text=String(value??"");return /[",\\n]/.test(text)?'"'+text.replace(/"/g,'""')+'"':text;}
  function downloadBlob(blob:Blob,name:string){const url=URL.createObjectURL(blob);const a=document.createElement("a");a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1500);}
  function canvasBlob(canvas:HTMLCanvasElement){return new Promise<Blob>((resolve,reject)=>canvas.toBlob(blob=>blob?resolve(blob):reject(new Error("No fue posible crear la imagen PNG.")),"image/png"));}
  async function exportJson(){if(!finalized||!imageSize||!imageRef.current){setError("Finaliza el caso antes de exportar los datos de investigación.");return;}const payload={schemaVersion:"1.0.0",study:"AVIS-100",application:"AVIS",moduleVersion:"Análisis cefalométrico",analysis:"Radiografía lateral de cráneo",patient:{ageYears:Number(ageYears),sex},image:{fileName,width:imageSize.width,height:imageSize.height,coordinateSystem:"pixels_from_original_image"},unit:pxPerMm?"mm_calibrados_y_grados":"px_relativos_y_grados",pixelsPerMm:pxPerMm,calibration:{points:calibrationPoints,knownDistanceMm:Number(knownDistance)||null},points,calculatedPoints:result.calculated,measurements:REFERENCES.map(r=>({key:r.key,label:r.label,value:result.values[r.key]??null,unit:r.unit.trim()||"°",reference:r.normal,status:result.values[r.key]===undefined?"Pendiente":result.values[r.key]<r.min?"Disminuido":result.values[r.key]>r.max?"Aumentado":"Dentro de norma"})),placementProtocol:{placementsPerCase:1,operatorCount:1,finalized:true},limitations:["Una sola colocación por caso; no estima reproducibilidad intraobservador ni interobservador.","Coordenadas en píxeles de la imagen original.","Las distancias lineales solo se interpretan con calibración registrada; la calibración no elimina magnificación diferencial."],generatedAt:new Date().toISOString()};downloadBlob(new Blob([JSON.stringify(payload,null,2)],{type:"application/json"}),`AVIS_Cefalometria_datos.json`);const rows=[["tipo","codigo","etiqueta","valor_1","valor_2","unidad"],...LANDMARKS.map(([code,label])=>["punto",code,label,points[code]?.x??"",points[code]?.y??"","px"]),...REFERENCES.map(r=>["medicion",r.key,r.label,result.values[r.key]??"","",r.unit.trim()||"°"])];downloadBlob(new Blob([rows.map(row=>row.map(csvCell).join(",")).join("\\n")],{type:"text/csv;charset=utf-8"}),`AVIS_Cefalometria_datos.csv`);if(canvasRef.current)downloadBlob(await canvasBlob(canvasRef.current),`AVIS_Cefalometria_trazado.png`);const original=document.createElement("canvas");original.width=imageSize.width;original.height=imageSize.height;const context=original.getContext("2d");if(context){context.drawImage(imageRef.current,0,0);downloadBlob(await canvasBlob(original),`AVIS_Cefalometria_original.png`);}}

  return <section className="analysis-page">
    <div className="analysis-heading"><div><button className="text-button" onClick={onBack}>← Reiniciar estudio</button><p className="eyebrow">AVIS · HERRAMIENTA WEB</p><h1>Radiografía lateral de cráneo · Análisis cefalométrico</h1><p>Coloca manualmente los puntos anatómicos. Los cálculos se actualizan conforme completas el trazado.</p></div><span className="module-count">{placed} / {LANDMARKS.length} puntos</span></div>
    <div className="guide"><strong>Datos del análisis</strong><div className="form-field"><label htmlFor="ceph-age-years">Edad (años)</label><input id="ceph-age-years" type="number" min="0" max="120" step="0.1" value={ageYears} onChange={e=>setAgeYears(e.target.value)} disabled={finalized}/></div><div className="form-field"><label htmlFor="ceph-sex">Sexo</label><select id="ceph-sex" value={sex} onChange={e=>setSex(e.target.value)} disabled={finalized}><option value="">Seleccionar</option><option>Femenino</option><option>Masculino</option><option>Otro / no especificado</option><option>No registrado</option></select></div><p className="clinical-note">Puedes revisar y corregir los puntos antes de finalizar el análisis.</p><button className="primary" disabled={finalized||!ageYears.trim()||!Number.isFinite(Number(ageYears))||Number(ageYears)<0||!sex||!imageSize||placed===0} onClick={()=>{setFinalized(true);setPlacing(false);setCalibrationMode(false);setError("");}}>Finalizar análisis ({placed}/{LANDMARKS.length} puntos)</button>{finalized&&<p className="clinical-note">Análisis finalizado. El trazado queda bloqueado.</p>}</div>
    <div className="workspace">
      <section className="panel photo-panel"><div className="panel-heading"><div><h2>Radiografía y trazado</h2><p>Sube una radiografía lateral, selecciona un punto y colócalo sobre la imagen.</p></div></div>
        <label className="upload-control"><span>＋ Cargar radiografía lateral</span><input type="file" accept="image/*" onChange={loadImage}/></label>
        {fileName&&imageSize&&<div className="file-meta"><strong>{fileName}</strong><span>{imageSize.width} × {imageSize.height} px</span></div>}
        {error&&<p className="error-text" role="alert">{error}</p>}
        {imageUrl&&imageSize?<><div className="zoom-row"><label htmlFor="ceph-zoom">Zoom</label><input id="ceph-zoom" type="range" min="0.2" max="3" step="0.05" value={zoom} onChange={e=>setZoom(Number(e.target.value))}/><span>{Math.round(zoom*100)} %</span><button className="small-button" onClick={()=>setZoom(.7)}>Restablecer</button></div><div className="image-viewport"><canvas ref={canvasRef} onClick={handleCanvasClick} style={{width:imageSize.width*zoom,height:imageSize.height*zoom,cursor:placing||calibrationMode?"crosshair":"default"}}/></div>
          {placing&&<p className="placement-hint">Haz clic para colocar <strong>{selected}</strong> · {LANDMARKS.find(p=>p[0]===selected)?.[1]}</p>}
          {calibrationMode&&<p className="placement-hint">Marca dos puntos que correspondan a una distancia conocida.</p>}
        </>:<div className="image-empty"><span>▧</span><strong>Radiografía no cargada</strong><p>La imagen se procesa localmente en este navegador. Utiliza una imagen desidentificada para las pruebas.</p></div>}
        <div className="point-controls"><label htmlFor="ceph-point">Punto anatómico</label><select id="ceph-point" value={selected} onChange={e=>setSelected(e.target.value)}>{LANDMARKS.map(([code,label])=><option key={code} value={code}>{code} · {label}</option>)}</select>
          <div className="point-actions"><button className="primary" disabled={finalized||!imageUrl} onClick={()=>{setCalibrationMode(false);setPlacing(true);}}>Colocar / corregir</button><button className="secondary" disabled={finalized||!points[selected]} onClick={removePoint}>Eliminar punto</button><span className="point-progress">{placed} / {LANDMARKS.length}</span></div>
          <div className="point-list">{LANDMARKS.map(([code])=><button key={code} className={points[code]?"point-chip point-done":"point-chip"} onClick={()=>setSelected(code)}>{points[code]?"✓ ":""}{code}</button>)}</div>
        </div>
        <div className="point-controls"><h3>Calibración de distancias</h3><p className="clinical-note">Opcional. Usa una referencia física conocida y situada en el mismo plano de la imagen. La calibración no corrige magnificación diferencial ni distorsión.</p><label className="visual-field"><span>Distancia conocida (mm)</span><input className="calibration-input" type="number" min="0.01" step="0.01" value={knownDistance} onChange={e=>{setKnownDistance(e.target.value);setPxPerMm(null);setCalibrationPoints([]);setCalibrationMode(false);}}/></label>
          <div className="point-actions"><button className="secondary" disabled={finalized||!imageUrl} onClick={()=>{if(calibrationMode){setCalibrationMode(false);setCalibrationPoints([]);}else{setCalibrationPoints([]);setPxPerMm(null);setCalibrationMode(true);setPlacing(false);setError("");}}}>{calibrationMode?"Cancelar calibración":"Marcar dos puntos de calibración"}</button><span className="point-progress">{pxPerMm?pxPerMm.toFixed(3)+" px/mm":"Sin calibrar"}</span></div>
          {pxPerMm&&<button className="small-button" onClick={()=>{setPxPerMm(null);setCalibrationPoints([]);}}>Eliminar calibración</button>}
        </div>
      </section>
      <aside className="panel results-panel"><div className="panel-heading"><div><h2>Mediciones cefalométricas</h2><p>Resultados parciales; no se completan valores faltantes.</p></div></div>
        <div className="unit-notice">Los ángulos son independientes de la escala. SL y SE requieren calibración válida; sin ella permanecen pendientes.</div>
        <div className="table-wrap"><table><thead><tr><th>Medición</th><th>Resultado</th><th>Referencia</th><th>Estado</th></tr></thead><tbody>{REFERENCES.map(r=>{const v=result.values[r.key];const state=v===undefined?"Pendiente":v<r.min?"Disminuido":v>r.max?"Aumentado":"Dentro de norma";return <tr key={r.key}><td>{r.label}</td><td className="result-value">{v===undefined?"—":v.toFixed(2)+r.unit}</td><td>{r.normal}</td><td>{state}</td></tr>;})}</tbody></table></div>
        <section className="automatic-conclusions"><div className="conclusions-heading"><h3>Lectura descriptiva</h3><span>Referencia de trabajo</span></div><ul>{REFERENCES.filter(r=>result.values[r.key]!==undefined).map(r=>{const v=result.values[r.key];return <li key={r.key}><strong>{r.key}:</strong> {v<r.min?r.low:v>r.max?r.high:r.normalText}</li>;})}</ul>{!Object.keys(result.values).length&&<p className="empty-conclusions">Coloca puntos anatómicos para iniciar los cálculos.</p>}</section>
        <button className="primary download-button" disabled={!imageUrl} onClick={exportPdf}>Descargar informe cefalométrico (PDF)</button><button className="secondary download-button" disabled={!placed} onClick={exportJson}>Descargar datos del análisis (JSON)</button><p className="clinical-note">Apoyo académico para trazado y medición. No constituye diagnóstico autónomo. Confirma puntos, referencias y calibración antes de interpretar. El JSON no incluye la radiografía.</p>
      </aside>
    </div>
  </section>;
}
