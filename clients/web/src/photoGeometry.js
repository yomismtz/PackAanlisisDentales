function angleAt(points,a,vertex,b){
 const p=points[a],v=points[vertex],q=points[b];if(!p||!v||!q)return null;
 const ax=p.x-v.x,ay=p.y-v.y,bx=q.x-v.x,by=q.y-v.y,den=Math.hypot(ax,ay)*Math.hypot(bx,by);
 if(!den)return null;
 return Math.acos(Math.max(-1,Math.min(1,(ax*bx+ay*by)/den)))*180/Math.PI;
}
function lineInclination(a,b){
 const dx=b.x-a.x,dy=b.y-a.y;if(!Math.hypot(dx,dy))return null;
 const angle=Math.atan2(dy,dx)*180/Math.PI;
 return (((angle+90)%180)+180)%180-90;
}
function angleBetweenLines(points,a,b,c,d){
 const p1=points[a],p2=points[b],p3=points[c],p4=points[d];
 if(!p1||!p2||!p3||!p4)return null;
 const first=lineInclination(p1,p2),second=lineInclination(p3,p4);
 if(first===null||second===null)return null;
 const difference=Math.abs(first-second);
 return Math.min(difference,180-difference);
}
export function calculatePowellAngles(points){
 return {
  nasofrontal:angleAt(points,"G","N","R"),
  nasofacial:angleBetweenLines(points,"G","Pg","N","Prn"),
  nasomental:angleAt(points,"N","Prn","Pg"),
  mentocervical:angleBetweenLines(points,"G","Pg","Me","C")
 };
}

export function calculateVerticalFacialThirds(points) {
  const tr=points.Tr,g=points.G,sn=points.Sn,me=points.Me;
  if(!tr||!g||!sn||!me)return null;
  const lengths=[Math.abs(g.y-tr.y),Math.abs(sn.y-g.y),Math.abs(me.y-sn.y)];
  const total=lengths.reduce((sum,value)=>sum+value,0);
  if(!(total>0))return null;
  return {lengths,percentages:lengths.map(value=>value/total*100)};
}
