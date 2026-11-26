export type PhotoMode =
  | "facial_frontal"
  | "facial_profile"
  | "facial_midlines"
  | "facial_levels"
  | "facial_contour"
  | "powell"
  | "smile"
  | "facial_projections"
  | "facial_symmetry";

export type Point = { x: number; y: number };
export type PointMap = Record<string, Point>;
export type PhotoFormula =
  | "frontal"
  | "profile"
  | "midlines"
  | "levels"
  | "contour"
  | "powell"
  | "smile"
  | "projections"
  | "symmetry";

export type PhotoConfig = {
  title: string;
  slot: "extra_frontal" | "extra_profile" | "extra_smiling";
  formula: PhotoFormula;
  points: Array<{ code: string; label: string }>;
  measures: Array<{ label: string; a: string; b: string }>;
};

export type PhotoResult = {
  label: string;
  value: string;
  reference: string;
};

export const PHOTO_CONFIG: Record<PhotoMode, PhotoConfig> = {
  facial_frontal: {
    title: "Análisis facial frontal vertical",
    slot: "extra_frontal",
    formula: "frontal",
    points: [
      { code: "Tr", label: "Implantación del cabello" },
      { code: "Of", label: "Borde superior de cejas" },
      { code: "N", label: "Nasion" },
      { code: "Sn", label: "Subnasal" },
      { code: "Me", label: "Mentón" },
      { code: "Sts", label: "Stomion superior" },
      { code: "Sti", label: "Stomion inferior" },
    ],
    measures: [
      { label: "Tercio superior Tr–Of", a: "Tr", b: "Of" },
      { label: "Tercio medio Of–Sn", a: "Of", b: "Sn" },
      { label: "Tercio inferior Sn–Me", a: "Sn", b: "Me" },
      { label: "N–Sn", a: "N", b: "Sn" },
      { label: "Sn–Me", a: "Sn", b: "Me" },
      { label: "N–Me", a: "N", b: "Me" },
      { label: "Sn–St", a: "Sn", b: "Sts" },
      { label: "St–Me", a: "Sti", b: "Me" },
    ],
  },
  facial_profile: {
    title: "Análisis facial sagital vertical",
    slot: "extra_profile",
    formula: "profile",
    points: [
      { code: "Tr", label: "Implantación del cabello" },
      { code: "Of", label: "Borde superior de cejas" },
      { code: "N", label: "Nasion blando" },
      { code: "Sn", label: "Subnasal" },
      { code: "Me", label: "Mentón" },
      { code: "Sts", label: "Stomion superior" },
      { code: "Sti", label: "Stomion inferior" },
    ],
    measures: [
      { label: "Tercio superior Tr–Of", a: "Tr", b: "Of" },
      { label: "Tercio medio Of–Sn", a: "Of", b: "Sn" },
      { label: "Tercio inferior Sn–Me", a: "Sn", b: "Me" },
      { label: "N–Sn", a: "N", b: "Sn" },
      { label: "Sn–Me", a: "Sn", b: "Me" },
      { label: "N–Me", a: "N", b: "Me" },
      { label: "Sn–St", a: "Sn", b: "Sts" },
      { label: "St–Me", a: "Sti", b: "Me" },
    ],
  },
  facial_midlines: {
    title: "Análisis de líneas medias",
    slot: "extra_frontal",
    formula: "midlines",
    points: [
      { code: "ICD", label: "Canto interno derecho" },
      { code: "ICI", label: "Canto interno izquierdo" },
      { code: "LS", label: "Centro del labio superior / filtro" },
      { code: "NAR", label: "Punta nasal" },
      { code: "MENT", label: "Centro del mentón" },
      { code: "UIS", label: "Línea media incisivos superiores" },
      { code: "LIS", label: "Línea media incisivos inferiores" },
    ],
    measures: [{ label: "Distancia intercantal", a: "ICD", b: "ICI" }],
  },
  facial_levels: {
    title: "Análisis de niveles faciales",
    slot: "extra_frontal",
    formula: "levels",
    points: [
      { code: "OD", label: "Punto ocular derecho" },
      { code: "OI", label: "Punto ocular izquierdo" },
      { code: "CD", label: "Canino superior derecho" },
      { code: "CI", label: "Canino superior izquierdo" },
      { code: "ID", label: "Canino inferior derecho" },
      { code: "II", label: "Canino inferior izquierdo" },
      { code: "MD", label: "Cuerpo mandibular derecho" },
      { code: "MI", label: "Cuerpo mandibular izquierdo" },
      { code: "MTD", label: "Mentón derecho" },
      { code: "MTI", label: "Mentón izquierdo" },
    ],
    measures: [
      { label: "Nivel ocular", a: "OD", b: "OI" },
      { label: "Nivel caninos superiores", a: "CD", b: "CI" },
      { label: "Nivel caninos inferiores", a: "ID", b: "II" },
      { label: "Nivel mandibular", a: "MD", b: "MI" },
      { label: "Nivel mentoniano", a: "MTD", b: "MTI" },
    ],
  },
  facial_contour: {
    title: "Análisis de contorno facial",
    slot: "extra_frontal",
    formula: "contour",
    points: [
      { code: "ZG_R", label: "Punto cigomático derecho" },
      { code: "ZG_L", label: "Punto cigomático izquierdo" },
      { code: "MA_R", label: "Ángulo mandibular derecho" },
      { code: "MA_L", label: "Ángulo mandibular izquierdo" },
      { code: "CB_R", label: "Cuerpo mandibular derecho" },
      { code: "CB_L", label: "Cuerpo mandibular izquierdo" },
      { code: "ME_R", label: "Mentón derecho" },
      { code: "ME_L", label: "Mentón izquierdo" },
      { code: "AL_R", label: "Ala nasal derecha" },
      { code: "AL_L", label: "Ala nasal izquierda" },
    ],
    measures: [
      { label: "Ancho cigomático", a: "ZG_R", b: "ZG_L" },
      { label: "Ancho mandibular", a: "CB_R", b: "CB_L" },
      { label: "Ancho nasal", a: "AL_R", b: "AL_L" },
    ],
  },
  powell: {
    title: "Análisis de Powell",
    slot: "extra_profile",
    formula: "powell",
    points: [
      { code: "G", label: "Glabela" },
      { code: "N", label: "Nasion blando" },
      { code: "R", label: "Radix nasal" },
      { code: "Prn", label: "Punta nasal / pronasale" },
      { code: "Pg", label: "Pogonion blando" },
      { code: "C", label: "Punto cervical" },
      { code: "Me", label: "Menton blando" },
    ],
    measures: [],
  },
  smile: {
    title: "Análisis de sonrisa",
    slot: "extra_smiling",
    formula: "smile",
    points: [
      { code: "LC_R", label: "Comisura derecha" },
      { code: "LC_L", label: "Comisura izquierda" },
      { code: "PUP_R", label: "Centro pupilar derecho" },
      { code: "PUP_L", label: "Centro pupilar izquierdo" },
      { code: "CU_R", label: "Punta de canino superior derecho" },
      { code: "CU_L", label: "Punta de canino superior izquierdo" },
      { code: "ST", label: "Centro del labio superior" },
      { code: "LI", label: "Centro del labio inferior" },
      { code: "D11", label: "Borde incisal central superior derecho" },
      { code: "D21", label: "Borde incisal central superior izquierdo" },
    ],
    measures: [],
  },
  facial_projections: {
    title: "Análisis de proyecciones",
    slot: "extra_profile",
    formula: "projections",
    points: [
      { code: "N", label: "Nasion blando · referencia TVL" },
      { code: "G", label: "Glabela" },
      { code: "OR", label: "Reborde orbitario" },
      { code: "MAL", label: "Pómulo / malar" },
      { code: "SUBP", label: "Punto subpupilar" },
      { code: "BB", label: "Base basal" },
      { code: "LS", label: "Labio superior" },
      { code: "PRN", label: "Punta nasal" },
      { code: "LI", label: "Labio inferior" },
      { code: "PG", label: "Pogonion blando" },
    ],
    measures: [],
  },
  facial_symmetry: {
    title: "Análisis de simetrías horizontales",
    slot: "extra_frontal",
    formula: "symmetry",
    points: [
      { code: "F_R", label: "Contorno facial lateral derecho" },
      { code: "CL_R", label: "Canto lateral derecho" },
      { code: "CM_R", label: "Canto medial derecho" },
      { code: "CM_L", label: "Canto medial izquierdo" },
      { code: "CL_L", label: "Canto lateral izquierdo" },
      { code: "F_L", label: "Contorno facial lateral izquierdo" },
      { code: "AL_R", label: "Ala nasal derecha" },
      { code: "AL_L", label: "Ala nasal izquierda" },
      { code: "PU_R", label: "Centro pupilar derecho" },
      { code: "PU_L", label: "Centro pupilar izquierdo" },
      { code: "COM_R", label: "Comisura derecha" },
      { code: "COM_L", label: "Comisura izquierda" },
    ],
    measures: [
      { label: "Quinto lateral derecho", a: "F_R", b: "CL_R" },
      { label: "Quinto ocular derecho", a: "CL_R", b: "CM_R" },
      { label: "Quinto central", a: "CM_R", b: "CM_L" },
      { label: "Quinto ocular izquierdo", a: "CM_L", b: "CL_L" },
      { label: "Quinto lateral izquierdo", a: "CL_L", b: "F_L" },
      { label: "Ancho nasal", a: "AL_R", b: "AL_L" },
      { label: "Ancho bucal", a: "COM_R", b: "COM_L" },
      { label: "Distancia intercantal", a: "CM_R", b: "CM_L" },
    ],
  },
};

