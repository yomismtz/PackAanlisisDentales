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

export function littleIrregularityIndex(contactPoints) {
  if (!Array.isArray(contactPoints) || contactPoints.length !== 6) return null;
  const segments = [];
  for (let i = 1; i < contactPoints.length; i += 1) {
    segments.push(distanceBetweenPoints(contactPoints[i - 1], contactPoints[i]));
  }
  if (segments.some((v) => v === null)) return null;
  return { segments, total: segments.reduce((sum, v) => sum + v, 0) };
}

export function estimateFourIncisorSumRange(widthsPx, lateralMeanMm = 6.1, lateralSdMm = 0.5) {
  if (!Array.isArray(widthsPx) || widthsPx.length !== 4 || widthsPx.some((v) => !Number.isFinite(v) || v <= 0)) return null;
  if (!Number.isFinite(lateralMeanMm) || !Number.isFinite(lateralSdMm) || lateralMeanMm <= lateralSdMm || lateralSdMm < 0) return null;
  const lateralReferencePx = (widthsPx[0] + widthsPx[3]) / 2;
  if (!(lateralReferencePx > 0)) return null;
  const sumPx = widthsPx.reduce((sum, value) => sum + value, 0);
  return [sumPx * (lateralMeanMm - lateralSdMm) / lateralReferencePx,
    sumPx * (lateralMeanMm + lateralSdMm) / lateralReferencePx];
}

export function scaleSpaceRange(spacePx, referencePx, referenceMeanMm, referenceSdMm) {
  if (![spacePx, referencePx, referenceMeanMm, referenceSdMm].every(Number.isFinite)) return null;
  if (spacePx < 0 || referencePx <= 0 || referenceMeanMm <= referenceSdMm || referenceSdMm < 0) return null;
  return [spacePx * (referenceMeanMm - referenceSdMm) / referencePx,
    spacePx * (referenceMeanMm + referenceSdMm) / referencePx];
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
  if (available[0] >= required[1]) return "Hay espacio";
  if (available[1] < required[0]) return "No hay espacio";
  return "No concluyente";
}
