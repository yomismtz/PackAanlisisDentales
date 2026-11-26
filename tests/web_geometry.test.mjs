import test from "node:test";
import assert from "node:assert/strict";
import { angleBetweenLinesDegrees, steinerIncisorAngleDegrees } from "../clients/web/src/cephalometryGeometry.js";

const p=(x,y)=>({x,y});
test("Go-Gn/SN angle returns degrees, not radians",()=>{
  const rad=Math.PI*32/180;
  assert.ok(Math.abs(angleBetweenLinesDegrees(p(0,0),p(100,0),p(0,0),p(100*Math.cos(rad),100*Math.sin(rad)))-32)<1e-9);
});
test("line angle handles 45 and 90 degrees",()=>{
  assert.ok(Math.abs(angleBetweenLinesDegrees(p(0,0),p(10,0),p(0,0),p(10,10))-45)<1e-9);
  assert.ok(Math.abs(angleBetweenLinesDegrees(p(0,0),p(10,0),p(0,0),p(0,10))-90)<1e-9);
});
test("line angle is independent of endpoint order",()=>{
  const a=angleBetweenLinesDegrees(p(0,0),p(10,0),p(0,0),p(10,10));
  const b=angleBetweenLinesDegrees(p(10,0),p(0,0),p(10,10),p(0,0));
  assert.equal(a,b);
});
test("Steiner upper incisor convention returns supplementary angle",()=>{
  const rad=Math.PI*76/180;
  assert.ok(Math.abs(steinerIncisorAngleDegrees(p(0,0),p(1,0),p(0,0),p(Math.cos(rad),Math.sin(rad)))-104)<1e-9);
});
test("degenerate axes do not produce a false angle",()=>{
  assert.equal(angleBetweenLinesDegrees(p(0,0),p(0,0),p(1,1),p(2,2)),null);
});
