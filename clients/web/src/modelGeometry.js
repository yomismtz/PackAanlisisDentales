export function distanceBetweenPoints(a, b) {
  if (!a || !b || ![a.x, a.y, b.x, b.y].every(Number.isFinite)) return null;
  return Math.hypot(b.x - a.x, b.y - a.y);
}

export function polylineLength(points) {
  if (!Array.isArray(points) || points.length < 2) return null;
  let total = 0;
  for (let i = 1; i < points.length; i += 1) {
    const segment = distanceBetweenPoints(points[i - 1], points[i]);
    if (segment === null) return null;
    total += segment;
  }
  return total;
}

export function littleIrregularityIndex(contactPairs) {
  if (!Array.isArray(contactPairs) || contactPairs.length !== 5) return null;
  const segments = contactPairs.map((pair) => {
    if (!Array.isArray(pair) || pair.length !== 2) return null;
    return distanceBetweenPoints(pair[0], pair[1]);
  });
  if (segments.some((v) => v === null)) return null;
  return { segments, total: segments.reduce((sum, v) => sum + v, 0) };
}

// 75th-percentile tables: 19.5–25.5 mm in 0.5 mm steps; separate sex and arch columns.\nconst MOYERS_SUMS = Array.from({ length: 13 }, (_, i) => 19.5 + i * 0.5);
const MOYERS_75 = {
  Masculino: {
    superior: [20.3,20.5,20.8,21.0,21.3,21.5,21.8,22.0,22.3,22.5,22.8,23.0,23.3],
    inferior: [20.3,20.5,20.8,21.0,21.3,21.5,21.8,22.0,22.3,22.5,22.8,23.0,23.3]
  },
  Femenino: {
    superior: [20.4,20.5,20.6,20.8,20.9,21.0,21.2,21.3,21.5,21.6,21.8,21.9,22.1],
    inferior: [19.6,19.8,20.1,20.3,20.6,20.8,21.1,21.3,21.6,21.9,22.1,22.4,22.7]
  }
};

export function moyers75Prediction(incisorSumMm, sex, arch) {
  if (!Number.isFinite(incisorSumMm) || incisorSumMm < 19.5 || incisorSumMm > 25.5) return null;
  if (!MOYERS_75[sex] || !MOYERS_75[sex][arch]) return null;
  const exact = MOYERS_SUMS.findIndex((v) => Math.abs(v - incisorSumMm) < 1e-8);
  if (exact >= 0) return MOYERS_75[sex][arch][exact];
  const lowerIndex = MOYERS_SUMS.findIndex((v, i) => i < MOYERS_SUMS.length - 1 && v < incisorSumMm && incisorSumMm < MOYERS_SUMS[i + 1]);
  if (lowerIndex < 0) return null;
  const t = (incisorSumMm - MOYERS_SUMS[lowerIndex]) / (MOYERS_SUMS[lowerIndex + 1] - MOYERS_SUMS[lowerIndex]);
  const values = MOYERS_75[sex][arch];
  return Math.round((values[lowerIndex] + t * (values[lowerIndex + 1] - values[lowerIndex])) * 100) / 100;
}

export function tanakaJohnstonPrediction(incisorSumMm, arch) {
  if (!Number.isFinite(incisorSumMm) || incisorSumMm <= 0) return null;
  if (arch === "superior") return 11 + incisorSumMm / 2;
  if (arch === "inferior") return 10.5 + incisorSumMm / 2;
  return null;
}

export function classifySpaceRange(available, required) {
  if (!available || !required || available.length !== 2 || required.length !== 2) return "No concluyente";
  if (![...available, ...required].every(Number.isFinite)) return "No concluyente";
  if (Math.abs(available[0] - available[1]) < 1e-9 && Math.abs(required[0] - required[1]) < 1e-9 && Math.abs(available[0] - required[0]) < 1e-9) return "Equilibrio";
  if (available[0] > required[1]) return "Hay espacio";
  if (available[1] < required[0]) return "No hay espacio";
  return "No concluyente";
}

export function pixelsToMillimeters(valuePx, pixelsPerMm) {
  if (!Number.isFinite(valuePx) || !Number.isFinite(pixelsPerMm) || valuePx < 0 || pixelsPerMm <= 0) return null;
  return valuePx / pixelsPerMm;
}

export function pixelsPerMillimeter(distancePx, knownDistanceMm) {
  if (!Number.isFinite(distancePx) || !Number.isFinite(knownDistanceMm) || distancePx <= 0 || knownDistanceMm <= 0) return null;
  return distancePx / knownDistanceMm;
}

export function careySpaceAnalysis(toothWidthsMm, archPerimeterMm) {
  if (!Array.isArray(toothWidthsMm) || toothWidthsMm.length !== 10 ||
      toothWidthsMm.some((value) => !Number.isFinite(value) || value <= 0) ||
      !Number.isFinite(archPerimeterMm) || archPerimeterMm <= 0) return null;
  const requiredMm = toothWidthsMm.reduce((sum, value) => sum + value, 0);
  const discrepancyMm = archPerimeterMm - requiredMm;
  return { availableMm: archPerimeterMm, requiredMm, discrepancyMm };
}