export const PHOTO_GUIDES: Record<PhotoConfig["slot"], string> = {
  extra_frontal:
    "FOTOGRAFÍA REQUERIDA · FRONTAL EN REPOSO. Rostro de frente, cabeza en posición natural, mirada al frente y labios relajados, sin sonreír. Cabello recogido, frente completamente despejada y ambas orejas descubiertas. Iluminación uniforme y fondo neutro.",
  extra_profile:
    "FOTOGRAFÍA REQUERIDA · PERFIL LATERAL EN REPOSO. Mantener siempre el mismo lado, cabeza en posición natural, mirada al frente y labios relajados. Cabello recogido, frente despejada y oreja del lado fotografiado descubierta. Deben verse nariz, labios, mentón y cuello.",
  extra_smiling:
    "FOTOGRAFÍA REQUERIDA · FRONTAL SONRIENDO. Sonrisa amplia y natural, mostrando dientes y encía visible. Rostro de frente, cabeza sin inclinación, mirada al frente, cabello recogido, frente despejada y ambas orejas descubiertas. Deben verse ambas comisuras.",
};

export const VISUAL_OPTIONS: Partial<Record<PhotoFormula, Record<string, string[]>>> = {
  midlines: {
    "Punta de la nariz": ["Derecha", "Centrada", "Izquierda"],
    Filtro: ["Derecha", "Centrado", "Izquierda"],
    Mentón: ["Derecha", "Centrado", "Izquierda"],
    "Línea media incisivos superiores": ["Derecha", "Centrada", "Izquierda"],
    "Línea media incisivos inferiores": ["Derecha", "Centrada", "Izquierda"],
  },
  levels: {
    "Ojos · desviación": ["Derecha", "Centrada", "Izquierda"],
    "Ojos · inclinación": ["Arriba", "Abajo", "Sin inclinación"],
    "Caninos superiores · desviación": ["Derecha", "Centrados", "Izquierda"],
    "Caninos superiores · inclinación": ["Arriba", "Abajo", "Sin inclinación"],
    "Caninos inferiores · desviación": ["Derecha", "Centrados", "Izquierda"],
    "Caninos inferiores · inclinación": ["Arriba", "Abajo", "Sin inclinación"],
    "Cuerpo mandibular · desviación": ["Derecha", "Centrado", "Izquierda"],
    "Cuerpo mandibular · inclinación": ["Arriba", "Abajo", "Sin inclinación"],
    "Nivel mentoniano · desviación": ["Derecha", "Centrado", "Izquierda"],
    "Nivel mentoniano · inclinación": ["Arriba", "Abajo", "Sin inclinación"],
  },
  smile: {
    "Línea de los labios": ["Alta", "Media", "Baja"],
    "Arco de sonrisa": ["Consonante", "Paralelo", "No consonante"],
    "Curvatura del labio superior": ["Alta", "Recta", "Baja"],
    "Espacios negativos": ["Presentes", "Ausentes"],
    "Simetría de sonrisa": ["Simétrica", "Asimétrica"],
    "Plano oclusal frontal": ["Aceptable", "No aceptable"],
    "Componente dental": ["Aceptable", "No aceptable"],
    "Componente gingival": ["Aceptable", "No aceptable"],
  },
  contour: {
    "Forma facial": ["Redonda", "Cuadrada", "Alargada"],
    "Tamaño facial": ["Estrecho", "Ancho", "Normal"],
    "Cigomático derecho": ["Grande", "Ancho", "Normal", "Estrecho"],
    "Cigomático izquierdo": ["Grande", "Ancho", "Normal", "Estrecho"],
    "Ángulo mandibular derecho": ["Grande", "Ancho", "Normal", "Estrecho"],
    "Ángulo mandibular izquierdo": ["Grande", "Ancho", "Normal", "Estrecho"],
    "Cuerpo mandibular derecho": ["Grande", "Ancho", "Normal", "Estrecho"],
    "Cuerpo mandibular izquierdo": ["Grande", "Ancho", "Normal", "Estrecho"],
    "Mentón derecho": ["Grande", "Ancho", "Normal", "Estrecho"],
    "Mentón izquierdo": ["Grande", "Ancho", "Normal", "Estrecho"],
    "Base alar derecha": ["Grande", "Ancha", "Normal", "Estrecha"],
    "Base alar izquierda": ["Grande", "Ancha", "Normal", "Estrecha"],
  },
};

