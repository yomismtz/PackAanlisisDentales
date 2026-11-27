import test from "node:test";
import assert from "node:assert/strict";
import { acuteAngleBetweenLines, calculatePowellAngles, calculateVerticalFacialThirds, horizontalDistancePx, lineInclinationDegrees, signedPerpendicularDistance } from "../clients/web/src/photoGeometry.js";
const p=(x,y)=>({x,y}),rad=d=>d*Math.PI/180;
test("Powell nasofrontal uses G-N and N-R with vertex N",()=>{
 const G=p(0,0),N=p(1,0),R=p(1+Math.cos(rad(60)),Math.sin(rad(60)));
 assert.ok(Math.abs(calculatePowellAngles({G,N,R}).nasofrontal-120)<1e-8);
});
test("Powell nasofacial is the angle between facial plane G-Pg and nasal dorsum N-Prn",()=>{
 const G=p(0,0),Pg=p(10,0),N=p(0,2),Prn=p(10*Math.cos(rad(35)),2+10*Math.sin(rad(35)));
 assert.ok(Math.abs(calculatePowellAngles({G,Pg,N,Prn}).nasofacial-35)<1e-8);
});
test("Powell nasomental uses N-Prn and Prn-Pg with vertex Prn",()=>{
 const N=p(1,0),Prn=p(0,0),Pg=p(Math.cos(rad(126)),Math.sin(rad(126)));
 assert.ok(Math.abs(calculatePowellAngles({N,Prn,Pg}).nasomental-126)<1e-8);
});
test("Powell mentocervical is the angle between G-Pg and Me-C",()=>{
 const G=p(0,0),Pg=p(10,0),Me=p(0,5),C=p(10*Math.cos(rad(85)),5+10*Math.sin(rad(85)));
 assert.ok(Math.abs(calculatePowellAngles({G,Pg,Me,C}).mentocervical-85)<1e-8);
});
test("Powell rejects missing or degenerate landmarks",()=>{
 assert.equal(calculatePowellAngles({G:p(0,0),N:p(0,0),R:p(1,0)}).nasofrontal,null);
 assert.equal(calculatePowellAngles({G:p(0,0),Pg:p(0,0),N:p(1,0),Prn:p(2,0)}).nasofacial,null);
 assert.equal(calculatePowellAngles({}).mentocervical,null);
});

test("vertical facial thirds use Tr-G, G-Sn and Sn-Me",()=>{
 const result=calculateVerticalFacialThirds({Tr:p(0,0),G:p(0,10),Sn:p(0,30),Me:p(0,60)});
 assert.deepEqual(result.lengths,[10,20,30]);
 assert.ok(Math.abs(result.percentages[0]-16.6666666667)<1e-8);
 assert.ok(Math.abs(result.percentages[1]-33.3333333333)<1e-8);
 assert.equal(result.percentages[2],50);
});
test("vertical thirds return null when a required landmark is absent or total height is zero",()=>{
 assert.equal(calculateVerticalFacialThirds({Tr:p(0,0),Sn:p(0,10),Me:p(0,20)}),null);
 assert.equal(calculateVerticalFacialThirds({Tr:p(0,0),G:p(0,0),Sn:p(0,0),Me:p(0,0)}),null);
});

test("frontal fifths use horizontal projection, not diagonal Euclidean distance",()=>{
 assert.equal(horizontalDistancePx(p(0,0),p(3,4)),3);
 assert.equal(horizontalDistancePx(p(3,4),p(0,0)),3);
});
test("signed midline offset is perpendicular to the reference axis",()=>{
 assert.equal(signedPerpendicularDistance(p(0,0),p(10,0),p(3,2)),2);
 assert.equal(signedPerpendicularDistance(p(0,0),p(0,10),p(2,5)),-2);
 assert.equal(signedPerpendicularDistance(p(0,0),p(0,0),p(2,5)),null);
});
test("line inclination and acute line angle ignore endpoint direction",()=>{
 assert.ok(Math.abs(lineInclinationDegrees(p(0,0),p(10,0)))<1e-9);
 assert.ok(Math.abs(Math.abs(lineInclinationDegrees(p(0,0),p(0,10)))-90)<1e-9);
 assert.ok(Math.abs(acuteAngleBetweenLines(p(0,0),p(10,0),p(0,0),p(10*Math.cos(rad(35)),10*Math.sin(rad(35))))-35)<1e-8);
 assert.ok(Math.abs(acuteAngleBetweenLines(p(10,0),p(0,0),p(10*Math.cos(rad(35)),10*Math.sin(rad(35))),p(0,0))-35)<1e-8);
});
