import type { PhotoReportInput } from "./pdfReport";
import type { PaletteColors } from "./themePalettes";

const WIDTH = 1240;
const MARGIN = 96;
const CONTENT_WIDTH = WIDTH - MARGIN * 2;
const MIN_PAGE_HEIGHT = 1754;
const BLACK = "#141414";

function loadImage(source: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve(image);
    image.onerror = () => reject(new Error("No fue posible preparar la fotografía para exportarla."));
    image.src = source;
  });
}

function wrapText(
  context: CanvasRenderingContext2D,
  value: string,
  maxWidth: number,
  font: string,
): string[] {
  context.font = font;
  const words = value.trim().split(/\s+/).filter(Boolean);
  if (!words.length) return [""];
  const lines: string[] = [];
  let current = "";
  for (const word of words) {
    const candidate = current ? current + " " + word : word;
    if (current && context.measureText(candidate).width > maxWidth) {
      lines.push(current);
      current = word;
    } else {
      current = candidate;
    }
  }
  if (current) lines.push(current);
  return lines;
}

function fillPage(context: CanvasRenderingContext2D, height: number, pageTitle: string, pageNumber: number, date: string, palette: PaletteColors) {
  const plum = palette.plum;
  const primary = palette.primary;
  const accent = palette.accent;
  const muted = palette.muted;
  context.fillStyle = "#FFFFFF";
  context.fillRect(0, 0, WIDTH, height);
  context.strokeStyle = plum;
  context.lineWidth = 2;
  context.strokeRect(54, 54, WIDTH - 108, height - 108);
  context.fillStyle = primary;
  context.font = "bold 44px Arial, sans-serif";
  context.textBaseline = "top";
  context.fillText("AVIS", MARGIN, 76);
  context.font = "bold 17px Arial, sans-serif";
  context.fillText("ANÁLISIS ODONTOLÓGICO INTEGRAL", MARGIN + 125, 91);
  context.fillStyle = muted;
  context.font = "15px Arial, sans-serif";
  context.textAlign = "right";
  context.fillText(date, WIDTH - MARGIN, 91);
  context.textAlign = "left";
  context.fillStyle = primary;
  context.font = "bold 25px Arial, sans-serif";
  context.fillText(pageTitle.toUpperCase(), MARGIN, 142);
  context.strokeStyle = accent;
  context.lineWidth = 1.5;
  context.beginPath();
  context.moveTo(MARGIN, 187);
  context.lineTo(WIDTH - MARGIN, 187);
  context.stroke();
  context.fillStyle = muted;
  context.font = "14px Arial, sans-serif";
  context.fillText(`AVIS · Reporte fotográfico · Página ${pageNumber}`, MARGIN, height - 76);
}

function drawWrapped(
  context: CanvasRenderingContext2D,
  value: string,
  x: number,
  y: number,
  maxWidth: number,
  font: string,
  color: string,
  lineHeight: number,
): number {
  const lines = wrapText(context, value, maxWidth, font);
  context.font = font;
  context.fillStyle = color;
  context.textAlign = "left";
  context.textBaseline = "top";
  for (const current of lines) {
    context.fillText(current, x, y);
    y += lineHeight;
  }
  return y;
}

