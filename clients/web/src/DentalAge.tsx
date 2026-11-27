import React, { useMemo, useState } from "react";

type DentalMethod = "nolla" | "demirjian";
type Study = "select" | "dental" | "cervical" | "carpal";
type Sex = "Femenino" | "Masculino";
const TEETH = ["37","36","35","34","33","32","31"];
const NOLLA = ["0 · Ausencia de cripta","1 · Presencia de cripta","2 · Calcificación inicial","3 · Un tercio de corona","4 · Dos tercios de corona","5 · Corona casi completa","6 · Corona completa","7 · Un tercio de raíz","8 · Dos tercios de raíz","9 · Raíz casi completa, ápice abierto","10 · Ápice cerrado"];
const DEMIRJIAN = ["A · Calcificación inicial en cúspides","B · Unión de puntos calcificados","C · Formación de esmalte y dentina","D · Corona completa hasta unión amelocementaria","E · Longitud radicular menor que corona","F · Longitud radicular igual o mayor que corona","G · Paredes del conducto paralelas, ápice abierto","H · Ápice cerrado"];
const FISHMAN = [
 ["SMI 1","Falange proximal del tercer dedo: epífisis tan ancha como la diáfisis"],
 ["SMI 2","Falange media del tercer dedo: epífisis tan ancha como la diáfisis"],
 ["SMI 3","Falange media del quinto dedo: epífisis tan ancha como la diáfisis"],
 ["SMI 4","Aparición/ osificación del sesamoideo del aductor del pulgar"],
 ["SMI 5","Falange distal del tercer dedo: capuchón epifisario (capping)"],
 ["SMI 6","Falange media del tercer dedo: capuchón epifisario (capping)"],
 ["SMI 7","Falange media del quinto dedo: capuchón epifisario (capping)"],
 ["SMI 8","Falange distal del tercer dedo: fusión epífisis-diáfisis"],
 ["SMI 9","Falange proximal del tercer dedo: fusión epífisis-diáfisis"],
 ["SMI 10","Falange media del tercer dedo: fusión epífisis-diáfisis"],
 ["SMI 11","Radio distal: fusión completa epífisis-diáfisis"],
] as const;
const selectStyle: React.CSSProperties = { width: "100%", minWidth: 0 };
const gridStyle: React.CSSProperties = { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 270px), 1fr))", gap: 16 };
export default function DentalAge({onBack}:{onBack:()=>void}){
 const [study,setStudy]=useState<Study>("select");
 const [method,setMethod]=useState<DentalMethod>("nolla");
 const [sex,setSex]=useState<Sex>("Femenino");
 const [stages,setStages]=useState<Record<string,string>>({});
 const [notes,setNotes]=useState("");
 const [dentalImage,setDentalImage]=useState("");
 const [carpalImage,setCarpalImage]=useState("");
 const [gpPlate,setGpPlate]=useState("");
 const [gpAge,setGpAge]=useState("");
 const [gpNotes,setGpNotes]=useState("");
 const [fishman,setFishman]=useState<Record<string,string>>({});
 const [carpalNotes,setCarpalNotes]=useState("");
 const [carpalSide,setCarpalSide]=useState("Izquierda");
 const [cervicalImage,setCervicalImage]=useState("");
 const [cervicalStage,setCervicalStage]=useState("");
 const [cervicalNotes,setCervicalNotes]=useState("");
 const selected=Object.values(stages).filter(v=>v!=="").length;
 const score=useMemo(()=>Object.values(stages).reduce((s,v)=>s+(v===""?0:Number(v)),0),[stages]);
 const labels=method==="nolla"?NOLLA:DEMIRJIAN;
 const highestFishman=useMemo(()=>{let highest=0;for(let i=1;i<=11;i++){if(fishman[String(i)]==="Presente")highest=i;}return highest;},[fishman]);
 function loadImage(file:File|null,setter:(value:string)=>void){if(!file)return;if(!file.type.startsWith("image/"))return;const reader=new FileReader();reader.onload=()=>setter(String(reader.result??""));reader.readAsDataURL(file);}
 function changeMethod(v:DentalMethod){setMethod(v);setStages({});}
 function exportReport(){
  const data={application:"AVIS",analysis:study==="dental"?"Edad dental":study==="carpal"?"Maduración esquelética carpal":"Maduración vertebral cervical",sex,study,
   ...(study==="dental"?{dental:{method,referenceTeeth:TEETH,stages:Object.fromEntries(TEETH.map(t=>[t,stages[t]??null])),totalNollaScore:method==="nolla"?score:null,evaluatedTeeth:selected,imageIncluded:Boolean(dentalImage),observations:notes,interpretation:method==="nolla"?"La suma de estadios no se convierte directamente a años. Requiere tabla normativa validada para sexo y población.":"Se requieren puntuaciones Demirjian específicas por sexo y tabla de conversión validada."}}:{}),
   ...(study==="carpal"?{carpal:{side:carpalSide,greulichPyle:{closestAtlasStandard:gpPlate||null,manuallyRecordedBoneAge:gpAge||null,observations:gpNotes},fishman:{indicators:FISHMAN.map(([id,description],i)=>({id,description,status:fishman[String(i+1)]||"No evaluado"})),highestObservedIndicator:highestFishman||null,interpretation:"El indicador SMI más alto registrado describe maduración esquelética; no equivale por sí mismo a una edad cronológica en años."},imageIncluded:Boolean(carpalImage),observations:carpalNotes}}:{}),
   ...(study==="cervical"?{cervical:{method:"CVM · Baccetti",stage:cervicalStage||null,imageIncluded:Boolean(cervicalImage),observations:cervicalNotes}}:{}),createdAt:new Date().toISOString()};
  const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:"application/json"}));const a=document.createElement("a");a.href=url;a.download="AVIS_Edad_y_Maduracion.json";a.click();window.setTimeout(()=>URL.revokeObjectURL(url),1500);
 }
 return <section className="analysis-page">
  {study==="select"?<>
   <div className="analysis-heading"><div><button className="text-button" onClick={onBack}>← Volver al inicio</button><p className="eyebrow">AVIS · DESARROLLO Y MADURACIÓN</p><h1>Edad y maduración</h1><p>Selecciona un solo estudio para comenzar. No es necesario realizar los demás.</p></div></div>
   <div className="workspace">
    <button type="button" className="panel" style={{textAlign:"left",cursor:"pointer",minHeight:170}} onClick={()=>setStudy("dental")}><h2>Edad dental</h2><p>Selecciona Nolla o Demirjian y registra el desarrollo de los siete dientes mandibulares izquierdos.</p><strong>Iniciar análisis dental →</strong></button>
    <button type="button" className="panel" style={{textAlign:"left",cursor:"pointer",minHeight:170}} onClick={()=>setStudy("cervical")}><h2>Maduración vertebral cervical</h2><p>Evalúa los estadios CVM (CS1–CS6) en la radiografía lateral.</p><strong>Iniciar análisis cervical →</strong></button>
    <button type="button" className="panel" style={{textAlign:"left",cursor:"pointer",minHeight:170}} onClick={()=>setStudy("carpal")}><h2>Maduración carpal</h2><p>Elige Greulich y Pyle o Fishman para la radiografía de mano y muñeca.</p><strong>Iniciar análisis carpal →</strong></button>
   </div>
  </>:<>
  <div className="analysis-heading"><div><button className="text-button" onClick={()=>setStudy("select")}>← Cambiar tipo de estudio</button><p className="eyebrow">AVIS · DESARROLLO Y MADURACIÓN</p><h1>{study==="dental"?"Edad dental":study==="carpal"?"Maduración esquelética carpal":"Maduración vertebral cervical"}</h1><p>Se registra únicamente el estudio seleccionado.</p></div>{study==="dental"?<span className="module-count">{selected}/7 dientes</span>:study==="carpal"?<span className="module-count">SMI {highestFishman||"—"}/11</span>:null}</div>
  <div className="guide"><strong>Importante</strong><p>Los estadios radiográficos describen maduración. No deben convertirse automáticamente en edad cronológica sin las tablas normativas, población de referencia y validación correspondientes. La asignación de estadios es responsabilidad del profesional.</p></div>
  <section className="panel">
   <div className="panel-heading"><div><h2>Edad dental</h2><p>Selecciona el método y registra los siete dientes mandibulares izquierdos.</p></div></div>
   <div style={gridStyle}>
    <div className="form-field"><label htmlFor="age-method">Método dental</label><select id="age-method" style={selectStyle} value={method} onChange={e=>changeMethod(e.target.value as DentalMethod)}><option value="nolla">Nolla · 0–10</option><option value="demirjian">Demirjian · A–H</option></select></div>
    <div className="form-field"><label htmlFor="age-sex">Sexo requerido por las referencias normativas</label><select id="age-sex" style={selectStyle} value={sex} onChange={e=>setSex(e.target.value as Sex)}><option>Femenino</option><option>Masculino</option></select></div>
   </div>
   <div className="form-field"><label htmlFor="dental-image">Radiografía panorámica o imagen diagnóstica</label><input id="dental-image" type="file" accept="image/*" onChange={e=>loadImage(e.target.files?.[0]??null,setDentalImage)}/></div>
   {dentalImage&&<img src={dentalImage} alt="Radiografía dental cargada" style={{maxWidth:"100%",maxHeight:280,objectFit:"contain",display:"block",margin:"12px auto"}}/>}
   <h3>Registro por pieza</h3>
   <div style={gridStyle}>{TEETH.map(t=><div className="form-field" key={t}><label htmlFor={"stage-"+t}>Diente {t}</label><select id={"stage-"+t} style={selectStyle} value={stages[t]??""} onChange={e=>setStages(p=>({...p,[t]:e.target.value}))}><option value="">Sin evaluar</option>{labels.map((s,i)=><option key={s} value={method==="nolla"?String(i):String(i+1)}>{s}</option>)}</select></div>)}</div>
   <div className="automatic-conclusions"><h3>{method==="nolla"?"Suma de estadios Nolla":"Registro Demirjian"}</h3><p className="result-value">{method==="nolla"?score.toFixed(1):selected+" de 7 dientes evaluados"}</p><p className="clinical-note">{method==="nolla"?"La suma no es una edad en años; requiere tabla normativa por sexo y población.":"Los estadios A–H requieren puntuaciones específicas por sexo y una tabla de conversión validada."}</p></div>
   <div className="form-field"><label htmlFor="age-notes">Observaciones dentales</label><textarea id="age-notes" rows={3} value={notes} onChange={e=>setNotes(e.target.value)}/></div>
  </section>
  <section className="panel" style={{marginTop:20}}>
   <div className="panel-heading"><div><h2>Maduración esquelética carpal</h2><p>Dos métodos complementarios para radiografía de mano y muñeca.</p></div></div>
   <div className="form-field"><label htmlFor="carpal-image">Cargar radiografía de mano y muñeca</label><input id="carpal-image" type="file" accept="image/*" onChange={e=>loadImage(e.target.files?.[0]??null,setCarpalImage)}/></div>
   {carpalImage&&<img src={carpalImage} alt="Radiografía carpal cargada" style={{maxWidth:"100%",maxHeight:360,objectFit:"contain",display:"block",margin:"12px auto"}}/>}
   <div style={gridStyle}>
    <div className="form-field"><label htmlFor="carpal-side">Lado radiografiado</label><select id="carpal-side" style={selectStyle} value={carpalSide} onChange={e=>setCarpalSide(e.target.value)}><option>Izquierda</option><option>Derecha</option></select></div>
    <div className="form-field"><label>Sexo de referencia</label><input value={sex} readOnly style={selectStyle}/></div>
   </div>
   <div className="panel-heading"><div><h3>Greulich y Pyle</h3><p>Comparación visual de la radiografía con la lámina correspondiente del atlas según sexo.</p></div></div>
   <div style={gridStyle}>
    <div className="form-field"><label htmlFor="gp-plate">Lámina/estándar del atlas más semejante</label><input id="gp-plate" value={gpPlate} onChange={e=>setGpPlate(e.target.value)} placeholder="Registrar lámina consultada"/></div>
    <div className="form-field"><label htmlFor="gp-age">Edad ósea indicada por el atlas</label><input id="gp-age" value={gpAge} onChange={e=>setGpAge(e.target.value)} placeholder="Transcribir resultado del atlas"/></div>
   </div>
   <div className="form-field"><label htmlFor="gp-notes">Observaciones de comparación</label><textarea id="gp-notes" rows={2} value={gpNotes} onChange={e=>setGpNotes(e.target.value)} placeholder="Describir concordancia y diferencias por regiones óseas"/></div>
   <p className="clinical-note">AVIS registra la comparación realizada por el profesional; no incluye ni reproduce las láminas protegidas del atlas ni selecciona automáticamente una edad.</p>
   <div className="divider-line"/>
   <div className="panel-heading"><div><h3>Fishman · 11 indicadores de maduración (SMI)</h3><p>Marca cada indicador como presente, ausente o no evaluable en la radiografía.</p></div><span className="module-count">SMI {highestFishman||"—"}/11</span></div>
   <div style={gridStyle}>{FISHMAN.map(([id,description],i)=><div className="form-field" key={id}><label htmlFor={"fishman-"+i}>{id} · {description}</label><select id={"fishman-"+i} style={selectStyle} value={fishman[String(i+1)]??""} onChange={e=>setFishman(p=>({...p,[String(i+1)]:e.target.value}))}><option value="">No evaluado</option><option value="Presente">Presente</option><option value="Ausente">Ausente</option><option value="No evaluable">No evaluable</option></select></div>)}</div>
   <p className="clinical-note">Los 11 indicadores corresponden a los eventos de ensanchamiento epifisario, aparición del sesamoideo, capping y fusión epífisis-diáfisis. El SMI más alto marcado como presente se muestra como referencia descriptiva; no se traduce automáticamente a edad cronológica ni a porcentaje de crecimiento restante.</p>
   <div className="form-field"><label htmlFor="carpal-notes">Observaciones de maduración carpal</label><textarea id="carpal-notes" rows={3} value={carpalNotes} onChange={e=>setCarpalNotes(e.target.value)}/></div>
  </section>
  <div style={{display:"flex",justifyContent:"flex-end",marginTop:18}}><button className="primary download-button" onClick={exportReport}>Exportar informe de edad y maduración (JSON)</button></div>
 </section>;
}
