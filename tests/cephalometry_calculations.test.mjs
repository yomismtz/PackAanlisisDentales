import test from "node:test";
import assert from "node:assert/strict";
import { calculateCephalometry } from "../clients/web/src/cephalometryCalculations.js";
const p=(x,y)=>({x,y});
const rad=(degrees)=>degrees*Math.PI/180;
test("SNA, SNB and ANB are calculated at Nasion and ANB is their signed difference",()=>{
 const S=p(0,0),N=p(1,0),A=p(1-Math.cos(rad(82)),Math.sin(rad(82))),B=p(1-Math.cos(rad(80)),-Math.sin(rad(80)));
 const {values}=calculateCephalometry({S,N,A,B});
 assert.ok(Math.abs(values.SNA-82)<1e-8);assert.ok(Math.abs(values.SNB-80)<1e-8);assert.ok(Math.abs(values.ANB-2)<1e-8);
});
test("SND uses Nasion as vertex",()=>{
 const S=p(0,0),N=p(1,0),D=p(1-Math.cos(rad(76)),Math.sin(rad(76)));
 assert.ok(Math.abs(calculateCephalometry({S,N,D}).values.SND-76)<1e-8);
});
test("Ar-Go-Me uses Gonion as vertex and preserves the obtuse gonial angle",()=>{
 const Ar=p(1,0),Go=p(0,0),Me=p(Math.cos(rad(125)),Math.sin(rad(125)));
 assert.ok(Math.abs(calculateCephalometry({Ar,Go,Me}).values.ArGoMe-125)<1e-8);
});
test("Go-Gn/SN returns the smaller plane angle in degrees",()=>{
 const S=p(0,0),N=p(10,0),Go=p(0,5),Gn=p(Math.cos(rad(32)),5+Math.sin(rad(32)));
 assert.ok(Math.abs(calculateCephalometry({S,N,Go,Gn}).values.GoGnSN-32)<1e-8);
});
test("AB-Go-Gn uses AB plane and mandibular Go-Gn plane",()=>{
 const A=p(0,0),B=p(10,0),Go=p(0,5),Gn=p(Math.cos(rad(74)),5+Math.sin(rad(74)));
 assert.ok(Math.abs(calculateCephalometry({A,B,Go,Gn}).values.ABGoGn-74)<1e-8);
});
test("U1-SN applies the supplementary convention",()=>{
 const S=p(0,0),N=p(10,0),U1_apex=p(0,0),U1_tip=p(Math.cos(rad(76)),Math.sin(rad(76)));
 assert.ok(Math.abs(calculateCephalometry({S,N,U1_apex,U1_tip}).values.U1SN-104)<1e-8);
});
test("L1-NB is the acute angle between NB and lower incisor axis",()=>{
 const N=p(0,0),B=p(10,0),L1_apex=p(0,0),L1_tip=p(Math.cos(rad(25)),Math.sin(rad(25)));
 assert.ok(Math.abs(calculateCephalometry({N,B,L1_apex,L1_tip}).values.L1NB-25)<1e-8);
});
test("IMPA is the angle between Go-Gn and lower incisor axis",()=>{
 const Go=p(0,0),Gn=p(10,0),L1_apex=p(0,0),L1_tip=p(0,10);
 assert.ok(Math.abs(calculateCephalometry({Go,Gn,L1_apex,L1_tip}).values.IMPA-90)<1e-8);
});
test("interincisal angle is measured on the radicular side using directed apex-to-tip axes",()=>{
 const U1_apex=p(0,0),U1_tip=p(10,0),L1_apex=p(0,0),L1_tip=p(Math.cos(rad(131)),Math.sin(rad(131)));
 assert.ok(Math.abs(calculateCephalometry({U1_apex,U1_tip,L1_apex,L1_tip}).values.Interincisal-131)<1e-8);
});
test("SL and SE are perpendicular projections onto SN and require calibration",()=>{
 const points={S:p(0,0),N:p(10,0),Pog:p(3,4),Co:p(5,6)};
 const {values,calculated}=calculateCephalometry(points,2);
 assert.deepEqual(calculated.L,p(3,0));assert.deepEqual(calculated.E,p(5,0));
 assert.equal(values.SL,1.5);assert.equal(values.SE,2.5);
 assert.equal(calculateCephalometry(points,null).values.SL,undefined);
});
test("degenerate and incomplete cephalometric geometry returns no fabricated value",()=>{
 const {values}=calculateCephalometry({S:p(0,0),N:p(0,0),A:p(1,1),Go:p(0,0),Gn:p(0,0)});
 assert.equal(values.SNA,undefined);assert.equal(values.GoGnSN,undefined);assert.equal(values.ANB,undefined);
});