function drawPageOne(input: PhotoReportInput, photo: HTMLImageElement, date: string): HTMLCanvasElement {
  const plum = input.palette.plum;
  const primary = input.palette.primary;
  const accent = input.palette.accent;
  const mint = input.palette.mint;
  const muted = input.palette.muted;
  const soft = input.palette.soft;
  const conclusionFont = "16px Arial, sans-serif";
  const conclusionLines = input.conclusions.flatMap((item) =>
    wrapText(document.createElement("canvas").getContext("2d")!, item, CONTENT_WIDTH - 92, conclusionFont),
  );
  const conclusionHeight = Math.max(170, 104 + conclusionLines.length * 25 + input.conclusions.length * 7);
  const pageHeight = Math.max(MIN_PAGE_HEIGHT, 1080 + conclusionHeight + 100);
  const canvas = document.createElement("canvas");
  canvas.width = WIDTH;
  canvas.height = pageHeight;
  const context = canvas.getContext("2d");
  if (!context) throw new Error("No fue posible generar la imagen del reporte.");
  fillPage(context, pageHeight, "Registro fotográfico", 1, date, input.palette);

  context.fillStyle = BLACK;
  context.font = "bold 22px Arial, sans-serif";
  context.textBaseline = "top";
  context.fillText(input.title, MARGIN, 214);
  context.fillStyle = muted;
  context.font = "15px Arial, sans-serif";
  context.fillText(
    `Imagen: ${input.fileName || "Fotografía cargada"} · ${input.photoWidth} × ${input.photoHeight} px`,
    MARGIN,
    248,
  );

  const photoBox = { x: MARGIN, y: 286, width: CONTENT_WIDTH, height: 735 };
  context.fillStyle = soft;
  context.fillRect(photoBox.x, photoBox.y, photoBox.width, photoBox.height);
  context.strokeStyle = plum;
  context.lineWidth = 1.4;
  context.strokeRect(photoBox.x, photoBox.y, photoBox.width, photoBox.height);
  const scale = Math.min(
    (photoBox.width - 28) / photo.naturalWidth,
    (photoBox.height - 28) / photo.naturalHeight,
  );
  const photoWidth = photo.naturalWidth * scale;
  const photoHeight = photo.naturalHeight * scale;
  const photoX = photoBox.x + (photoBox.width - photoWidth) / 2;
  const photoY = photoBox.y + (photoBox.height - photoHeight) / 2;
  context.drawImage(photo, photoX, photoY, photoWidth, photoHeight);

  const boxY = 1060;
  const boxHeight = conclusionHeight;
  context.fillStyle = mint;
  context.fillRect(MARGIN, boxY, CONTENT_WIDTH, boxHeight);
  context.strokeStyle = plum;
  context.lineWidth = 2.5;
  context.strokeRect(MARGIN, boxY, CONTENT_WIDTH, boxHeight);
  context.fillStyle = plum;
  context.font = "bold 21px Arial, sans-serif";
  context.fillText("CONCLUSIONES DEL REPORTE", MARGIN + 30, boxY + 24);
  context.strokeStyle = plum;
  context.lineWidth = 1;
  context.beginPath();
  context.moveTo(MARGIN + 30, boxY + 61);
  context.lineTo(WIDTH - MARGIN - 30, boxY + 61);
  context.stroke();

  let y = boxY + 82;
  for (const conclusion of input.conclusions) {
    context.fillStyle = plum;
    context.beginPath();
    context.arc(MARGIN + 36, y + 9, 3.5, 0, Math.PI * 2);
    context.fill();
    y = drawWrapped(context, conclusion, MARGIN + 52, y, CONTENT_WIDTH - 90, conclusionFont, BLACK, 25) + 7;
  }
  return canvas;
}

