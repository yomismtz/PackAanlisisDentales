import React, { useMemo, useState } from "react";

type Method = "nolla" | "demirjian";
const TEETH = ["37","36","35","34","33","32","31"];
const NOLLA = ["0 · Ausencia de cripta","1 · Presencia de cripta","2 · Calcificación inicial","3 · Un tercio de corona","4 · Dos tercios de corona","5 · Corona casi completa","6 · Corona completa","7 · Un tercio de raíz","8 · Dos tercios de raíz","9 · Raíz casi completa, ápice abierto","10 · Ápice cerrado"];
const DEMIRJIAN = ["A · Calcificación inicial en cúspides","B · Unión de puntos calcificados","C · Formación de esmalte y dentina","D · Corona completa hasta unión amelocementaria","E · Longitud radicular menor que corona","F · Longitud radicular igual o mayor que corona","G · Paredes del conducto paralelas, ápice abierto","H · Ápice cerrado"];
export default function DentalAge({onBack}:{onBack:()=>void}){
 const [method,setMethod]=useState<Method>("nolla");
 const [sex,setSex]=useState<"Femenino"|"Masculino">("Femenino");
 const [stages,setStages]=useState<Record<string,string>>({});
 const [notes,setNotes]=useState("");
 const [imageName,setImageName]=useState("");
 const selected=Object.values(stages).filter(v=>v!=="").length;
 const score=useMemo(()=>Object.values(stages).reduce((s,v)=>s+(v===""?0:Number(v)),0),[stages]);
 const labels=method==="nolla"?NOLLA:DEMIRJIAN;
 function changeMethod(v:Method){setMethod(v);setStages({});}
 function exportReport(){
  const data={application:"AVIS",analysis:"Estimación de maduración dental",method,sex,referenceTeeth:TEETH,stages:Object.fromEntries(TEETH.map(t=>[t,stages[t]??null])),totalScore:score,scoredTeeth:selected,imageName,observations:notes,interpretation:method==="nolla"?"Suma de estadios Nolla registrada. La conversión a edad dental requiere la tabla normativa validada para sexo y población; no se infiere una edad sin esa referencia.":"Estadios Demirjian registrados. La conversión a puntuación de madurez y edad dental requiere las tablas de puntuación por sexo y la curva de referencia correspondiente; no se infiere una edad sin ellas.",createdAt:new Date().toISOString()};
  const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:"application/json"}));const a=document.createElement("a");a.href=url;a.download="AVIS_Edad_Dental.json";a.click();URL.revokeObjectURL(url);
 }
 return <section className="analysis-page">
  <div className="analysis-heading"><div><button className="text-button" onClick={onBack}>← Volver al inicio</button><p className="eyebrow">AVIS · DESARROLLO DENTAL</p><h1>Análisis de edad dental</h1><p>Registro radiográfico de estadios de maduración dental mediante Nolla o Demirjian.</p></div><span className="module-count">{selected} / 7 dientes</span></div>
  <div className="mode-row"><label htmlFor="age-method">Método</label><select id="age-method" value={method} onChange={e=>changeMethod(e.target.value as Method)}><option value="nolla">Nolla · 0–10</option><option value="demirjian">Demirjian · A–H</option></select></div>
  <div className="guide"><strong>Protocolo de registro</strong><p>Evalúa los siete dientes permanentes mandibulares izquierdos (37 a 31) en la radiografía. Selecciona un estadio por diente. Usa una imagen diagnóstica adecuada y registra únicamente lo que pueda observarse.</p></div>
  <div className="workspace">
   <section className="panel photo-panel"><div className="panel-heading"><div><h2>Radiografía de evaluación</h2><p>La imagen sirve como referencia visual; la asignación del estadio es manual.</p></div></div>
    <label className="upload-control"><span>＋ Cargar radiografía</span><input type="file" accept="image/*" onChange={e=>setImageName(e.target.files?.[0]?.name??"")}/></label>
    {imageName&&<p className="file-meta"><strong>{imageName}</strong></p>}
    <div className="point-controls"><h3>Registro por pieza</h3>{TEETH.map(t=><div className="form-field" key={t}><label htmlFor={"stage-"+t}>Diente {t}</label><select id={"stage-"+t} value={stages[t]??""} onChange={e=>setStages(p=>({...p,[t]:e.target.value}))}><option value="">Sin evaluar</option>{labels.map((s,i)=><option key={s} value={method==="nolla"?String(i):String(i+1)}>{s}</option>)}</select></div>)}</div>
   </section>
   <aside className="panel results-panel"><div className="panel-heading"><div><h2>Resultados de registro</h2><p>Control de estadios asignados.</p></div></div>
    <div className="form-field"><label htmlFor="age-sex">Sexo requerido por las tablas normativas</label><select id="age-sex" value={sex} onChange={e=>setSex(e.target.value as typeof sex)}><option>Femenino</option><option>Masculino</option></select></div>
    <table><thead><tr><th>Diente</th><th>Estadio</th></tr></thead><tbody>{TEETH.map(t=><tr key={t}><td>{t}</td><td>{stages[t]?method==="nolla"?NOLLA[Number(stages[t])]:DEMIRJIAN[Number(stages[t])-1]:"Pendiente"}</td></tr>)}</tbody></table>
    <div className="automatic-conclusions"><h3>{method==="nolla"?"Suma de estadios Nolla":"Registro de estadios Demirjian"}</h3><p className="result-value">{method==="nolla"?score.toFixed(1):selected+" de 7 dientes evaluados"}</p><p className="clinical-note">{method==="nolla"?"La suma es un dato de maduración, no una edad en años. Para convertirla a edad dental debe aplicarse una tabla normativa por sexo y población, seleccionada y documentada.":"Los estadios A–H no se suman directamente como edad. Se requieren las puntuaciones Demirjian específicas por sexo y la curva de conversión validada."}</p></div>
    <div className="form-field"><label htmlFor="age-notes">Observaciones</label><textarea id="age-notes" rows={4} value={notes} onChange={e=>setNotes(e.target.value)} /></div>
    <button className="primary download-button" disabled={selected===0} onClick={exportReport}>Exportar registro de edad dental (JSON)</button>
   </aside>
  </div>
 </section>;
}
