import { angleBetweenLinesDegrees, steinerIncisorAngleDegrees } from "./cephalometryGeometry.js";

function angleAt(a, vertex, b) {
  const ax=a.x-vertex.x, ay=a.y-vertex.y, bx=b.x-vertex.x, by=b.y-vertex.y;
  const denominator=Math.hypot(ax,ay)*Math.hypot(bx,by);
  if(!denominator)return null;
  return Math.acos(Math.max(-1,Math.min(1,(ax*bx+ay*by)/denominator)))*180/Math.PI;
}
function angleBetweenAxes(apex1,tip1,apex2,tip2) {
  const ax=tip1.x-apex1.x, ay=tip1.y-apex1.y, bx=tip2.x-apex2.x, by=tip2.y-apex2.y;
  const denominator=Math.hypot(ax,ay)*Math.hypot(bx,by);
  if(!denominator)return null;
  return Math.acos(Math.max(-1,Math.min(1,(ax*bx+ay*by)/denominator)))*180/Math.PI;
}
function project(point,a,b) {
  const dx=b.x-a.x,dy=b.y-a.y,lengthSquared=dx*dx+dy*dy;
  if(!lengthSquared)return null;
  const t=((point.x-a.x)*dx+(point.y-a.y)*dy)/lengthSquared;
  return {x:a.x+t*dx,y:a.y+t*dy};
}
const distance=(a,b)=>Math.hypot(b.x-a.x,b.y-a.y);

export function calculateCephalometry(points,pxPerMm=null) {
  const values={};
  const put=(key,value)=>{if(value!==null&&Number.isFinite(value))values[key]=value;};
  const p=(key)=>points[key];
  if(p("S")&&p("N")&&p("A"))put("SNA",angleAt(p("S"),p("N"),p("A")));
  if(p("S")&&p("N")&&p("B"))put("SNB",angleAt(p("S"),p("N"),p("B")));
  if(values.SNA!==undefined&&values.SNB!==undefined)put("ANB",values.SNA-values.SNB);
  if(p("S")&&p("N")&&p("D"))put("SND",angleAt(p("S"),p("N"),p("D")));
  if(p("Ar")&&p("Go")&&p("Me"))put("ArGoMe",angleAt(p("Ar"),p("Go"),p("Me")));
  if(p("S")&&p("N")&&p("Go")&&p("Gn"))put("GoGnSN",angleBetweenLinesDegrees(p("S"),p("N"),p("Go"),p("Gn")));
  if(p("A")&&p("B")&&p("Go")&&p("Gn"))put("ABGoGn",angleBetweenLinesDegrees(p("A"),p("B"),p("Go"),p("Gn")));
  if(p("S")&&p("N")&&p("U1_apex")&&p("U1_tip"))put("U1SN",steinerIncisorAngleDegrees(p("S"),p("N"),p("U1_apex"),p("U1_tip")));
  if(p("N")&&p("B")&&p("L1_apex")&&p("L1_tip"))put("L1NB",angleBetweenLinesDegrees(p("N"),p("B"),p("L1_apex"),p("L1_tip")));
  if(p("Go")&&p("Gn")&&p("L1_apex")&&p("L1_tip"))put("IMPA",angleBetweenLinesDegrees(p("Go"),p("Gn"),p("L1_apex"),p("L1_tip")));
  if(p("U1_apex")&&p("U1_tip")&&p("L1_apex")&&p("L1_tip"))put("Interincisal",angleBetweenAxes(p("U1_apex"),p("U1_tip"),p("L1_apex"),p("L1_tip")));
  const calculated={};
  if(p("S")&&p("N")&&p("Pog")){const l=project(p("Pog"),p("S"),p("N"));if(l){calculated.L=l;if(Number.isFinite(pxPerMm)&&pxPerMm>0)put("SL",distance(p("S"),l)/pxPerMm);}}
  if(p("S")&&p("N")&&p("Co")){const e=project(p("Co"),p("S"),p("N"));if(e){calculated.E=e;if(Number.isFinite(pxPerMm)&&pxPerMm>0)put("SE",distance(p("S"),e)/pxPerMm);}}
  return {values,calculated};
}
