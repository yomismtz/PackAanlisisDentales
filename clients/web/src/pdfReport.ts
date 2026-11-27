import type { PaletteColors } from "./themePalettes";

export type ReportRow = {
  label: string;
  value: string;
  reference: string;
};

export type PhotoReportInput = {
  title: string;
  mode: string;
  fileName: string;
  status: string;
  photoDataUrl: string;
  photoWidth: number;
  photoHeight: number;
  horizontalGuides: boolean;
  points: Record<string, { x: number; y: number }>;
  results: ReportRow[];
  conclusions: string[];
  visualAssessment: Record<string, string>;
  observations: string;
  professionalConclusion: string;
  generatedAt: Date;
  palette: PaletteColors;
  paletteName?: string;
  reportLabel?: string;
  logoDataUrl?: string;
  clinicLogoDataUrl?: string;
  clinicWatermarkDataUrl?: string;
  birdIconDataUrl?: string;
  birdWatermarkDataUrl?: string;
};

type RGB = [number, number, number];

const BLACK: RGB = [20, 20, 20];
function toRgb(hex: string): RGB {
  const normalized = hex.replace("#", "");
  return [
    Number.parseInt(normalized.slice(0, 2), 16),
    Number.parseInt(normalized.slice(2, 4), 16),
    Number.parseInt(normalized.slice(4, 6), 16),
  ];
}
const PAGE_W = 595.28;
const PAGE_H = 841.89;

function color(rgb: RGB, stroke = false): string {
  const values = rgb.map((value) => (value / 255).toFixed(3)).join(" ");
  return values + (stroke ? " RG" : " rg");
}

function escapePdfText(value: string): string {
  const map: Record<string, number> = {
    "€": 0x80, "‚": 0x82, "ƒ": 0x83, "„": 0x84, "…": 0x85,
    "†": 0x86, "‡": 0x87, "ˆ": 0x88, "‰": 0x89, "Š": 0x8a,
    "‹": 0x8b, "Œ": 0x8c, "Ž": 0x8e, "‘": 0x91, "’": 0x92,
    "“": 0x93, "”": 0x94, "•": 0x95, "–": 0x96, "—": 0x97,
    "˜": 0x98, "™": 0x99, "š": 0x9a, "›": 0x9b, "œ": 0x9c,
    "ž": 0x9e, "Ÿ": 0x9f, "°": 0xb0,
  };
  let hex = "";
  for (const character of value) {
    const code = map[character] ?? character.charCodeAt(0);
    const safe = code <= 255 ? code : 0x3f;
    hex += safe.toString(16).padStart(2, "0");
  }
  return "<" + hex.toUpperCase() + ">";
}

function text(
  content: string,
  x: number,
  y: number,
  size = 9,
  font = "F1",
  rgb: RGB = BLACK,
): string {
  return `BT ${color(rgb)} /${font} ${size} Tf 1 0 0 1 ${x.toFixed(2)} ${y.toFixed(2)} Tm ${escapePdfText(content)} Tj ET\n`;
}

function line(x1: number, y1: number, x2: number, y2: number, rgb: RGB, width = 0.7): string {
  return `q ${color(rgb, true)} ${width} w ${x1.toFixed(2)} ${y1.toFixed(2)} m ${x2.toFixed(2)} ${y2.toFixed(2)} l S Q\n`;
}

function rectangle(
  x: number,
  y: number,
  width: number,
  height: number,
  fill: RGB | null,
  stroke: RGB | null,
  strokeWidth = 1,
): string {
  let command = "q ";
  if (fill) command += color(fill) + " ";
  if (stroke) command += color(stroke, true) + ` ${strokeWidth} w `;
  command += `${x.toFixed(2)} ${y.toFixed(2)} ${width.toFixed(2)} ${height.toFixed(2)} re `;
  command += fill && stroke ? "B" : fill ? "f" : "S";
  return command + " Q\n";
}