function getDistance(points: PointMap, a: string, b: string): number | null {
  const pa = points[a];
  const pb = points[b];
  if (!pa || !pb) return null;
  return Math.hypot(pb.x - pa.x, pb.y - pa.y);
}

function getVerticalDistance(points: PointMap, a: string, b: string): number | null {
  const pa = points[a];
  const pb = points[b];
  return pa && pb ? Math.abs(pb.y - pa.y) : null;
}

function getHorizontalDistance(points: PointMap, a: string, b: string): number | null {
  const pa = points[a];
  const pb = points[b];
  return pa && pb ? Math.abs(pb.x - pa.x) : null;
}

function getAngle(points: PointMap, a: string, b: string, c: string): number | null {
  const p = points[a];
  const q = points[b];
  const r = points[c];
  if (!p || !q || !r) return null;
  const v = { x: p.x - q.x, y: p.y - q.y };
  const w = { x: r.x - q.x, y: r.y - q.y };
  const denominator = Math.hypot(v.x, v.y) * Math.hypot(w.x, w.y);
  if (!denominator) return null;
  const cosine = Math.max(-1, Math.min(1, (v.x * w.x + v.y * w.y) / denominator));
  return (Math.acos(cosine) * 180) / Math.PI;
}

function lineInclination(a: Point, b: Point): number | null {
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  if (!Math.hypot(dx, dy)) return null;
  const angle = (Math.atan2(dy, dx) * 180) / Math.PI;
  return (((angle + 90) % 180) + 180) % 180 - 90;
}

