export type CephalometricPoint = { x: number; y: number };
export type CephalometricPointMap = Record<string, CephalometricPoint>;
export function calculateCephalometry(points: CephalometricPointMap, pixelsPerMm?: number | null): { values: Record<string, number>; calculated: CephalometricPointMap };
