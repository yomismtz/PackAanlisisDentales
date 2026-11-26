export type Point2D = { x: number; y: number };
export function distanceBetweenPoints(a: Point2D | null | undefined, b: Point2D | null | undefined): number | null;
export function polylineLength(points: Point2D[] | null | undefined): number | null;
export function littleIrregularityIndex(contactPairs: [Point2D | null | undefined, Point2D | null | undefined][] | null | undefined): { segments: number[]; total: number } | null;
export function moyers75Prediction(incisorSumMm: number, sex: "Femenino" | "Masculino", arch: "superior" | "inferior"): number | null;
export function tanakaJohnstonPrediction(incisorSumMm: number, arch: "superior" | "inferior"): number | null;
export function classifySpaceRange(available: [number, number] | null, required: [number, number] | null): string;

export function pixelsToMillimeters(valuePx: number, pixelsPerMm: number): number | null;