function angleDifference(a1: Point, a2: Point, b1: Point, b2: Point): number | null {
  const first = lineInclination(a1, a2);
  const second = lineInclination(b1, b2);
  if (first === null || second === null) return null;
  const difference = Math.abs(first - second);
  return Math.min(difference, 180 - difference);
}

function getLineAngle(points: PointMap, a: string, b: string, c: string, d: string): number | null {
  const p1=points[a],p2=points[b],p3=points[c],p4=points[d];
  return p1&&p2&&p3&&p4?angleDifference(p1,p2,p3,p4):null;
}

function proportions(lengths: number[]): number[] | null {
  if (!lengths.length || lengths.some((value) => value < 0)) return null;
  const total = lengths.reduce((sum, value) => sum + value, 0);
  return total > 0 ? lengths.map((value) => (value / total) * 100) : null;
}

function bilateralDifference(right: number | null, left: number | null): [number, number | null] | null {
  if (right === null || left === null) return null;
  const difference = Math.abs(right - left);
  const mean = (right + left) / 2;
  return [difference, mean > 0 ? (difference / mean) * 100 : null];
}

const px = (value: number | null) => (value === null ? "Pendiente" : value.toFixed(2) + " px");
const deg = (value: number | null) => (value === null ? "Pendiente" : value.toFixed(2) + "°");

