import React, { useEffect, useMemo, useRef, useState } from "react";
import { buildPhotoReportPdf, loadAvisLogoDataUrl, loadAvisBirdIconDataUrl, loadAvisBirdWatermarkDataUrl } from "./pdfReport";
import { getAvisPalette } from "./themePalettes";
import IntermaxillaryRelations from "./IntermaxillaryRelations";
import { careySpaceAnalysis, classifySpaceRange, littleIrregularityIndex, moyers75Prediction, pixelsPerMillimeter, pixelsToMillimeters, polylineLength, tanakaJohnstonPrediction } from "./modelGeometry";

type XY = { x:number; y:number };
type ViewKey = "incisors" | "upper" | "lower";
type ImageInfo = { url:string; name:string; width:number; height:number };
type PointSets = Record<ViewKey,Record<string,XY>>;
type TraceSets = Record<ViewKey,Record<string,XY[]>>;
type Method = "little" | "moyers" | "tanaka" | "carey" | "intermaxillary";
const EMPTY_POINTS:PointSets={incisors:{},upper:{},lower:{}};
const EMPTY_TRACES:TraceSets={incisors:{},upper:{},lower:{}};
const LITTLE_CONTACTS=[
 {id:"43/42",a:"43_M",b:"42_D",aLabel:"43 · mesial",bLabel:"42 · distal"},
 {id:"42/41",a:"42_M",b:"41_D",aLabel:"42 · mesial",bLabel:"41 · distal"},
 {id:"41/31",a:"41_M",b:"31_M",aLabel:"41 · mesial",bLabel:"31 · mesial"},
 {id:"31/32",a:"31_D",b:"32_M",aLabel:"31 · distal",bLabel:"32 · mesial"},
 {id:"32/33",a:"32_D",b:"33_M",aLabel:"32 · distal",bLabel:"33 · mesial"}
] as const;
const INCISORS=["42","41","31","32"];
const CAREY_TEETH:Record<"upper"|"lower",string[]>={upper:["15","14","13","12","11","21","22","23","24","25"],lower:["45","44","43","42","41","31","32","33","34","35"]};
const distance=(a:XY,b:XY)=>Math.hypot(b.x-a.x,b.y-a.y);
function pathLength(path:XY[]){return polylineLength(path);}
function pointOptions(method:Method,view:ViewKey){
 if(method==="intermaxillary")return [];
 if(method==="little")return view==="upper"||view==="lower"?LITTLE_CONTACTS.flatMap(c=>[[c.a,c.aLabel],[c.b,c.bLabel]] as [string,string][]):[];
 if(method==="carey")return CAREY_TEETH[view==="upper"?"upper":"lower"].flatMap(t=>[[t+"_M",t+" · mesial"],[t+"_D",t+" · distal"]]);
 if(view==="incisors")return INCISORS.flatMap(t=>[[t+"_M",t+" · mesial"],[t+"_D",t+" · distal"]]);
 return [["lat_R","Lateral · distal derecho"],["mol_R","Primer molar · mesial derecho"],["lat_L","Lateral · distal izquierdo"],["mol_L","Primer molar · mesial izquierdo"]];
}
function classifyRange(available:[number,number]|null,required:[number,number]|null){
 return classifySpaceRange(available,required);
}
export default function ModelAnalysis({onBack,paletteId}:{onBack:()=>void;paletteId:string}){
 const [method,setMethod]=useState<Method>("little");
 const [view,setView]=useState<ViewKey>("lower");
 const [images,setImages]=useState<Partial<Record<ViewKey,ImageInfo>>>({});
 const objectUrls=useRef<Set<string>>(new Set());
 const [points,setPoints]=useState<PointSets>(EMPTY_POINTS);
 const [traces,setTraces]=useState<TraceSets>(EMPTY_TRACES);
 const [selected,setSelected]=useState<string>(LITTLE_CONTACTS[0].a);
 const [placing,setPlacing]=useState(false);
 const [traceMode,setTraceMode]=useState("");
 const [zoom,setZoom]=useState(.7);
 const [sex,setSex]=useState<"Seleccionar"|"Femenino"|"Masculino">("Seleccionar");
 const [calibration,setCalibration]=useState<Partial<Record<ViewKey,{pxPerMm:number;knownDistanceMm:number;points:[XY,XY]}>>>({});
 const [calibrationMode,setCalibrationMode]=useState(false);
 const [calibrationPoints,setCalibrationPoints]=useState<XY[]>([]);
 const [knownDistanceMm,setKnownDistanceMm]=useState("10");
 const [error,setError]=useState("");
 const canvasRef=useRef<HTMLCanvasElement>(null);
 const image=images[view];
 const options=pointOptions(method,view);
 const [observations,setObservations]=useState("");
 const [conclusion,setConclusion]=useState("");
 useEffect(()=>()=>{objectUrls.current.forEach(url=>URL.revokeObjectURL(url));objectUrls.current.clear();},[]);
 useEffect(()=>{
  const canvas=canvasRef.current;if(!canvas||!image)return;
  const img=new Image();
  img.onload=()=>{
   canvas.width=img.naturalWidth;canvas.height=img.naturalHeight;
   const ctx=canvas.getContext("2d");if(!ctx)return;
   ctx.clearRect(0,0,canvas.width,canvas.height);ctx.drawImage(img,0,0);
   const current=points[view];const currentTraces=traces[view];
   ctx.lineWidth=Math.max(2,img.naturalWidth/1000);ctx.strokeStyle="#22B8B0";
   const drawPath=(items:XY[],color:string)=>{if(items.length<2)return;ctx.beginPath();ctx.strokeStyle=color;ctx.moveTo(items[0].x,items[0].y);items.slice(1).forEach(p=>ctx.lineTo(p.x,p.y));ctx.stroke();};
   if(method==="carey")drawPath(currentTraces.perimeter??[],"#F4C95D");
   else {drawPath(currentTraces.Derecho??[],"#22B8B0");drawPath(currentTraces.Izquierdo??[],"#22B8B0");}
   if(method==="little"){for(const pair of LITTLE_CONTACTS){const a=current[pair.a],b=current[pair.b];if(a&&b){ctx.beginPath();ctx.strokeStyle="#22B8B0";ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();}}}
   if(method==="carey"){for(const tooth of CAREY_TEETH[view==="upper"?"upper":"lower"]){const a=current[tooth+"_M"],b=current[tooth+"_D"];if(a&&b){ctx.beginPath();ctx.strokeStyle="#22B8B0";ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();}}}
   if(method==="moyers"||method==="tanaka"){
    const pairs=view==="incisors"?INCISORS.map(t=>[t+"_M",t+"_D"]):[];
    for(const [a,b] of pairs){const p=current[a],q=current[b];if(p&&q){ctx.beginPath();ctx.strokeStyle="#F4C95D";ctx.moveTo(p.x,p.y);ctx.lineTo(q.x,q.y);ctx.stroke();}}
    for(const side of ["Derecho","Izquierdo"]){const start=current[side==="Derecho"?"lat_R":"lat_L"],end=current[side==="Derecho"?"mol_R":"mol_L"];const path=currentTraces[side]??[];if(start&&end)drawPath([start,...path,end],"#22B8B0");}
   }
   for(const [key,p] of Object.entries(current)){const r=Math.max(3,img.naturalWidth/600);ctx.beginPath();ctx.arc(p.x,p.y,r,0,Math.PI*2);ctx.fillStyle="#fff";ctx.fill();ctx.strokeStyle="#6D45A6";ctx.lineWidth=Math.max(1,img.naturalWidth/1500);ctx.stroke();ctx.fillStyle="#48263F";ctx.font=`bold ${Math.max(12,img.naturalWidth/100)}px system-ui`;ctx.fillText(key,p.x+r+3,p.y-r-3);}
   for(const list of Object.values(currentTraces))for(const p of list){ctx.beginPath();ctx.arc(p.x,p.y,Math.max(2,img.naturalWidth/900),0,Math.PI*2);ctx.fillStyle="#F4C95D";ctx.fill();}
   const calibrationLine=calibration[view]?.points??calibrationPoints;
   if(calibrationLine.length===1){ctx.beginPath();ctx.arc(calibrationLine[0].x,calibrationLine[0].y,Math.max(4,img.naturalWidth/500),0,Math.PI*2);ctx.fillStyle="#E07A5F";ctx.fill();}
   if(calibrationLine.length===2){ctx.beginPath();ctx.moveTo(calibrationLine[0].x,calibrationLine[0].y);ctx.lineTo(calibrationLine[1].x,calibrationLine[1].y);ctx.strokeStyle="#E07A5F";ctx.lineWidth=Math.max(2,img.naturalWidth/800);ctx.stroke();}
  };
  img.src=image.url;
 },[image,view,method,points,traces,calibration,calibrationPoints]);
 function changeMethod(next:Method){if(next==="intermaxillary"){setMethod(next);setPlacing(false);setTraceMode("");setCalibrationMode(false);return;}const nextView:ViewKey=next==="moyers"||next==="tanaka"?"incisors":next==="little"?"lower":"upper";setMethod(next);setTraceMode("");setPlacing(false);setCalibrationMode(false);setCalibrationPoints([]);setView(nextView);setSelected(pointOptions(next,nextView)[0]?.[0]??"");setZoom(.7);}
 function changeView(next:ViewKey){setView(next);setPlacing(false);setTraceMode("");setCalibrationMode(false);setCalibrationPoints([]);setSelected(pointOptions(method,next)[0]?.[0]??"");}
 function loadImage(event:React.ChangeEvent<HTMLInputElement>){
  const file=event.target.files?.[0];if(!file)return;
  if(file.type&&!file.type.startsWith("image/")){setError("Selecciona un archivo de imagen válido.");return;}
  const url=URL.createObjectURL(file),img=new Image();objectUrls.current.add(url);
  img.onload=()=>{setImages(prev=>{const old=prev[view];if(old?.url){URL.revokeObjectURL(old.url);objectUrls.current.delete(old.url);}return {...prev,[view]:{url,name:file.name,width:img.naturalWidth,height:img.naturalHeight}};});setPoints(prev=>({...prev,[view]:{}}));setTraces(prev=>({...prev,[view]:{}}));setCalibration(prev=>{const next={...prev};delete next[view];return next;});setCalibrationMode(false);setCalibrationPoints([]);setError("");};
  img.onerror=()=>{URL.revokeObjectURL(url);setError("No fue posible abrir la imagen.");};img.src=url;event.target.value="";
 }
 function clickCanvas(event:React.MouseEvent<HTMLCanvasElement>){
  if(!image)return;const rect=event.currentTarget.getBoundingClientRect();
  const p={x:(event.clientX-rect.left)/rect.width*image.width,y:(event.clientY-rect.top)/rect.height*image.height};
  if(calibrationMode){
   const next=[...calibrationPoints,p];
   if(next.length===2){const px=distance(next[0],next[1]),mm=Number(knownDistanceMm);if(px<=0||!Number.isFinite(mm)||mm<=0){setError("Distancia patrón inválida.");setCalibrationPoints([]);return;}setCalibration(prev=>({...prev,[view]:{pxPerMm:pixelsPerMillimeter(px,mm)!,knownDistanceMm:mm,points:[next[0],next[1]]}}));setCalibrationPoints(next);setCalibrationMode(false);setError("");}
   else setCalibrationPoints(next);
   return;
  }
  if(traceMode){setTraces(prev=>({...prev,[view]:{...prev[view],[traceMode]:[...(prev[view][traceMode]??[]),p]}}));return;}
  if(placing&&selected){setPoints(prev=>({...prev,[view]:{...prev[view],[selected]:p}}));setPlacing(false);setError("");}
 }
 function beginTrace(key:string){if(!image){setError("Carga primero la imagen de esta vista.");return;}if(method==="carey"){setTraces(prev=>({...prev,[view]:{...prev[view],perimeter:[]}}));}else setTraces(prev=>({...prev,[view]:{...prev[view],[key]:[]}}));setTraceMode(method==="carey"?"perimeter":key);setPlacing(false);}
 function finishTrace(){if(traceMode){const n=traces[view][traceMode]?.length??0;if(n<(method==="carey"?4:2)){setError(method==="carey"?"Marca al menos cuatro puntos siguiendo la curva de la arcada.":"Marca al menos dos puntos para completar el recorrido.");return;}setTraceMode("");setError("");}}
 function deleteSelected(){setPoints(prev=>({...prev,[view]:Object.fromEntries(Object.entries(prev[view]).filter(([k])=>k!==selected))}));}
 function resetCurrent(){setPoints(prev=>({...prev,[view]:{}}));setTraces(prev=>({...prev,[view]:{}}));setCalibration(prev=>{const next={...prev};delete next[view];return next;});setCalibrationMode(false);setCalibrationPoints([]);setTraceMode("");setPlacing(false);}
 const little=useMemo(()=>{
  if(view!=="upper"&&view!=="lower")return null;
  const p=points[view],pairs=LITTLE_CONTACTS.map(c=>[p[c.a],p[c.b]] as [XY|undefined,XY|undefined]);
  const result=littleIrregularityIndex(pairs);
  const scale=calibration[view]?.pxPerMm;
  return {segments:result?.segments.map(v=>scale?pixelsToMillimeters(v,scale):null)??Array(5).fill(null),total:result&&scale?pixelsToMillimeters(result.total,scale):null};
 },[points,view,calibration]);
 const carey=useMemo(()=>{
  if(view!=="upper"&&view!=="lower")return null;
  const p=points[view],teeth=CAREY_TEETH[view],widths=teeth.map(t=>p[t+"_M"]&&p[t+"_D"]?distance(p[t+"_M"],p[t+"_D"]):null);
  const availablePx=pathLength(traces[view].perimeter??[]);
  if(widths.some(v=>v===null)||availablePx===null)return null;
  const scale=calibration[view]?.pxPerMm;if(!scale)return null;
  const available=pixelsToMillimeters(availablePx,scale);
  const widthsMm=widths.map(v=>pixelsToMillimeters(v??NaN,scale));
  if(available===null||widthsMm.some(v=>v===null))return null;
  const result=careySpaceAnalysis(widthsMm as number[],available);
  if(!result)return null;
  return {available:result.availableMm,required:result.requiredMm,diff:result.discrepancyMm,percent:result.requiredMm?Math.abs(result.discrepancyMm)/result.requiredMm*100:0};
 },[points,traces,view,calibration]);
 const mixed=useMemo(()=>{
  const incisorScale=calibration.incisors?.pxPerMm;
  if(!incisorScale)return null;
  const ip=points.incisors;
  const widthsPx=INCISORS.map(t=>ip[t+"_M"]&&ip[t+"_D"]?distance(ip[t+"_M"],ip[t+"_D"]):null);
  if(widthsPx.some(v=>v===null))return null;
  const widthsMm=(widthsPx as number[]).map(v=>pixelsToMillimeters(v,incisorScale));
  if(widthsMm.some(v=>v===null))return null;
  const incisorSumMm=(widthsMm as number[]).reduce((sum,v)=>sum+v,0);
  const rows=[];
  for(const a of ["upper","lower"] as const){
   const scale=calibration[a]?.pxPerMm;
   for(const side of ["Derecho","Izquierdo"]){
    const start=points[a][side==="Derecho"?"lat_R":"lat_L"],end=points[a][side==="Derecho"?"mol_R":"mol_L"];
    const path=traces[a][side]??[];
    const px=start&&end&&path.length>=2?pathLength([start,...path,end]):null;
    const availableMm=px!==null&&scale?pixelsToMillimeters(px,scale):null;
    let requiredMm:number|null=null;
    const arch=a==="upper"?"superior":"inferior";
    if(method==="moyers"&&sex!=="Seleccionar")requiredMm=moyers75Prediction(incisorSumMm,sex,arch);
    else if(method==="tanaka")requiredMm=tanakaJohnstonPrediction(incisorSumMm,arch);
    const available:[number,number]|null=availableMm===null?null:[availableMm,availableMm];
    const required:[number,number]|null=requiredMm===null?null:[requiredMm,requiredMm];
    rows.push({arch:a==="upper"?"Superior":"Inferior",side,available,required,result:classifyRange(available,required)});
   }
  }
  return {incisorSumMm,rows};
 },[points,traces,method,sex,calibration]);
 const activePoints=points[view];
 const canExport=Object.values(images).some(Boolean);
 function exportJson(){
  const payload={application:"AVIS",analysis:method,images:Object.fromEntries(Object.entries(images).map(([k,v])=>[k,v?{name:v.name,width:v.width,height:v.height}:null])),points,traces,sex,calibration,results:{little,carey,mixed},observations,conclusion,generatedAt:new Date().toISOString(),limitations:"Las medidas en mm dependen de una calibración física válida e independiente por imagen. Las predicciones de Moyers y Tanaka-Johnston son estimaciones estadísticas y requieren validación profesional."};
  const blob=new Blob([JSON.stringify(payload,null,2)],{type:"application/json"});const url=URL.createObjectURL(blob);const a=document.createElement("a");a.href=url;a.download="AVIS_Analisis_Modelos.json";a.click();URL.revokeObjectURL(url);
 }
 async function exportPdf(){
  const canvas=canvasRef.current;if(!canvas||!image){setError("Carga una imagen antes de generar el PDF.");return;}
  const rows=method==="little"?[{label:"Índice de Little",value:little?.total?.toFixed(2)??"Pendiente",reference:"Suma de cinco desplazamientos · mm calibrados"}]:method==="carey"?[{label:"Perímetro disponible",value:carey?.available.toFixed(2)??"Pendiente",reference:"mm calibrados"},{label:"Material dentario",value:carey?.required.toFixed(2)??"Pendiente",reference:"mm calibrados"},{label:"Discrepancia",value:carey?.diff.toFixed(2)??"Pendiente",reference:"mm calibrados"}]:(mixed?.rows??[]).flatMap(r=>[
   {label:r.arch+" · "+r.side+" · espacio disponible",value:r.available?.[0].toFixed(2)??"Pendiente",reference:"mm calibrados"},
   {label:r.arch+" · "+r.side+" · espacio requerido",value:r.required?.[0].toFixed(2)??"Pendiente",reference:method==="moyers"?"Moyers 75 %":"Tanaka-Johnston"},
   {label:r.arch+" · "+r.side+" · discrepancia",value:r.available&&r.required?(r.available[0]-r.required[0]).toFixed(2):"Pendiente",reference:"mm; positivo = espacio, negativo = apiñamiento"}
  ]);
  const activePalette=getAvisPalette(paletteId);
  const pdf=buildPhotoReportPdf({title:"Análisis de modelos dentales · "+(method==="carey"&&view==="upper"?"Perímetro de arcada superior":method),mode:"models",fileName:image.name,status:"En proceso",photoDataUrl:canvas.toDataURL("image/jpeg",.92),photoWidth:image.width,photoHeight:image.height,horizontalGuides:false,points:activePoints,results:rows,conclusions:["Resultado de apoyo académico; verificar las referencias y la calidad del modelo.",observations,conclusion].filter(Boolean),visualAssessment:{},observations,professionalConclusion:"Las mediciones se convierten a milímetros mediante la calibración de esta imagen. Confirmar que el patrón de escala esté coplanar y que los puntos anatómicos sean correctos antes de la interpretación clínica.",generatedAt:new Date(),palette:activePalette.colors,paletteName:activePalette.name,logoDataUrl:await loadAvisLogoDataUrl(),birdIconDataUrl:await loadAvisBirdIconDataUrl(activePalette.birdImage),birdWatermarkDataUrl:await loadAvisBirdWatermarkDataUrl(activePalette.birdImage),reportLabel:"Reporte de modelos dentales"});
  const blob=new Blob([new Uint8Array(pdf).buffer as ArrayBuffer],{type:"application/pdf"});const url=URL.createObjectURL(blob);const a=document.createElement("a");a.href=url;a.download="AVIS_Analisis_Modelos.pdf";a.click();window.setTimeout(()=>URL.revokeObjectURL(url),1500);
 }
 if(method==="intermaxillary")return <IntermaxillaryRelations onBack={()=>setMethod("little")} paletteId={paletteId}/>;
 const title=method==="little"?(view==="lower"?"Índice de irregularidad de Little":"Irregularidad anterior · adaptación maxilar"):method==="moyers"?"Dentición mixta · Moyers 75 %":method==="tanaka"?"Dentición mixta · Tanaka-Johnston":view==="upper"?"Perímetro de arcada superior":"Análisis de espacio · Carey";
 return <section className="analysis-page">
  <div className="analysis-heading"><div><button className="text-button" onClick={onBack}>← Volver al inicio</button><p className="eyebrow">AVIS · MODELOS DENTALES</p><h1>{title}</h1><p>Carga los modelos oclusales superior e inferior y registra los puntos y recorridos manualmente.</p></div><span className="module-count">{Object.values(images).filter(Boolean).length} / 3 vistas cargadas</span></div>
  <div className="mode-row"><label htmlFor="model-method">Análisis</label><select id="model-method" value={method} onChange={e=>changeMethod(e.target.value as Method)}><option value="little">Little · irregularidad anterior</option><option value="moyers">Moyers · percentil 75 %</option><option value="tanaka">Tanaka-Johnston</option><option value="carey">Carey · perímetro de arcada</option><option value="intermaxillary">Relaciones intermaxilares · sagital, vertical y transversal</option></select></div>
  <div className="guide"><strong>{method==="little"?"Diez puntos anatómicos en cinco pares de contacto":method==="carey"?"Diez anchos mesiodistales y perímetro de arcada": "Incisivos inferiores, espacio disponible y predicción por hemiarcada"}</strong><p>{method==="little"?"El índice original se aplica a la arcada inferior y suma cinco distancias entre pares anatómicos (43–42 a 32–33). La arcada superior se etiqueta como adaptación no equivalente a una norma validada. Se expresa en mm solo después de calibrar esta imagen.":method==="carey"?"Carey compara el perímetro mandibular disponible entre los primeros molares con la suma de los anchos mesiodistales de los diez dientes de 5 a 5. En maxilar se presenta como análisis de perímetro de arcada. Requiere calibración.":"Moyers y Tanaka-Johnston usan la suma real en mm de los cuatro incisivos inferiores. Calibra por separado la imagen de incisivos y cada arcada. Traza el espacio posterior considerando la posición prevista de los incisivos tras alineación; el registro de una arcada apiñada sin ajuste puede alterar el espacio disponible."}</p></div>
  <div className="mode-row"><label>Vista</label><div className="point-actions">
   {(method==="moyers"||method==="tanaka"?[["incisors","Incisivos inferiores"],["upper","Modelo superior"],["lower","Modelo inferior"]]:[["upper","Modelo superior"],["lower","Modelo inferior"]]).map(([k,label])=><button key={k} className={view===k?"primary":"secondary"} onClick={()=>changeView(k as ViewKey)}>{label}</button>)}
  </div></div>
  <div className="workspace">
   <section className="panel photo-panel"><div className="panel-heading"><div><h2>{view==="incisors"?"Incisivos inferiores":view==="upper"?"Modelo superior":"Modelo inferior"}</h2><p>Sube una imagen nítida, sin perspectiva excesiva y con la arcada completa visible.</p></div></div>
    <label className="upload-control"><span>＋ Cargar imagen de esta vista</span><input type="file" accept="image/*" onChange={loadImage}/></label>
    {image&&<div className="file-meta"><strong>{image.name}</strong><span>{image.width} × {image.height} px</span></div>}
    {error&&<p className="error-text" role="alert">{error}</p>}
    {image?<><div className="zoom-row"><label>Zoom</label><input type="range" min=".2" max="3" step=".05" value={zoom} onChange={e=>setZoom(Number(e.target.value))}/><span>{Math.round(zoom*100)} %</span><button className="small-button" onClick={()=>setZoom(.7)}>Restablecer</button></div><div className="image-viewport"><canvas ref={canvasRef} onClick={clickCanvas} style={{width:image.width*zoom,height:image.height*zoom,cursor:placing||traceMode||calibrationMode?"crosshair":"default"}}/></div></>:<div className="image-empty"><span>▧</span><strong>Vista no cargada</strong><p>Selecciona la imagen o fotografía del modelo que corresponde a esta vista.</p></div>}
    {calibrationMode&&<p className="placement-hint">Marca dos puntos separados por {knownDistanceMm} mm.</p>}{traceMode&&<p className="placement-hint">Trazando {traceMode==="perimeter"?"perímetro de arcada":traceMode==="Derecho"?"espacio derecho":"espacio izquierdo"}. Haz clic siguiendo la curva y finaliza el recorrido.</p>}
    <div className="point-controls"><label htmlFor="model-point">Punto anatómico / dental</label><select id="model-point" value={selected} onChange={e=>setSelected(e.target.value)}>{options.map(([k,label])=><option key={k} value={k}>{k} · {label}</option>)}</select>
     <div className="point-actions"><button className="primary" disabled={!image||!selected||!!traceMode||calibrationMode} onClick={()=>setPlacing(true)}>Colocar / corregir punto</button><button className="secondary" disabled={!activePoints[selected]} onClick={deleteSelected}>Eliminar punto</button><button className="secondary" onClick={resetCurrent}>Limpiar vista</button></div>
     <div className="point-controls"><h3>Calibración física de esta imagen</h3><label className="visual-field"><span>Distancia patrón conocida (mm)</span><input className="calibration-input" type="number" min="0.01" step="0.01" value={knownDistanceMm} onChange={e=>{setKnownDistanceMm(e.target.value);setCalibration(prev=>{const next={...prev};delete next[view];return next;});setCalibrationPoints([]);}}/></label><div className="point-actions"><button className="secondary" disabled={!image||!!traceMode} onClick={()=>{if(calibrationMode){setCalibrationMode(false);setCalibrationPoints([]);}else{setCalibrationPoints([]);setCalibration(prev=>{const next={...prev};delete next[view];return next;});setCalibrationMode(true);setPlacing(false);setError("");}}}>{calibrationMode?"Cancelar calibración":"Marcar escala con dos puntos"}</button><span className="point-progress">{calibration[view]?calibration[view]!.pxPerMm.toFixed(3)+" px/mm":"Sin calibrar"}</span></div><p className="clinical-note">Usa una regla o patrón milimetrado coplanar con el modelo. Calibra por separado cada fotografía. Si sustituyes la imagen, debes calibrarla de nuevo.</p></div>

     <div className="point-list">{options.map(([k])=><button key={k} className={activePoints[k]?"point-chip point-done":"point-chip"} onClick={()=>setSelected(k)}>{activePoints[k]?"✓ ":""}{k}</button>)}</div>
    </div>
    {(method==="carey"||method==="moyers"||method==="tanaka")&&view!=="incisors"&&<div className="point-controls"><h3>Recorrido curvo del espacio</h3>{method==="carey"?<button className="secondary" disabled={calibrationMode} onClick={()=>traceMode?finishTrace():beginTrace("perimeter")}>{traceMode?"Finalizar perímetro":"Trazar perímetro completo"}</button>:<div className="point-actions">{["Derecho","Izquierdo"].map(side=><button key={side} className="secondary" disabled={calibrationMode} onClick={()=>traceMode===side?finishTrace():beginTrace(side)}>{traceMode===side?"Finalizar "+side:"Trazar "+side}</button>)}</div>}<p className="clinical-note">Marca varios puntos siguiendo la curvatura real del arco. No cierres el recorrido por fuera de los puntos anatómicos.</p></div>}
   </section>
   <aside className="panel results-panel"><div className="panel-heading"><div><h2>Resultados</h2><p>Los valores se actualizan con los puntos disponibles.</p></div></div>
    {(method==="moyers"||method==="tanaka")&&view==="incisors"&&<p className="unit-notice">Coloca mesial y distal de 42, 41, 31 y 32 y calibra esta imagen. La suma se calcula con los anchos medidos en mm, no con un promedio poblacional.</p>}
    {method==="moyers"&&<div className="form-field"><label htmlFor="model-sex">Sexo requerido por la tabla Moyers</label><select id="model-sex" value={sex} onChange={e=>setSex(e.target.value as typeof sex)}><option>Seleccionar</option><option>Femenino</option><option>Masculino</option></select></div>}

    {method==="little"&&<><div className="unit-notice">Cinco desplazamientos entre pares anatómicos. Unidad: mm; requiere calibración.</div><table><thead><tr><th>Segmento</th><th>Distancia</th></tr></thead><tbody>{LITTLE_CONTACTS.map((contact,i)=><tr key={contact.id}><td>{contact.id}</td><td className="result-value">{little?.segments[i]?.toFixed(2)??"—"}</td></tr>)}</tbody></table><p className="result-value">{view==="lower"?"Índice de Little":"Índice de irregularidad anterior (adaptación maxilar)"}: {little?.total?.toFixed(2)??"Pendiente"} mm</p></>}
    {method==="carey"&&<><div className="unit-notice">Se requieren 20 puntos mesial/distal, perímetro desde mesial del primer molar derecho hasta mesial del izquierdo siguiendo cúspides bucales y bordes incisales, y calibración. Unidad: mm.</div><table><tbody><tr><td>Espacio disponible</td><td className="result-value">{carey?.available.toFixed(2)??"—"} mm</td></tr><tr><td>Material dentario</td><td className="result-value">{carey?.required.toFixed(2)??"—"} mm</td></tr><tr><td>Discrepancia</td><td className="result-value">{carey?.diff.toFixed(2)??"—"} mm</td></tr></tbody></table><p>{carey?carey.diff>0?"Exceso de espacio relativo":carey.diff<0?"Déficit de espacio relativo":"Equilibrio geométrico relativo":"Faltan puntos o recorrido."}</p></>}
    {(method==="moyers"||method==="tanaka")&&<><div className="unit-notice">La predicción requiere calibración independiente de la vista de incisivos y de cada arcada.</div><p className="clinical-note">Σ incisivos inferiores: {mixed?.incisorSumMm.toFixed(2)??"Pendiente"} mm</p><table><thead><tr><th>Arcada / lado</th><th>Disponible</th><th>Requerido</th><th>Discrepancia</th><th>Resultado</th></tr></thead><tbody>{(mixed?.rows??["Superior · Derecho","Superior · Izquierdo","Inferior · Derecho","Inferior · Izquierdo"].map(label=>({arch:label.split(" · ")[0],side:label.split(" · ")[1],available:null,required:null,result:"Pendiente"}))).map((r,i)=><tr key={i}><td>{r.arch} · {r.side}</td><td>{r.available!==null?r.available[0].toFixed(2)+" mm":"—"}</td><td>{r.required!==null?r.required[0].toFixed(2)+" mm":"—"}</td><td>{r.available!==null&&r.required!==null?(r.available[0]-r.required[0]).toFixed(2)+" mm":"—"}</td><td>{r.result}</td></tr>)}</tbody></table><p className="clinical-note">Moyers estima por hemiarcada el ancho combinado de canino y premolares al percentil 75 %. Tanaka-Johnston calcula 11 + (Σ incisivos inferiores/2) para maxilar y 10.5 + (Σ incisivos inferiores/2) para mandibular.</p></>}
    <div className="form-field"><label htmlFor="model-observations">Observaciones</label><textarea id="model-observations" rows={3} value={observations} onChange={e=>setObservations(e.target.value)}/></div><div className="form-field"><label htmlFor="model-conclusion">Conclusión profesional / docente</label><textarea id="model-conclusion" rows={3} value={conclusion} onChange={e=>setConclusion(e.target.value)}/></div>
    <button className="primary download-button" disabled={!image} onClick={exportPdf}>Descargar informe PDF de esta vista</button><button className="secondary download-button" disabled={!canExport} onClick={exportJson}>Exportar análisis completo (JSON)</button><p className="clinical-note">Los cálculos lineales requieren calibración física válida en cada vista. Las predicciones estadísticas no sustituyen la medición clínica ni la valoración profesional.</p>
   </aside>
  </div>
 </section>;
}
