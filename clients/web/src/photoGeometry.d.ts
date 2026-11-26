export type PhotoLandmark = { x: number; y: number };
export type PhotoLandmarkMap = Record<string, PhotoLandmark>;
export function calculatePowellAngles(points: PhotoLandmarkMap): {
  nasofrontal: number | null;
  nasofacial: number | null;
  nasomental: number | null;
  mentocervical: number | null;
};

export function calculateVerticalFacialThirds(points: PhotoLandmarkMap): { lengths: [number, number, number]; percentages: [number, number, number] } | null;

export function lineInclinationDegrees(a: PhotoLandmark, b: PhotoLandmark): number | null;
export function acuteAngleBetweenLines(a1: PhotoLandmark, a2: PhotoLandmark, b1: PhotoLandmark, b2: PhotoLandmark): number | null;
export function horizontalDistancePx(a: PhotoLandmark, b: PhotoLandmark): number | null;
export function signedPerpendicularDistance(origin: PhotoLandmark, axisEnd: PhotoLandmark, point: PhotoLandmark): number | null;
