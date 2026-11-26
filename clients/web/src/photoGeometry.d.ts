export type PhotoLandmark = { x: number; y: number };
export type PhotoLandmarkMap = Record<string, PhotoLandmark>;
export function calculatePowellAngles(points: PhotoLandmarkMap): {
  nasofrontal: number | null;
  nasofacial: number | null;
  nasomental: number | null;
  mentocervical: number | null;
};

export function calculateVerticalFacialThirds(points: PhotoLandmarkMap): { lengths: [number, number, number]; percentages: [number, number, number] } | null;