function wrapWords(value: string, maxCharacters: number): string[] {
  const words = value.trim().split(/\s+/).filter(Boolean);
  if (!words.length) return [""];
  const lines: string[] = [];
  let current = "";
  for (const word of words) {
    const next = current ? current + " " + word : word;
    if (next.length > maxCharacters && current) {
      lines.push(current);
      current = word;
    } else {
      current = next;
    }
  }
  if (current) lines.push(current);
  return lines;
}

function base64ToBytes(dataUrl: string): Uint8Array {
  const base64 = dataUrl.substring(dataUrl.indexOf(",") + 1);
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) {
    bytes[index] = binary.charCodeAt(index);
  }
  return bytes;
}


export async function loadAvisLogoDataUrl(): Promise<string> {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => {
      const canvas = document.createElement("canvas");
      canvas.width = 96;
      canvas.height = 96;
      const context = canvas.getContext("2d");
      if (!context) { reject(new Error("No fue posible preparar el logotipo de AVIS.")); return; }
      context.drawImage(image, 0, 0, 96, 96);
      resolve(canvas.toDataURL("image/jpeg", 0.94));
    };
    image.onerror = () => reject(new Error("No fue posible cargar el logotipo de AVIS."));
    image.src = "/avis-icon.svg";
  });
}

function loadBirdRasterDataUrl(source: string, size: number, opacity: number): Promise<string> {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => {
      const canvas = document.createElement("canvas");
      canvas.width = size;
      canvas.height = size;
      const context = canvas.getContext("2d");
      if (!context) { reject(new Error("No fue posible preparar el icono de la paleta.")); return; }
      context.fillStyle = "#FFFFFF";
      context.fillRect(0, 0, size, size);
      const scale = Math.min(size / image.naturalWidth, size / image.naturalHeight);
      const width = image.naturalWidth * scale;
      const height = image.naturalHeight * scale;
      context.globalAlpha = opacity;
      context.drawImage(image, (size - width) / 2, (size - height) / 2, width, height);
      resolve(canvas.toDataURL("image/jpeg", 0.94));
    };
    image.onerror = () => reject(new Error("No fue posible cargar el ave de la paleta seleccionada."));
    image.src = source;
  });
}

export async function loadYomDentalLogoDataUrl(palette: PaletteColors): Promise<string> {
 const image=new Image(); image.src="/yomdental-logo.svg";
 await new Promise<void>((resolve,reject)=>{image.onload=()=>resolve();image.onerror=()=>reject(new Error("No fue posible cargar el logotipo de YomDental."));});
 const canvas=document.createElement("canvas");canvas.width=220;canvas.height=220;
 const context=canvas.getContext("2d");if(!context)throw new Error("No fue posible preparar el logotipo de YomDental.");
 context.fillStyle="#FFFFFF";context.fillRect(0,0,220,220);
 const scale=Math.min(204/image.naturalWidth,204/image.naturalHeight),w=image.naturalWidth*scale,h=image.naturalHeight*scale;
 context.drawImage(image,(220-w)/2,(220-h)/2,w,h);return canvas.toDataURL("image/jpeg",.92);
}
export async function loadYomDentalWatermarkDataUrl(palette: PaletteColors): Promise<string> {
 const image=new Image();image.src="/yomdental-logo.svg";
 await new Promise<void>((resolve,reject)=>{image.onload=()=>resolve();image.onerror=()=>reject(new Error("No fue posible cargar la marca de agua YomDental."));});
 const canvas=document.createElement("canvas");canvas.width=400;canvas.height=400;
 const context=canvas.getContext("2d");if(!context)throw new Error("No fue posible preparar la marca de agua YomDental.");
 const scale=Math.min(380/image.naturalWidth,380/image.naturalHeight),w=image.naturalWidth*scale,h=image.naturalHeight*scale;
 context.drawImage(image,(400-w)/2,(400-h)/2,w,h);context.globalCompositeOperation="source-in";
 const gradient=context.createLinearGradient(20,20,380,380);gradient.addColorStop(0,palette.plum);gradient.addColorStop(.55,palette.primary);gradient.addColorStop(1,palette.accent);
 context.fillStyle=gradient;context.fillRect(0,0,400,400);return canvas.toDataURL("image/jpeg", 0.92);
}
export function loadAvisBirdIconDataUrl(source: string): Promise<string> {
  return loadBirdRasterDataUrl(source, 128, 1);
}

