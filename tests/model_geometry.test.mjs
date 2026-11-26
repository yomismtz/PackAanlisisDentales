import test from "node:test";
import assert from "node:assert/strict";
import {
  distanceBetweenPoints, polylineLength, littleIrregularityIndex,
  estimateFourIncisorSumRange, scaleSpaceRange, tanakaJohnstonPrediction,
  classifySpaceRange
} from "../clients/web/src/modelGeometry.js";

const p=(x,y)=>({x,y});
test("distance and path length use Euclidean geometry",()=>{
  assert.equal(distanceBetweenPoints(p(0,0),p(3,4)),5);
  assert.equal(polylineLength([p(0,0),p(3,4),p(6,8)]),10);
  assert.equal(polylineLength([p(0,0)]),null);
});
test("Little index sums the five adjacent contact-point displacements",()=>{
  const result=littleIrregularityIndex([p(0,0),p(3,0),p(3,4),p(6,4),p(6,8),p(9,8)]);
  assert.deepEqual(result.segments,[3,4,3,4,3]);
  assert.equal(result.total,17);
  assert.equal(littleIrregularityIndex([p(0,0)]),null);
});
test("four-incisor width interval uses mean of bilateral lower lateral incisors as scale reference",()=>{
  const result=estimateFourIncisorSumRange([60,50,50,60]);
  assert.ok(Math.abs(result[0]-20.5333333333)<1e-8);
  assert.ok(Math.abs(result[1]-24.2)<1e-8);
  assert.equal(estimateFourIncisorSumRange([60,50,null,60]),null);
});
test("reference-tooth scaling returns a bounded available-space interval",()=>{
  assert.deepEqual(scaleSpaceRange(100,20,6.1,.5),[28,33]);
  assert.equal(scaleSpaceRange(100,0,6.1,.5),null);
});
test("Tanaka-Johnston predicts one quadrant from four-incisor sum",()=>{
  assert.equal(tanakaJohnstonPrediction(22,"superior"),22);
  assert.equal(tanakaJohnstonPrediction(22,"inferior"),21.5);
  assert.equal(tanakaJohnstonPrediction(22,"other"),null);
});
test("interval classification requires non-overlapping ranges for a conclusion",()=>{
  assert.equal(classifySpaceRange([24,26],[20,23]),"Hay espacio");
  assert.equal(classifySpaceRange([18,19],[20,22]),"No hay espacio");
  assert.equal(classifySpaceRange([19,21],[20,22]),"No concluyente");
});
