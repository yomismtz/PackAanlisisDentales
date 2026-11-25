import React, { useEffect, useMemo, useRef, useState } from "react";

type XY = { x: number; y: number };
type PointMap = Record<string, XY>;
type RefRow = { key: string; label: string; normal: string; min: number; max: number; unit: string; low: string; normalText: string; high: string };
const LANDMARKS: Array<[string, string]> = [
  ["S", "Sella"], ["N", "Nasion"], ["A", "Punto A"], ["B", "Punto B"], ["D", "Punto D"],
  ["Ar", "Articulare"], ["Go", "Gonion"], ["Gn", "Gnathion"], ["Me", "Menton"],
  ["Pog", "Pogonion"], ["Co", "Contorno posterior del cóndilo"],
  ["U1_tip", "Borde incisal del incisivo superior"], ["U1_apex", "Ápice radicular del incisivo superior"],
];
const REFERENCES: RefRow[] = [
  {key:"SNA",label:"SNA",normal:"82° ± 2°",min:80,max:84,unit:"°",low:"Tendencia a retrusión maxilar.",normalText:"Posición maxilar dentro del intervalo de referencia.",high:"Tendencia a protrusión maxilar."},
  {key:"SNB",label:"SNB",normal:"80° ± 2°",min:78,max:82,unit:"°",low:"Tendencia a retrusión mandibular.",normalText:"Posición mandibular dentro del intervalo de referencia.",high:"Tendencia a protrusión mandibular."},
  {key:"ANB",label:"ANB",normal:"2° ± 1°",min:1,max:3,unit:"°",low:"Tendencia a relación esquelética Clase III.",normalText:"Relación sagital esquelética Clase I según esta referencia.",high:"Tendencia a relación esquelética Clase II."},
  {key:"SND",label:"SND",normal:"77° ± 2°",min:75,max:79,unit:"°",low:"Tendencia a retrogenismo de la sínfisis mandibular.",normalText:"Posición de la sínfisis dentro del intervalo de referencia.",high:"Tendencia a progenismo de la sínfisis mandibular."},
  {key:"ArGoMe",label:"Ar-Go-Me · ángulo goniaco",normal:"125° ± 2°",min:123,max:127,unit:"°",low:"Configuración goniaca más cerrada.",normalText:"Ángulo goniaco dentro del intervalo de referencia.",high:"Configuración goniaca más abierta."},
  {key:"GoGnSN",label:"Go-Gn / SN",normal:"32° ± 5°",min:27,max:37,unit:"°",low:"Tendencia a patrón horizontal o rotación anterior.",normalText:"Tendencia a patrón mesofacial.",high:"Tendencia a patrón vertical o rotación posterior."},
  {key:"ABGoGn",label:"AB-Go-Gn",normal:"74° ± 2°",min:72,max:76,unit:"°",low:"Tendencia a mordida abierta.",normalText:"Relación vertical maxilomandibular dentro del intervalo.",high:"Tendencia a mordida profunda."},
  {key:"U1SN",label:"Incisivo superior / SN",normal:"104° ± 2°",min:102,max:106,unit:"°",low:"Tendencia a retroinclinación del incisivo superior.",normalText:"Inclinación del incisivo superior dentro del intervalo.",high:"Tendencia a proinclinación del incisivo superior."},
  {key:"SL",label:"Segmento SL",normal:"51 mm ± 2 mm",min:49,max:53,unit:" mm",low:"Mandíbula corta o posición de Pogonion más retruida.",normalText:"Posición de Pogonion dentro del intervalo de referencia.",high:"Mandíbula larga o posición de Pogonion más adelantada."},
  {key:"SE",label:"Segmento SE",normal:"23 mm ± 2 mm",min:21,max:25,unit:" mm",low:"Cóndilo en posición más adelantada respecto a SN.",normalText:"Posición condilar dentro del intervalo de referencia.",high:"Cóndilo en posición más retrasada respecto a SN."},
];
const distance = (a: XY,b: XY) => Math.hypot(b.x-a.x,b.y-a.y);
function angleAt(a: XY,v: XY,b: XY) {
  const ax=a.x-v.x, ay=a.y-v.y, bx=b.x-v.x, by=b.y-v.y, den=Math.hypot(ax,ay)*Math.hypot(bx,by);
  if (!den) return null;
  return Math.acos(Math.max(-1,Math.min(1,(ax*bx+ay*by)/den)))*180/Math.PI;
}
function angleLines(a: XY,b: XY,c: XY,d: XY) {
  const one=Math.atan2(b.y-a.y,b.x-a.x), two=Math.atan2(d.y-c.y,d.x-c.x);
  const delta=Math.abs(((one-two+Math.PI)%(2*Math.PI)+2*Math.PI)%(2*Math.PI)-Math.PI);
  return Math.min(delta,180-delta);
}
function project(p: XY,a: XY,b: XY): XY | null {
  const dx=b.x-a.x,dy=b.y-a.y,len=dx*dx+dy*dy;
  if (!len) return null;
  const t=((p.x-a.x)*dx+(p.y-a.y)*dy)/len;
  return {x:a.x+t*dx,y:a.y+t*dy};
}
function calculate(points: PointMap, pxPerMm: number | null) {
  const values: Record<string,number> = {};
  const put=(key:string,value:number|null)=>{if(value!==null && Number.isFinite(value)) values[key]=value;};
  const p=(key:string)=>points[key];
  if(p("S")&&p("N")&&p("A")) put("SNA",angleAt(p("S"),p("N"),p("A")));
  if(p("S")&&p("N")&&p("B")) put("SNB",angleAt(p("S"),p("N"),p("B")));
  if(values.SNA!==undefined&&values.SNB!==undefined) put("ANB",values.SNA-values.SNB);
  if(p("S")&&p("N")&&p("D")) put("SND",angleAt(p("S"),p("N"),p("D")));
  if(p("Ar")&&p("Go")&&p("Me")) put("ArGoMe",angleAt(p("Ar"),p("Go"),p("Me")));
  if(p("S")&&p("N")&&p("Go")&&p("Gn")) put("GoGnSN",angleLines(p("S"),p("N"),p("Go"),p("Gn")));
  if(p("A")&&p("B")&&p("Go")&&p("Gn")) put("ABGoGn",angleLines(p("A"),p("B"),p("Go"),p("Gn")));
  if(p("S")&&p("N")&&p("U1_apex")&&p("U1_tip")) put("U1SN",180-angleLines(p("S"),p("N"),p("U1_apex"),p("U1_tip")));
  const calculated: PointMap = {};
  if(p("S")&&p("N")&&p("Pog")) { const l=project(p("Pog"),p("S"),p("N")); if(l){calculated.L=l;if(pxPerMm)put("SL",distance(p("S"),l)/pxPerMm);} }
  if(p("S")&&p("N")&&p("Co")) { const e=project(p("Co"),p("S"),p("N")); if(e){calculated.E=e;if(pxPerMm)put("SE",distance(p("S"),e)/pxPerMm);} }
  return {values,calculated};
}