export function calculatePhotoResults(mode: PhotoMode, points: PointMap): PhotoResult[] {
  const cfg = PHOTO_CONFIG[mode];
  const rows: PhotoResult[] = [];
  const add = (label: string, value: string, reference = "") => rows.push({ label, value, reference });

  if (cfg.formula === "frontal" || cfg.formula === "profile") {
    for (const measure of cfg.measures) {
      add(
        measure.label,
        px(getVerticalDistance(points, measure.a, measure.b)),
        "Distancia relativa en píxeles de la fotografía",
      );
    }
    const total = getVerticalDistance(points, "N", "Me");
    const ns = getVerticalDistance(points, "N", "Sn");
    const sm = getVerticalDistance(points, "Sn", "Me");
    if (total && ns !== null && sm !== null) {
      add("N–Sn (%)", ((ns / total) * 100).toFixed(1) + " %", "Proporción vertical dentro de N–Me");
      add("Sn–Me (%)", ((sm / total) * 100).toFixed(1) + " %", "Proporción vertical dentro de N–Me");
    }
    const thirds = [
      getVerticalDistance(points, "Tr", "Of"),
      getVerticalDistance(points, "Of", "Sn"),
      getVerticalDistance(points, "Sn", "Me"),
    ];
    if (thirds.every((value): value is number => value !== null)) {
      const percentages = proportions(thirds);
      if (percentages) {
        ["Tercio superior (%)", "Tercio medio (%)", "Tercio inferior (%)"].forEach((label, index) =>
          add(label, percentages[index].toFixed(1) + " %", "Proporción de la suma de los tres tercios Tr–Me"),
        );
      }
    }
    if (points.Sn && points.Sts && points.Sti && points.Me) {
      const stY = (points.Sts.y + points.Sti.y) / 2;
      const snSt = Math.abs(stY - points.Sn.y);
      const stMe = Math.abs(points.Me.y - stY);
      if (snSt + stMe) {
        add("Sn–St (%)", ((snSt / (snSt + stMe)) * 100).toFixed(1) + " %", "Proporción relativa de la imagen");
        add("St–Me (%)", ((stMe / (snSt + stMe)) * 100).toFixed(1) + " %", "Proporción relativa de la imagen");
      }
    }
  } else if (cfg.formula === "smile") {
    const { PUP_R, PUP_L, LC_R, LC_L } = points;
    if (PUP_R && PUP_L && LC_R && LC_L) {
      const difference = angleDifference(PUP_R, PUP_L, LC_R, LC_L);
      if (difference !== null) {
        add(
          "Diferencia angular bipupilar–comisural",
          deg(difference),
          "Ángulo agudo entre ambas líneas (0° paralelas; 90° perpendiculares); no es una clasificación clínica",
        );
      }
    }
  } else if (cfg.formula === "midlines") {
    if (points.ICD && points.ICI && points.LS) {
      const bridge = {
        x: (points.ICD.x + points.ICI.x) / 2,
        y: (points.ICD.y + points.ICI.y) / 2,
      };
      const lip = points.LS;
      const vx = lip.x - bridge.x;
      const vy = lip.y - bridge.y;
      const norm = Math.hypot(vx, vy);
      if (norm) {
        [
          ["Punta de la nariz", "NAR"],
          ["Mentón", "MENT"],
          ["Línea media incisivos superiores", "UIS"],
          ["Línea media incisivos inferiores", "LIS"],
        ].forEach(([label, key]) => {
          const point = points[key];
          if (point) {
            const signed = (vx * (point.y - bridge.y) - vy * (point.x - bridge.x)) / norm;
            add(
              label,
              (signed >= 0 ? "+" : "") + signed.toFixed(2) + " px",
              "Desviación perpendicular relativa al eje puente nasal–labio superior",
            );
          }
        });
      }
    }
  } else if (cfg.formula === "levels") {
    for (const measure of cfg.measures) {
      const a = points[measure.a];
      const b = points[measure.b];
      if (a && b) {
        const inclination = lineInclination(a, b);
        if (inclination !== null) {
          add(
            measure.label,
            (inclination >= 0 ? "+" : "") + inclination.toFixed(2) + "°",
            "Desnivel relativo " +
              Math.abs(b.y - a.y).toFixed(2) +
              " px; inclinación respecto a la horizontal de la imagen; completar la dirección en evaluación visual",
          );
        }
      }
    }
  } else if (cfg.formula === "powell") {
    const items: Array<{label:string;value:number|null;reference:string}> = [
      {label:"Nasofrontal",value:getAngle(points,"G","N","R"),reference:"115°–130° · vértice N"},
      {label:"Nasofacial",value:getLineAngle(points,"G","Pg","N","Prn"),reference:"30°–40° · plano facial G–Pg con dorso nasal N–Prn"},
      {label:"Nasomental",value:getAngle(points,"N","Prn","Pg"),reference:"120°–132° · vértice Prn"},
      {label:"Mentocervical",value:getLineAngle(points,"G","Pg","Me","C"),reference:"80°–95° · plano facial G–Pg con línea mentón–cervical Me–C"},
    ];
    for (const item of items) add(item.label,deg(item.value),item.reference);
  } else if (cfg.formula === "projections") {
    if (points.N) {
      const x0 = points.N.x;
      [
        ["Glabela", "G"],
        ["Reborde orbitario", "OR"],
        ["Pómulo", "MAL"],
        ["Punto subpupilar", "SUBP"],
        ["Base basal", "BB"],
        ["Labio superior", "LS"],
        ["Punta nasal", "PRN"],
        ["Labio inferior", "LI"],
        ["Pogonion", "PG"],
      ].forEach(([label, key]) => {
        const point = points[key];
        if (point) {
          const dx = point.x - x0;
          add(label, (dx >= 0 ? "+" : "") + dx.toFixed(2) + " px", "Desviación horizontal relativa respecto a N; no representa milímetros");
        }
      });
    }
  } else if (cfg.formula === "symmetry") {
    for (const measure of cfg.measures) {
      add(
        measure.label,
        px(getDistance(points, measure.a, measure.b)),
        "Distancia relativa en la misma fotografía; no equivale a milímetros",
      );
    }
    const comparisons: Array<[string, [string, string], [string, string]]> = [
      ["Diferencia entre quintos laterales derecho–izquierdo", ["F_R", "CL_R"], ["CL_L", "F_L"]],
      ["Diferencia entre quintos oculares derecho–izquierdo", ["CL_R", "CM_R"], ["CM_L", "CL_L"]],
    ];
    for (const [label, rightPair, leftPair] of comparisons) {
      const comparison = bilateralDifference(
        getDistance(points, rightPair[0], rightPair[1]),
        getDistance(points, leftPair[0], leftPair[1]),
      );
      if (comparison) {
        const [difference, percent] = comparison;
        add(
          label,
          difference.toFixed(2) + " px" + (percent === null ? "" : " (" + percent.toFixed(1) + " % relativo)"),
          "Diferencia absoluta entre longitudes bilaterales marcadas; no constituye diagnóstico por sí sola",
        );
      }
    }
  } else if (cfg.formula === "contour") {
    for (const measure of cfg.measures) {
      add(
        measure.label,
        px(getHorizontalDistance(points, measure.a, measure.b)),
        "Separación horizontal relativa en la fotografía; no equivale a milímetros",
      );
    }
    const comparisons: Array<[string, [string, string], [string, string]]> = [
      ["Diferencia bilateral cigomático–ángulo mandibular", ["ZG_R", "MA_R"], ["ZG_L", "MA_L"]],
      ["Diferencia bilateral ángulo–cuerpo mandibular", ["MA_R", "CB_R"], ["MA_L", "CB_L"]],
      ["Diferencia bilateral cuerpo mandibular–mentón", ["CB_R", "ME_R"], ["CB_L", "ME_L"]],
    ];
    for (const [label, rightPair, leftPair] of comparisons) {
      const comparison = bilateralDifference(
        getDistance(points, rightPair[0], rightPair[1]),
        getDistance(points, leftPair[0], leftPair[1]),
      );
      if (comparison) {
        const [difference, percent] = comparison;
        add(
          label,
          difference.toFixed(2) + " px" + (percent === null ? "" : " (" + percent.toFixed(1) + " % relativo)"),
          "Diferencia absoluta entre longitudes bilaterales marcadas; no constituye diagnóstico por sí sola",
        );
      }
    }
  }
  return rows;
}