export function loadAvisBirdWatermarkDataUrl(source: string): Promise<string> {
  return loadBirdRasterDataUrl(source, 320, 0.075);
}

function ascii(value: string): Uint8Array {
  return new TextEncoder().encode(value);
}

function concatBytes(parts: Uint8Array[]): Uint8Array {
  const total = parts.reduce((sum, part) => sum + part.length, 0);
  const output = new Uint8Array(total);
  let offset = 0;
  for (const part of parts) {
    output.set(part, offset);
    offset += part.length;
  }
  return output;
}

function drawPageFrame(
  pageTitle: string, pageNumber: number, generatedAt: string, palette: PaletteColors,
  reportLabel = "Reporte", hasLogo = false, hasClinicLogo = false, hasPaletteIcon = false,
  hasBirdWatermark = false, hasClinicWatermark = false,
): string {
  const plum = toRgb(palette.plum);
  const primary = toRgb(palette.primary);
  const accent = toRgb(palette.accent);
  const muted = toRgb(palette.muted);
  let output = rectangle(0, 0, PAGE_W, PAGE_H, toRgb(palette.background), null);
  if (hasBirdWatermark) output += "q 250 0 0 250 172 330 cm /Watermark Do Q\n";
  if (hasClinicWatermark) output += "q 225 0 0 225 185 340 cm /ClinicWatermark Do Q\n";
  output += rectangle(27, 27, PAGE_W - 54, PAGE_H - 54, null, plum, 1.15);
  if (hasLogo) output += "q 30 0 0 30 48 778 cm /Logo Do Q\n";
  output += text("AVIS", hasLogo ? 84 : 48, 790, 19, "F2", primary);
  output += text("ANÁLISIS ODONTOLÓGICO INTEGRAL", hasLogo ? 137 : 101, 795, 8, "F2", plum);
  if (hasClinicLogo) output += "q 40 0 0 40 486 773 cm /ClinicLogo Do Q\n";
  if (hasPaletteIcon) output += "q 28 0 0 28 538 778 cm /Bird Do Q\n";
  output += text("Fecha y hora del análisis: " + generatedAt, 300, 778, 7, "F1", muted);
  output += text(pageTitle.toUpperCase(), 48, 750, 12, "F2", primary);
  output += line(48, 738, PAGE_W - 48, 738, accent, 1.25);
  output += text(`AVIS · ${reportLabel} · Página ${pageNumber}`, 48, 58, 7, "F1", muted);
  output += text("Autoría: Dra. Yomira Salgado Martínez · YomDental", 48, 46, 6, "F1", muted);
  output += text("Cirujano Dentista · Especialidad en Ortodoncia · Maestría en Ciencias Odontológicas · Doctorado en Educación", 48, 35, 5.1, "F1", muted);
  return output;
}

