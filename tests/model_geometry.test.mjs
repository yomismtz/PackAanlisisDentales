import test from "node:test";
import assert from "node:assert/strict";
import {
  distanceBetweenPoints, polylineLength, littleIrregularityIndex, pixelsPerMillimeter, pixelsToMillimeters,
  careySpaceAnalysis, moyers75Prediction, tanakaJohnstonPrediction,
  classifySpaceRange
} from "../clients/web/src/modelGeometry.js";

const p=(x,y)=>({x,y});
test("distance and path length use Euclidean geometry",()=>{
  assert.equal(distanceBetweenPoints(p(0,0),p(3,4)),5);
  assert.equal(polylineLength([p(0,0),p(3,4),p(6,8)]),10);
  assert.equal(polylineLength([p(0,0)]),null);
});
test("Little index sums the five adjacent contact-point displacements",()=>{
  const pairs=[[p(0,0),p(3,4)],[p(0,0),p(0,2)],[p(1,1),p(4,5)],[p(2,2),p(2,6)],[p(0,0),p(0,5)]];
  const result=littleIrregularityIndex(pairs);
  assert.deepEqual(result.segments,[5,2,5,4,5]);
  assert.equal(result.total,21);
  assert.equal(littleIrregularityIndex(pairs.slice(0,4)),null);
  assert.equal(littleIrregularityIndex([[p(0,0),null],...pairs.slice(1)]),null);
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
  assert.equal(classifySpaceRange([20,20],[20,20]),"Equilibrio");
});

test("pixel calibration converts measurements to millimeters and rejects invalid scales",()=>{
  assert.equal(pixelsToMillimeters(25,5),5);
  assert.equal(pixelsToMillimeters(25,0),null);
  assert.equal(pixelsToMillimeters(-1,5),null);
});

test("Moyers 75th percentile uses sex- and arch-specific published values",()=>{
  assert.equal(moyers75Prediction(22,"Femenino","superior"),21.0);
  assert.equal(moyers75Prediction(22,"Femenino","inferior"),20.8);
  assert.equal(moyers75Prediction(22,"Masculino","superior"),21.5);
  assert.equal(moyers75Prediction(22,"Masculino","inferior"),21.4);
  assert.equal(moyers75Prediction(21.25,"Femenino","superior"),20.85);
  assert.equal(moyers75Prediction(23,"Masculino","inferior"),21.9);
  assert.equal(moyers75Prediction(19,"Femenino","superior"),null);
});

test("calibration factor rejects zero and invalid known distances",()=>{
  assert.equal(pixelsPerMillimeter(50,10),5);
  assert.equal(pixelsPerMillimeter(0,10),null);
  assert.equal(pixelsPerMillimeter(50,0),null);
});

test("Carey discrepancy equals arch perimeter minus ten-tooth material",()=>{
  const result=careySpaceAnalysis([6,6,7,6,5.5,5.5,6,7,6,6],61);
  assert.equal(result.requiredMm,61);
  assert.equal(result.availableMm,61);
  assert.equal(result.discrepancyMm,0);
  assert.equal(careySpaceAnalysis([6,6,7,6,5.5,5.5,6,7,6,6],64).discrepancyMm,3);
  assert.equal(careySpaceAnalysis([6,6,7,6,5.5,5.5,6,7,6,6],59).discrepancyMm,-2);
  assert.equal(careySpaceAnalysis([6,6],61),null);
  assert.equal(careySpaceAnalysis(Array(10).fill(6),0),null);
});