function describeBilateralPair(
  label: string,
  right: number | null,
  left: number | null,
): string | null {
  if (right === null || left === null) return null;
  const difference = Math.abs(right - left);
  const mean = (right + left) / 2;
  const relative = mean > 0 ? (difference / mean) * 100 : null;
  if (difference.toFixed(2) === "0.00") {
    return `${label}: las medidas derecha e izquierda coinciden a la precisión mostrada (${right.toFixed(2)} px).`;
  }
  return `${label}: las medidas no coinciden; derecha ${right.toFixed(2)} px e izquierda ${left.toFixed(2)} px. Diferencia: ${difference.toFixed(2)} px${relative === null ? "" : ` (${relative.toFixed(1)} % relativo)`}.`;
}

function describeProportions(
  label: string,
  firstName: string,
  first: number,
  secondName: string,
  second: number,
): string {
  const firstRounded = first.toFixed(1);
  const secondRounded = second.toFixed(1);
  if (firstRounded === secondRounded) {
    return `${label}: ${firstName} y ${secondName} presentan proporciones equivalentes a la precisión mostrada (${firstRounded} % cada uno).`;
  }
  const larger = first > second ? firstName : secondName;
  const smaller = first > second ? secondName : firstName;
  const largerValue = Math.max(first, second);
  const smallerValue = Math.min(first, second);
  return `${label}: ${larger} representa una proporción mayor (${largerValue.toFixed(1)} %) que ${smaller} (${smallerValue.toFixed(1)} %).`;
}

/**
 * Produce observaciones descriptivas derivadas de los mismos puntos y cálculos
 * que aparecen en la tabla. No introduce umbrales clínicos nuevos.
 */