export default function Cephalometry() {
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
  const canvasRef=useRef<HTMLCanvasElement>(null);
  const imageRef=useRef<HTMLImageElement|null>(null);
  const objectUrlRef=useRef("");
  const result=useMemo(()=>calculate(points,pxPerMm),[points,pxPerMm]);
  const placed=Object.keys(points).length;
  useEffect(()=>{const canvas=canvasRef.current, image=imageRef.current;if(!canvas||!image||!imageSize)return;
    canvas.width=imageSize.width;canvas.height=imageSize.height;const ctx=canvas.getContext("2d");if(!ctx)return;
    ctx.clearRect(0,0,canvas.width,canvas.height);ctx.drawImage(image,0,0);
    const lines:Array<[string,string]>=[["S","N"],["N","A"],["N","B"],["N","D"],["Ar","Go"],["Go","Me"],["Go","Gn"],["A","B"],["U1_apex","U1_tip"],["S","L"],["S","E"]];
    ctx.strokeStyle="#22B8B0";ctx.lineWidth=Math.max(1,imageSize.width/1200);
    for(const [a,b] of lines){const p1=points[a]??result.calculated[b],p2=points[b]??result.calculated[a];if(p1&&p2){ctx.beginPath();ctx.moveTo(p1.x,p1.y);ctx.lineTo(p2.x,p2.y);ctx.stroke();}}
    for(const [code,p] of Object.entries(points)){const r=Math.max(3,imageSize.width/550);ctx.beginPath();ctx.arc(p.x,p.y,r,0,Math.PI*2);ctx.fillStyle="#fff";ctx.fill();ctx.strokeStyle="#6D45A6";ctx.lineWidth=Math.max(1,imageSize.width/1500);ctx.stroke();ctx.fillStyle="#48263F";ctx.font=`bold ${Math.max(12,imageSize.width/100)}px system-ui`;ctx.fillText(code,p.x+r+4,p.y-r-4);}
    for(const [code,p] of Object.entries(result.calculated)){ctx.beginPath();ctx.arc(p.x,p.y,Math.max(3,imageSize.width/600),0,Math.PI*2);ctx.fillStyle="#F4C95D";ctx.fill();}
    if(calibrationPoints.length===2){ctx.strokeStyle="#E07A5F";ctx.beginPath();ctx.moveTo(calibrationPoints[0].x,calibrationPoints[0].y);ctx.lineTo(calibrationPoints[1].x,calibrationPoints[1].y);ctx.stroke();}
  },[imageUrl,imageSize,points,result.calculated,calibrationPoints]);
  useEffect(()=>()=>{if(objectUrlRef.current)URL.revokeObjectURL(objectUrlRef.current);},[]);
  function loadImage(event:React.ChangeEvent<HTMLInputElement>){const file=event.target.files?.[0];if(!file)return;
    if(file.type&&!file.type.startsWith("image/")){setError("Selecciona un archivo de imagen compatible.");return;}
    if(objectUrlRef.current)URL.revokeObjectURL(objectUrlRef.current);
    const url=URL.createObjectURL(file),img=new Image();
    img.onload=()=>{imageRef.current=img;objectUrlRef.current=url;setImageUrl(url);setImageSize({width:img.naturalWidth,height:img.naturalHeight});setFileName(file.name);setPoints({});setCalibrationPoints([]);setPxPerMm(null);setError("");};
    img.onerror=()=>{URL.revokeObjectURL(url);setError("No fue posible abrir la imagen.");};img.src=url;event.target.value="";
  }
  function handleCanvasClick(event:React.MouseEvent<HTMLCanvasElement>){if(!imageSize)return;const rect=event.currentTarget.getBoundingClientRect();const p={x:(event.clientX-rect.left)/rect.width*imageSize.width,y:(event.clientY-rect.top)/rect.height*imageSize.height};
    if(calibrationMode){const next=[...calibrationPoints,p];if(next.length===2){const px=distance(next[0],next[1]),mm=Number(knownDistance);if(px<=0||!Number.isFinite(mm)||mm<=0){setError("La distancia conocida debe ser mayor que cero.");setCalibrationPoints([]);return;}setCalibrationPoints(next);setPxPerMm(px/mm);setCalibrationMode(false);setError("");}else setCalibrationPoints(next);return;}
    if(placing){setPoints(prev=>({...prev,[selected]:p}));setPlacing(false);setError("");}
  }
  function removePoint(){setPoints(prev=>{const next={...prev};delete next[selected];return next;});}
  function exportJson(){const payload={application:"AVIS",analysis:"Steiner · radiografía lateral de cráneo",image:{fileName,width:imageSize?.width??null,height:imageSize?.height??null},unit:pxPerMm?"mm_calibrados_y_grados":"px_relativos_y_grados",pixelsPerMm:pxPerMm,calibration:{points:calibrationPoints,knownDistanceMm:Number(knownDistance)||null},points,calculatedPoints:result.calculated,measurements:REFERENCES.map(r=>({key:r.key,label:r.label,value:result.values[r.key]??null,unit:r.unit.trim()||"°",reference:r.normal,status:result.values[r.key]===undefined?"Pendiente":result.values[r.key]<r.min?"Disminuido":result.values[r.key]>r.max?"Aumentado":"Dentro de norma"})),generatedAt:new Date().toISOString()};const blob=new Blob([JSON.stringify(payload,null,2)],{type:"application/json"});const url=URL.createObjectURL(blob);const a=document.createElement("a");a.href=url;a.download="AVIS_Steiner_resultados.json";a.click();URL.revokeObjectURL(url);}
  return <section className="analysis-page">
    <div className="analysis-heading"><div><button className="text-button" onClick={()=>{setImageUrl("");setFileName("");}}>← Reiniciar estudio</button><p className="eyebrow">AVIS · HERRAMIENTA WEB</p><h1>Radiografía lateral de cráneo · Steiner</h1><p>Coloca manualmente los puntos anatómicos. Los cálculos se actualizan conforme completas el trazado.</p></div><span className="module-count">{placed} / {LANDMARKS.length} puntos</span></div>
    <div className="guide"><strong>Uso académico y trazado manual</strong><p>Los ángulos se calculan en grados. SL y SE solo se expresan en milímetros cuando registras una calibración con una distancia conocida. La referencia numérica debe revisarse según la población, edad y criterio profesional.</p></div>
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
          <div className="point-actions"><button className="primary" disabled={!imageUrl} onClick={()=>{setCalibrationMode(false);setPlacing(true);}}>Colocar / corregir</button><button className="secondary" disabled={!points[selected]} onClick={removePoint}>Eliminar punto</button><span className="point-progress">{placed} / {LANDMARKS.length}</span></div>
          <div className="point-list">{LANDMARKS.map(([code])=><button key={code} className={points[code]?"point-chip point-done":"point-chip"} onClick={()=>setSelected(code)}>{points[code]?"✓ ":""}{code}</button>)}</div>
        </div>
        <div className="point-controls"><h3>Calibración de distancias</h3><p className="clinical-note">Opcional. Usa una referencia física conocida y situada en el mismo plano de la imagen. La calibración no corrige magnificación diferencial ni distorsión.</p><label className="visual-field"><span>Distancia conocida (mm)</span><input className="calibration-input" type="number" min="0.01" step="0.01" value={knownDistance} onChange={e=>setKnownDistance(e.target.value)}/></label>
          <div className="point-actions"><button className="secondary" disabled={!imageUrl} onClick={()=>{setCalibrationPoints([]);setCalibrationMode(true);setPlacing(false);setError("");}}>Marcar dos puntos de calibración</button><span className="point-progress">{pxPerMm?pxPerMm.toFixed(3)+" px/mm":"Sin calibrar"}</span></div>
          {pxPerMm&&<button className="small-button" onClick={()=>{setPxPerMm(null);setCalibrationPoints([]);}}>Eliminar calibración</button>}
        </div>
      </section>
      <aside className="panel results-panel"><div className="panel-heading"><div><h2>Mediciones de Steiner</h2><p>Resultados parciales; no se completan valores faltantes.</p></div></div>
        <div className="unit-notice">Los ángulos son independientes de la escala. SL y SE requieren calibración válida; sin ella permanecen pendientes.</div>
        <div className="table-wrap"><table><thead><tr><th>Medición</th><th>Resultado</th><th>Referencia</th><th>Estado</th></tr></thead><tbody>{REFERENCES.map(r=>{const v=result.values[r.key];const state=v===undefined?"Pendiente":v<r.min?"Disminuido":v>r.max?"Aumentado":"Dentro de norma";return <tr key={r.key}><td>{r.label}</td><td className="result-value">{v===undefined?"—":v.toFixed(2)+r.unit}</td><td>{r.normal}</td><td>{state}</td></tr>;})}</tbody></table></div>
        <section className="automatic-conclusions"><div className="conclusions-heading"><h3>Lectura descriptiva</h3><span>Referencia de trabajo</span></div><ul>{REFERENCES.filter(r=>result.values[r.key]!==undefined).map(r=>{const v=result.values[r.key];return <li key={r.key}><strong>{r.key}:</strong> {v<r.min?r.low:v>r.max?r.high:r.normalText}</li>;})}</ul>{!Object.keys(result.values).length&&<p className="empty-conclusions">Coloca puntos anatómicos para iniciar los cálculos.</p>}</section>
        <button className="primary download-button" disabled={!placed} onClick={exportJson}>Descargar resultados (JSON)</button><p className="clinical-note">Apoyo académico para trazado y medición. No constituye diagnóstico autónomo. Confirma puntos, referencias y calibración antes de interpretar. El JSON no incluye la radiografía.</p>
      </aside>
    </div>
  </section>;
}