function drawPageTwo(input: PhotoReportInput, date: string): HTMLCanvasElement {
  const plum = input.palette.plum;
  const primary = input.palette.primary;
  const accent = input.palette.accent;
  const muted = input.palette.muted;
  const soft = input.palette.soft;
  const border = input.palette.border;
  const measureCanvas = document.createElement("canvas");
  const measureContext = measureCanvas.getContext("2d");
  if (!measureContext) throw new Error("No fue posible preparar la tabla de resultados.");

  const labelFont = "15px Arial, sans-serif";
  const valueFont = "bold 15px Arial, sans-serif";
  const referenceFont = "14px Arial, sans-serif";
  const tableRows = input.results.map((row) => {
    const label = wrapText(measureContext, row.label, 290, labelFont);
    const value = wrapText(measureContext, row.value, 150, valueFont);
    const reference = wrapText(measureContext, row.reference || "—", 475, referenceFont);
    const lines = Math.max(label.length, value.length, reference.length);
    return { row, label, value, reference, height: Math.max(50, lines * 21 + 24) };
  });

  const notes = [
    ["CRITERIOS VISUALES", Object.entries(input.visualAssessment)
      .filter(([, value]) => value && value !== "Sin evaluar")
      .map(([label, value]) => `${label}: ${value}`).join("; ")],
    ["OBSERVACIONES", input.observations],
    ["CONCLUSIÓN PROFESIONAL", input.professionalConclusion],
  ].filter((item) => item[1].trim());

  let requiredHeight = 340 + tableRows.reduce((sum, item) => sum + item.height, 0);
  for (const [, value] of notes) {
    requiredHeight += wrapText(measureContext, value, CONTENT_WIDTH, "15px Arial, sans-serif").length * 23 + 56;
  }
  const pageHeight = Math.max(MIN_PAGE_HEIGHT, requiredHeight + 150);
  const canvas = document.createElement("canvas");
  canvas.width = WIDTH;
  canvas.height = pageHeight;
  const context = canvas.getContext("2d");
  if (!context) throw new Error("No fue posible generar la segunda página del reporte.");
  fillPage(context, pageHeight, "Resultados y mediciones", 2, date, input.palette);

  context.fillStyle = BLACK;
  context.font = "bold 21px Arial, sans-serif";
  context.textBaseline = "top";
  context.fillText(input.title, MARGIN, 214);
  context.font = "15px Arial, sans-serif";
  context.fillText(`Estado: ${input.status} · Unidad de distancia: píxeles relativos (px)`, MARGIN, 250);
  context.fillStyle = muted;
  context.fillText("Las medidas fotográficas son relativas a la imagen y no equivalen a milímetros.", MARGIN, 278);

  const tableX = MARGIN;
  const tableWidth = CONTENT_WIDTH;
  const colX = [tableX + 18, tableX + 350, tableX + 530];
  let y = 320;
  context.fillStyle = soft;
  context.fillRect(tableX, y, tableWidth, 43);
  context.strokeStyle = plum;
  context.lineWidth = 1.5;
  context.strokeRect(tableX, y, tableWidth, 43);
  context.fillStyle = primary;
  context.font = "bold 14px Arial, sans-serif";
  context.fillText("MEDICIÓN", colX[0], y + 13);
  context.fillText("RESULTADO", colX[1], y + 13);
  context.fillText("REFERENCIA / COMPARACIÓN", colX[2], y + 13);
  y += 43;

  for (const item of tableRows) {
    const rowY = y;
    context.strokeStyle = border;
    context.lineWidth = 1;
    context.beginPath();
    context.moveTo(tableX, rowY + item.height);
    context.lineTo(tableX + tableWidth, rowY + item.height);
    context.stroke();

    context.font = labelFont;
    context.fillStyle = BLACK;
    item.label.forEach((value, index) => context.fillText(value, colX[0], rowY + 13 + index * 21));
    context.font = valueFont;
    item.value.forEach((value, index) => context.fillText(value, colX[1], rowY + 13 + index * 21));
    context.font = referenceFont;
    item.reference.forEach((value, index) => context.fillText(value, colX[2], rowY + 13 + index * 21));
    y += item.height;
  }

  y += 34;
  for (const [heading, value] of notes) {
    context.fillStyle = primary;
    context.font = "bold 16px Arial, sans-serif";
    context.fillText(heading, MARGIN, y);
    y += 28;
    y = drawWrapped(context, value, MARGIN, y, CONTENT_WIDTH, "15px Arial, sans-serif", BLACK, 23);
    y += 24;
  }
  context.fillStyle = muted;
  context.font = "13px Arial, sans-serif";
  context.fillText(
    "Herramienta de apoyo para medición y registro. No sustituye la valoración profesional.",
    MARGIN,
    Math.min(pageHeight - 130, y + 18),
  );
  return canvas;
}

export async function renderPhotoReportImage(
  input: PhotoReportInput,
  format: "png" | "jpeg",
): Promise<Blob> {
  const photo = await loadImage(input.photoDataUrl);
  const date = input.generatedAt.toLocaleString("es-MX", {
    year: "numeric",
    month: "long",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
  const firstPage = drawPageOne(input, photo, date);
  const secondPage = drawPageTwo(input, date);
  const gap = 28;

  const combined = document.createElement("canvas");
  combined.width = WIDTH;
  combined.height = firstPage.height + gap + secondPage.height;
  const context = combined.getContext("2d");
  if (!context) throw new Error("No fue posible componer el reporte como imagen.");
  context.fillStyle = input.palette.background;
  context.fillRect(0, 0, combined.width, combined.height);
  context.drawImage(firstPage, 0, 0);
  context.fillStyle = input.palette.plum;
  context.fillRect(0, firstPage.height, WIDTH, gap);
  context.drawImage(secondPage, 0, firstPage.height + gap);

  const mimeType = format === "png" ? "image/png" : "image/jpeg";
  const blob = await new Promise<Blob>((resolve, reject) => {
    combined.toBlob(
      (value) => value ? resolve(value) : reject(new Error("El navegador no pudo codificar el reporte en el formato seleccionado.")),
      mimeType,
      format === "jpeg" ? 0.94 : undefined,
    );
  });
  return blob;
}