export function summarizePhotoAnalysis(
  mode: PhotoMode,
  points: PointMap,
  visualValues: Record<string, string> = {},
): string[] {
  const conclusions: string[] = [];
  const cfg = PHOTO_CONFIG[mode];

  if (cfg.formula === "frontal" || cfg.formula === "profile") {
    const thirdNames = ["Tercio superior", "Tercio medio", "Tercio inferior"];
    const thirdValues = [
      getVerticalDistance(points, "Tr", "Of"),
      getVerticalDistance(points, "Of", "Sn"),
      getVerticalDistance(points, "Sn", "Me"),
    ];
    if (thirdValues.every((value): value is number => value !== null)) {
      const total = thirdValues.reduce((sum, value) => sum + value, 0);
      const percentages = proportions(thirdValues);
      if (total > 0 && percentages) {
        const ranked = thirdValues
          .map((value, index) => ({ name: thirdNames[index], value, percent: percentages[index] }))
          .sort((a, b) => b.value - a.value);
        const largest = ranked.filter((item) => item.percent.toFixed(1) === ranked[0].percent.toFixed(1));
        const smallest = ranked.filter((item) => item.percent.toFixed(1) === ranked[2].percent.toFixed(1));
        const largestNames = largest.map((item) => item.name.toLowerCase()).join(" y ");
        const smallestNames = smallest.map((item) => item.name.toLowerCase()).join(" y ");
        if (new Set(percentages.map((value) => value.toFixed(1))).size === 1) {
          conclusions.push(
            `Los tres tercios presentan proporciones equivalentes a la precisión mostrada: ${percentages.map((value) => value.toFixed(1) + " %").join(", ")}.`,
          );
        } else {
          conclusions.push(
            `${largestNames.charAt(0).toUpperCase() + largestNames.slice(1)} ${largest.length > 1 ? "comparten" : "es"} ${largest.length > 1 ? "la mayor proporción" : "el de mayor dimensión vertical"} (${largest.map((item) => item.value.toFixed(2) + " px / " + item.percent.toFixed(1) + " %").join(" y ")}).`,
          );
          conclusions.push(
            `${smallestNames.charAt(0).toUpperCase() + smallestNames.slice(1)} ${smallest.length > 1 ? "comparten" : "es"} ${smallest.length > 1 ? "la menor proporción" : "el de menor dimensión vertical"} (${smallest.map((item) => item.value.toFixed(2) + " px / " + item.percent.toFixed(1) + " %").join(" y ")}).`,
          );
          conclusions.push(
            `Las proporciones de los tres tercios no coinciden entre sí. La diferencia entre el mayor y el menor es ${(ranked[0].percent - ranked[2].percent).toFixed(1)} puntos porcentuales.`,
          );
        }
      }
    }

    const totalNm = getVerticalDistance(points, "N", "Me");
    const ns = getVerticalDistance(points, "N", "Sn");
    const sm = getVerticalDistance(points, "Sn", "Me");
    if (totalNm && ns !== null && sm !== null) {
      conclusions.push(
        describeProportions("Dentro del segmento N–Me", "N–Sn", (ns / totalNm) * 100, "Sn–Me", (sm / totalNm) * 100),
      );
    }

    if (points.Sn && points.Sts && points.Sti && points.Me) {
      const stomionY = (points.Sts.y + points.Sti.y) / 2;
      const snSt = Math.abs(stomionY - points.Sn.y);
      const stMe = Math.abs(points.Me.y - stomionY);
      const sum = snSt + stMe;
      if (sum > 0) {
        conclusions.push(
          describeProportions("Relación subnasal–mentón", "Sn–St", (snSt / sum) * 100, "St–Me", (stMe / sum) * 100),
        );
      }
    }
  } else if (cfg.formula === "symmetry") {
    const comparisons: Array<[string, [string, string], [string, string]]> = [
      ["Quintos laterales", ["F_R", "CL_R"], ["CL_L", "F_L"]],
      ["Quintos oculares", ["CL_R", "CM_R"], ["CM_L", "CL_L"]],
    ];
    for (const [label, rightPair, leftPair] of comparisons) {
      const observation = describeBilateralPair(
        label,
        getDistance(points, rightPair[0], rightPair[1]),
        getDistance(points, leftPair[0], leftPair[1]),
      );
      if (observation) conclusions.push(observation);
    }
    const unequalFifths = conclusions
      .filter((item) => item.includes("no coinciden"))
      .map((item) => item.slice(0, item.indexOf(":")));
    if (!conclusions.length) {
      conclusions.push("Aún faltan puntos para comparar las medidas bilaterales de los quintos faciales.");
    } else if (unequalFifths.length) {
      conclusions.push(
        `Conclusión: se observa asimetría geométrica relativa en ${unequalFifths.join(" y ")}. La observación se limita a los segmentos medidos y no determina por sí sola la simetría clínica de todo el rostro.`,
      );
    } else {
      conclusions.push("No se identificaron diferencias entre las longitudes de los quintos comparados a la precisión mostrada; esto no equivale a una certificación de simetría facial completa.");
    }
  } else if (cfg.formula === "contour") {
    const comparisons: Array<[string, [string, string], [string, string]]> = [
      ["Segmento cigomático–ángulo mandibular", ["ZG_R", "MA_R"], ["ZG_L", "MA_L"]],
      ["Segmento ángulo–cuerpo mandibular", ["MA_R", "CB_R"], ["MA_L", "CB_L"]],
      ["Segmento cuerpo mandibular–mentón", ["CB_R", "ME_R"], ["CB_L", "ME_L"]],
    ];
    for (const [label, rightPair, leftPair] of comparisons) {
      const observation = describeBilateralPair(
        label,
        getDistance(points, rightPair[0], rightPair[1]),
        getDistance(points, leftPair[0], leftPair[1]),
      );
      if (observation) conclusions.push(observation);
    }
    for (const label of ["Forma facial", "Tamaño facial"]) {
      const value = visualValues[label];
      if (value && value !== "Sin evaluar") {
        conclusions.push(`${label}: ${value.toLowerCase()}.`);
      }
    }
    const contourPairs: Array<[string, string, string]> = [
      ["Cigomático", "Cigomático derecho", "Cigomático izquierdo"],
      ["Ángulo mandibular", "Ángulo mandibular derecho", "Ángulo mandibular izquierdo"],
      ["Cuerpo mandibular", "Cuerpo mandibular derecho", "Cuerpo mandibular izquierdo"],
      ["Mentón", "Mentón derecho", "Mentón izquierdo"],
      ["Base alar", "Base alar derecha", "Base alar izquierda"],
    ];
    for (const [label, rightKey, leftKey] of contourPairs) {
      const rightValue = visualValues[rightKey];
      const leftValue = visualValues[leftKey];
      if (rightValue && leftValue && rightValue !== "Sin evaluar" && leftValue !== "Sin evaluar") {
        conclusions.push(
          rightValue === leftValue
            ? `${label}: la descripción visual registrada coincide en ambos lados (${rightValue.toLowerCase()}).`
            : `${label}: las descripciones visuales derecha e izquierda no coinciden (${rightValue.toLowerCase()} / ${leftValue.toLowerCase()}).`,
        );
      }
    }
    const unequalContour = conclusions
      .filter((item) => item.includes("no coinciden"))
      .map((item) => item.slice(0, item.indexOf(":")));
    if (unequalContour.length) {
      conclusions.push(
        `Conclusión: se registran diferencias entre lado derecho e izquierdo en ${unequalContour.join(", ")}. La descripción se limita a los segmentos y criterios evaluados.`,
      );
    }
    if (!conclusions.length) conclusions.push("Coloca los puntos bilaterales y registra los criterios visuales para comparar ambos lados del contorno.");
  } else if (cfg.formula === "smile") {
    const { PUP_R, PUP_L, LC_R, LC_L } = points;
    if (PUP_R && PUP_L && LC_R && LC_L) {
      const difference = angleDifference(PUP_R, PUP_L, LC_R, LC_L);
      if (difference !== null) {
        conclusions.push(
          difference.toFixed(2) === "0.00"
            ? "La línea bipupilar y la línea comisural son paralelas a la precisión mostrada (diferencia angular 0.00°)."
            : `La línea bipupilar y la línea comisural no son paralelas; la diferencia angular registrada es de ${difference.toFixed(2)}°.`,
        );
      }
    } else {
      conclusions.push("Faltan puntos pupilares o comisurales para comparar la inclinación de ambas líneas.");
    }
  } else if (cfg.formula === "midlines") {
    if (points.ICD && points.ICI && points.LS) {
      const bridge = {
        x: (points.ICD.x + points.ICI.x) / 2,
        y: (points.ICD.y + points.ICI.y) / 2,
      };
      const vx = points.LS.x - bridge.x;
      const vy = points.LS.y - bridge.y;
      const norm = Math.hypot(vx, vy);
      if (norm > 0) {
        const landmarks: Array<[string, string]> = [
          ["Punta nasal", "NAR"],
          ["Mentón", "MENT"],
          ["Línea media incisivos superiores", "UIS"],
          ["Línea media incisivos inferiores", "LIS"],
        ];
        const deviations = landmarks.flatMap(([label, key]) => {
          const point = points[key];
          if (!point) return [];
          const signed = (vx * (point.y - bridge.y) - vy * (point.x - bridge.x)) / norm;
          return [{ label, signed }];
        });
        const displaced = deviations.filter((item) => Math.abs(item.signed) >= 0.01);
        conclusions.push("El punto LS (filtro / centro del labio superior) define el eje de referencia y no se interpreta como una desviación independiente.");
        if (displaced.length) {
          conclusions.push(
            `Puntos que se apartan del eje puente nasal–labio superior: ${displaced.map((item) => `${item.label} (${item.signed >= 0 ? "+" : ""}${item.signed.toFixed(2)} px)`).join("; ")}.`,
          );
        } else if (deviations.length) {
          conclusions.push("Los puntos de línea media colocados coinciden con el eje de referencia a la precisión de 0.01 px.");
        }
      }
    }
    if (!conclusions.length) conclusions.push("Coloca los puntos intercantales y el centro del labio superior para establecer el eje de referencia de las líneas medias.");
  } else if (cfg.formula === "levels") {
    for (const measure of cfg.measures) {
      const a = points[measure.a];
      const b = points[measure.b];
      if (!a || !b) continue;
      const inclination = lineInclination(a, b);
      if (inclination === null) continue;
      const verticalDifference = Math.abs(b.y - a.y);
      conclusions.push(
        verticalDifference.toFixed(2) === "0.00"
          ? `${measure.label}: los dos puntos se encuentran al mismo nivel vertical en la imagen.`
          : `${measure.label}: se registra un desnivel vertical de ${verticalDifference.toFixed(2)} px y una inclinación de ${inclination.toFixed(2)}°.`,
      );
    }
    if (!conclusions.length) conclusions.push("Coloca los pares de puntos anatómicos para describir los niveles faciales.");
  } else if (cfg.formula === "powell") {
    const measurements: Array<{label:string;value:number|null;min:number;max:number}> = [
      {label:"Nasofrontal",value:getAngle(points,"G","N","R"),min:115,max:130},
      {label:"Nasofacial",value:getLineAngle(points,"G","Pg","N","Prn"),min:30,max:40},
      {label:"Nasomental",value:getAngle(points,"N","Prn","Pg"),min:120,max:132},
      {label:"Mentocervical",value:getLineAngle(points,"G","Pg","Me","C"),min:80,max:95},
    ];
    for (const measurement of measurements) {
      const {label,value,min,max}=measurement;
      if(value===null)continue;
      const position=value<min?"por debajo":value>max?"por encima":"dentro";
      conclusions.push(`Ángulo ${label.toLowerCase()}: ${value.toFixed(2)}°; se encuentra ${position} del intervalo de referencia (${min}°–${max}°).`);
    }
    if (!conclusions.length) conclusions.push("Faltan puntos anatómicos para calcular los ángulos del análisis de Powell.");
  } else if (cfg.formula === "projections") {
    if (points.N) {
      const projections: Array<[string, string]> = [
        ["Glabela", "G"],
        ["Reborde orbitario", "OR"],
        ["Pómulo", "MAL"],
        ["Punto subpupilar", "SUBP"],
        ["Base basal", "BB"],
        ["Labio superior", "LS"],
        ["Punta nasal", "PRN"],
        ["Labio inferior", "LI"],
        ["Pogonion", "PG"],
      ];
      const placed = projections.flatMap(([label, key]) => {
        const point = points[key];
        return point ? [{ label, offset: point.x - points.N.x }] : [];
      });
      if (placed.length) {
        conclusions.push(
          `Proyecciones horizontales respecto a la vertical que pasa por N (eje de la imagen): ${placed.map((item) => `${item.label} ${item.offset >= 0 ? "+" : ""}${item.offset.toFixed(2)} px`).join("; ")}.`,
        );
      }
    }
    if (!conclusions.length) conclusions.push("Coloca Nasion blando y los puntos de proyección para obtener sus desviaciones horizontales relativas.");
  }

  const recordedVisualValues = Object.entries(visualValues).filter(
    ([, value]) => Boolean(value) && value !== "Sin evaluar",
  );
  if (recordedVisualValues.length && cfg.formula !== "contour") {
    conclusions.push(
      "Criterios visuales registrados: " +
        recordedVisualValues.map(([label, value]) => `${label}: ${value.toLowerCase()}`).join("; ") +
        ".",
    );
  }

  if (conclusions.length) {
    conclusions.push(
      "Interpretación descriptiva basada en los puntos colocados y las medidas relativas de esta fotografía. No aplica umbrales clínicos automáticos ni sustituye la valoración profesional.",
    );
  }
  return conclusions;
}