function createPdf(input: PhotoReportInput): Uint8Array {
  const photoBytes = base64ToBytes(input.photoDataUrl);
  const logoBytes = input.logoDataUrl ? base64ToBytes(input.logoDataUrl) : null;
  const clinicLogoBytes = input.clinicLogoDataUrl ? base64ToBytes(input.clinicLogoDataUrl) : null;
  const birdBytes = input.birdIconDataUrl ? base64ToBytes(input.birdIconDataUrl) : null;
  const watermarkBytes = input.birdWatermarkDataUrl ? base64ToBytes(input.birdWatermarkDataUrl) : null;
  const clinicWatermarkBytes = input.clinicWatermarkDataUrl ? base64ToBytes(input.clinicWatermarkDataUrl) : null;
  let nextImageObject = 10;
  const logoObjectId = logoBytes ? nextImageObject++ : null;
  const clinicLogoObjectId = clinicLogoBytes ? nextImageObject++ : null;
  const birdObjectId = birdBytes ? nextImageObject++ : null;
  const watermarkObjectId = watermarkBytes ? nextImageObject++ : null;
  const clinicWatermarkObjectId = clinicWatermarkBytes ? nextImageObject++ : null;
  const page1XObjects = [
    "/Im1 7 0 R",
    ...(logoObjectId ? [`/Logo ${logoObjectId} 0 R`] : []),
    ...(clinicLogoObjectId ? [`/ClinicLogo ${clinicLogoObjectId} 0 R`] : []),
    ...(birdObjectId ? [`/Bird ${birdObjectId} 0 R`] : []),
    ...(watermarkObjectId ? [`/Watermark ${watermarkObjectId} 0 R`] : []),
    ...(clinicWatermarkObjectId ? [`/ClinicWatermark ${clinicWatermarkObjectId} 0 R`] : []),
  ].join(" ");
  const page2XObjects = [
    ...(logoObjectId ? [`/Logo ${logoObjectId} 0 R`] : []),
    ...(clinicLogoObjectId ? [`/ClinicLogo ${clinicLogoObjectId} 0 R`] : []),
    ...(birdObjectId ? [`/Bird ${birdObjectId} 0 R`] : []),
    ...(watermarkObjectId ? [`/Watermark ${watermarkObjectId} 0 R`] : []),
  ].join(" ");
  const plum = toRgb(input.palette.plum);
  const mint = toRgb(input.palette.mint);
  const primary = toRgb(input.palette.primary);
  const soft = toRgb(input.palette.soft);
  const muted = toRgb(input.palette.muted);
  const border = toRgb(input.palette.border);
  const generatedAt = input.generatedAt.toLocaleString("es-MX", {
    year: "numeric", month: "long", day: "2-digit", hour: "2-digit", minute: "2-digit",
  });

  // Página 1: fotografía anotada y conclusiones inmediatamente debajo.
  let page1 = drawPageFrame("Imagen y trazado", 1, generatedAt, input.palette, input.reportLabel, Boolean(logoBytes), Boolean(clinicLogoBytes), Boolean(birdBytes), Boolean(watermarkBytes), Boolean(clinicWatermarkBytes));
  page1 += text(input.title, 48, 718, 10.5, "F2", primary);
  page1 += text(input.horizontalGuides ? "Puntos anatómicos y líneas horizontales de referencia" : "Puntos anatómicos trazados sobre la fotografía", 48, 702, 8, "F1", muted);
  page1 += text(`Imagen: ${input.fileName || "Fotografía cargada"} · ${input.photoWidth} × ${input.photoHeight} px`, 48, 687, 7.5, "F1", BLACK);

  const photoBox = { x: 48, y: 313, width: PAGE_W - 96, height: 370 };
  const scale = Math.min(
    photoBox.width / input.photoWidth,
    photoBox.height / input.photoHeight,
  );
  const drawWidth = input.photoWidth * scale;
  const drawHeight = input.photoHeight * scale;
  const drawX = photoBox.x + (photoBox.width - drawWidth) / 2;
  const drawY = photoBox.y + (photoBox.height - drawHeight) / 2;
  page1 += rectangle(photoBox.x, photoBox.y, photoBox.width, photoBox.height, [250, 249, 251], plum, 0.6);
  page1 += `q ${drawWidth.toFixed(2)} 0 0 ${drawHeight.toFixed(2)} ${drawX.toFixed(2)} ${drawY.toFixed(2)} cm /Im1 Do Q\n`;
  page1 += rectangle(drawX, drawY, drawWidth, drawHeight, null, plum, 0.4);

  // Recuadro de conclusiones: fondo menta, borde y título ciruela, texto negro.
  const boxX = 48;
  const boxY = 65;
  const boxW = PAGE_W - 96;
  const boxH = 224;
  page1 += rectangle(boxX, boxY, boxW, boxH, mint, plum, 1.2);
  page1 += text("CONCLUSIONES DEL REPORTE", boxX + 15, boxY + boxH - 23, 10, "F2", plum);
  page1 += line(boxX + 15, boxY + boxH - 33, boxX + boxW - 15, boxY + boxH - 33, plum, 0.55);

  const conclusionLines: string[] = [];
  for (const conclusion of input.conclusions) {
    const wrapped = wrapWords(conclusion, 112);
    conclusionLines.push(...wrapped);
    conclusionLines.push("");
  }
  if (!conclusionLines.length) conclusionLines.push("No hay conclusiones automáticas disponibles.");
  const maxLines = 15;
  const visibleLines = conclusionLines.slice(0, maxLines);
  const fontSize = conclusionLines.length > maxLines ? 7.1 : 7.8;
  let conclusionY = boxY + boxH - 49;
  for (const value of visibleLines) {
    if (value) {
      page1 += text(value, boxX + 15, conclusionY, fontSize, "F1", BLACK);
    }
    conclusionY -= 10.1;
  }
  if (conclusionLines.length > maxLines) {
    page1 += text("Las conclusiones restantes se incluyen en la página de resultados.", boxX + 15, boxY + 13, 7, "F1", BLACK);
  }

  // Página 2: tabla completa de mediciones y registro complementario.
  let page2 = drawPageFrame("Resultados y mediciones", 2, generatedAt, input.palette, input.reportLabel, Boolean(logoBytes), Boolean(clinicLogoBytes), Boolean(birdBytes), Boolean(watermarkBytes), false);
  page2 += text(input.title, 48, 732, 10, "F2", primary);
  page2 += text(`Estado: ${input.status} · Unidad de distancia: píxeles relativos (px)`, 48, 716, 8, "F1", BLACK);
  page2 += text("Las medidas fotográficas son relativas a la imagen y no equivalen a milímetros.", 48, 702, 7.5, "F1", muted);

  const tableX = 48;
  const tableW = PAGE_W - 96;
  const columns = [tableX + 9, tableX + 177, tableX + 270];
  const maxChars = [31, 17, 51];
  const widths = [160, 86, tableW - 246];
  let y = 678;
  page2 += rectangle(tableX, y - 22, tableW, 22, soft, plum, 0.75);
  page2 += text("MEDICIÓN", columns[0], y - 14, 7.2, "F2", plum);
  page2 += text("RESULTADO", columns[1], y - 14, 7.2, "F2", plum);
  page2 += text("REFERENCIA / COMPARACIÓN", columns[2], y - 14, 7.2, "F2", plum);
  y -= 22;

  for (const row of input.results) {
    const cells = [
      wrapWords(row.label, maxChars[0]),
      wrapWords(row.value, maxChars[1]),
      wrapWords(row.reference || "—", maxChars[2]),
    ];
    const lineCount = Math.max(...cells.map((cell) => cell.length));
    const rowHeight = Math.max(21, lineCount * 9 + 8);
    if (y - rowHeight < 104) break;
    page2 += line(tableX, y - rowHeight, tableX + tableW, y - rowHeight, border, 0.35);
    cells.forEach((cellLines, columnIndex) => {
      cellLines.forEach((lineValue, lineIndex) => {
        page2 += text(
          lineValue,
          columns[columnIndex],
          y - 12 - lineIndex * 9,
          7.2,
          columnIndex === 1 ? "F2" : "F1",
          BLACK,
        );
      });
    });
    y -= rowHeight;
  }
  page2 += line(tableX, y, tableX + tableW, y, plum, 0.65);
  y -= 17;

  const notes: Array<[string, string]> = [
    ["Criterios visuales", Object.entries(input.visualAssessment)
      .filter(([, value]) => value && value !== "Sin evaluar")
      .map(([label, value]) => `${label}: ${value}`).join("; ")],
    ["Observaciones", input.observations],
    ["Conclusión profesional", input.professionalConclusion],
  ];
  for (const [label, value] of notes) {
    if (!value.trim() || y < 72) continue;
    page2 += text(label.toUpperCase(), tableX, y, 7.8, "F2", plum);
    y -= 12;
    for (const lineValue of wrapWords(value, 112)) {
      if (y < 58) break;
      page2 += text(lineValue, tableX, y, 7.3, "F1", BLACK);
      y -= 10;
    }
    y -= 8;
  }

  const imageObject = concatBytes([
    ascii(`7 0 obj\n<< /Type /XObject /Subtype /Image /Width ${input.photoWidth} /Height ${input.photoHeight} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length ${photoBytes.length} >>\nstream\n`),
    photoBytes,
    ascii("\nendstream\nendobj\n"),
  ]);
  const objects: Uint8Array[] = [
    ascii("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"),
    ascii("2 0 obj\n<< /Type /Pages /Kids [3 0 R 4 0 R] /Count 2 >>\nendobj\n"),
    ascii("3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595.28 841.89] /Resources << /Font << /F1 5 0 R /F2 6 0 R >> /XObject << " + page1XObjects + " >> >> /Contents 8 0 R >>\nendobj\n"),
    ascii("4 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595.28 841.89] /Resources << /Font << /F1 5 0 R /F2 6 0 R >> /XObject << " + page2XObjects + " >> >> /Contents 9 0 R >>\nendobj\n"),
    ascii("5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>\nendobj\n"),
    ascii("6 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>\nendobj\n"),
    imageObject,
    concatBytes([ascii(`8 0 obj\n<< /Length ${ascii(page1).length} >>\nstream\n`), ascii(page1), ascii("\nendstream\nendobj\n")]),
    concatBytes([ascii(`9 0 obj\n<< /Length ${ascii(page2).length} >>\nstream\n`), ascii(page2), ascii("\nendstream\nendobj\n")]),
  ];

  const appendImageObject = (objectId: number, width: number, height: number, bytes: Uint8Array) => {
    objects.push(concatBytes([
      ascii(`${objectId} 0 obj\n<< /Type /XObject /Subtype /Image /Width ${width} /Height ${height} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length ${bytes.length} >>\nstream\n`),
      bytes,
      ascii("\nendstream\nendobj\n"),
    ]));
  };
  if (logoBytes && logoObjectId) appendImageObject(logoObjectId, 96, 96, logoBytes);
  if (clinicLogoBytes && clinicLogoObjectId) appendImageObject(clinicLogoObjectId, 220, 220, clinicLogoBytes);
  if (birdBytes && birdObjectId) appendImageObject(birdObjectId, 128, 128, birdBytes);
  if (watermarkBytes && watermarkObjectId) appendImageObject(watermarkObjectId, 320, 320, watermarkBytes);
  if (clinicWatermarkBytes && clinicWatermarkObjectId) appendImageObject(clinicWatermarkObjectId, 400, 400, clinicWatermarkBytes);

  const chunks: Uint8Array[] = [ascii("%PDF-1.4\n")];
  const offsets: number[] = [0];
  let byteOffset = chunks[0].length;
  objects.forEach((objectBytes) => {
    offsets.push(byteOffset);
    chunks.push(objectBytes);
    byteOffset += objectBytes.length;
  });
  const xrefOffset = byteOffset;
  let xref = `xref\n0 ${objects.length + 1}\n0000000000 65535 f \n`;
  for (let index = 1; index < offsets.length; index += 1) {
    xref += offsets[index].toString().padStart(10, "0") + " 00000 n \n";
  }
  xref += `trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xrefOffset}\n%%EOF`;
  chunks.push(ascii(xref));
  return concatBytes(chunks);
}

export function buildPhotoReportPdf(input: PhotoReportInput): Uint8Array {
  return createPdf(input);
}
