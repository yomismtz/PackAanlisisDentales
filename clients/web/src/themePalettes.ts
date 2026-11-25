export type PaletteId =
  | "buho_real"
  | "colibri"
  | "guacamayo_azul"
  | "guacamaya_roja"
  | "quetzal"
  | "faisan"
  | "ninfa"
  | "pavo_real"
  | "tucan"
  | "agapornis";

export type PaletteColors = {
  plum: string;
  primary: string;
  accent: string;
  mint: string;
  background: string;
  surface: string;
  soft: string;
  border: string;
  text: string;
  muted: string;
};

export type AvisPalette = {
  id: PaletteId;
  name: string;
  bird: string;
  audioFile: string;
  colors: PaletteColors;
};

export const AVIS_PALETTES: AvisPalette[] = [
  {
    id: "buho_real",
    name: "Búho real",
    bird: "🦉",
    audioFile: "buho_real.mp3",
    colors: {
      plum: "#3C3451", primary: "#756B8C", accent: "#C39B67", mint: "#E6E0D1",
      background: "#F7F5F0", surface: "#FFFFFF", soft: "#F0ECF5", border: "#D9D1DE",
      text: "#16131B", muted: "#706B75",
    },
  },
  {
    id: "colibri",
    name: "Colibrí",
    bird: "🐦",
    audioFile: "colibri.mp3",
    colors: {
      plum: "#48263F", primary: "#6D45A6", accent: "#22B8B0", mint: "#C8F0E2",
      background: "#F7F7FA", surface: "#FFFFFF", soft: "#F1EBF2", border: "#D8C7D7",
      text: "#141414", muted: "#6D6872",
    },
  },
  {
    id: "guacamayo_azul",
    name: "Guacamayo azul",
    bird: "🦜",
    audioFile: "guacamayo_azul.mp3",
    colors: {
      plum: "#263A66", primary: "#2478B7", accent: "#27B7A5", mint: "#C7EEE3",
      background: "#F3F8FC", surface: "#FFFFFF", soft: "#EAF3F8", border: "#C9DDEB",
      text: "#142333", muted: "#627789",
    },
  },
  {
    id: "guacamaya_roja",
    name: "Guacamaya roja",
    bird: "🦜",
    audioFile: "guacamaya_roja.mp3",
    colors: {
      plum: "#57263A", primary: "#D33E42", accent: "#D9A72D", mint: "#F9E6B7",
      background: "#FBF6F1", surface: "#FFFFFF", soft: "#F7EBDC", border: "#EAC9AD",
      text: "#24191D", muted: "#77665F",
    },
  },
  {
    id: "quetzal",
    name: "Quetzal",
    bird: "🪶",
    audioFile: "quetzal.mp3",
    colors: {
      plum: "#173E3A", primary: "#1D775D", accent: "#22A9A7", mint: "#C9EDE3",
      background: "#F4F8F5", surface: "#FFFFFF", soft: "#E6F3EE", border: "#BFDCCF",
      text: "#172B28", muted: "#637772",
    },
  },
  {
    id: "faisan",
    name: "Faisán",
    bird: "🐓",
    audioFile: "faisan.mp3",
    colors: {
      plum: "#55362C", primary: "#A36A3F", accent: "#C4A04D", mint: "#E8E2C8",
      background: "#FAF7F1", surface: "#FFFFFF", soft: "#F3EDE2", border: "#DDD0BA",
      text: "#241D18", muted: "#756A5D",
    },
  },
  {
    id: "ninfa",
    name: "Ninfa",
    bird: "🐦",
    audioFile: "ninfa.mp3",
    colors: {
      plum: "#47434B", primary: "#96949D", accent: "#E4BD55", mint: "#E6EDE1",
      background: "#F7F7F5", surface: "#FFFFFF", soft: "#F0F0EB", border: "#D8D8D1",
      text: "#201F22", muted: "#77747A",
    },
  },
  {
    id: "pavo_real",
    name: "Pavo real",
    bird: "🦚",
    audioFile: "pavo_real.mp3",
    colors: {
      plum: "#352A65", primary: "#306FA6", accent: "#168C85", mint: "#D6EEE8",
      background: "#F4F7FB", surface: "#FFFFFF", soft: "#EAEFF8", border: "#C9D5E8",
      text: "#19182B", muted: "#66677D",
    },
  },
  {
    id: "tucan",
    name: "Tucán",
    bird: "🐦",
    audioFile: "tucan.mp3",
    colors: {
      plum: "#33303A", primary: "#E37A2C", accent: "#D6B83F", mint: "#D5EAE2",
      background: "#F8F6F2", surface: "#FFFFFF", soft: "#F2ECE5", border: "#DCD0C2",
      text: "#1C1A1D", muted: "#716A63",
    },
  },
  {
    id: "agapornis",
    name: "Agapornis",
    bird: "🦜",
    audioFile: "agapornis.mp3",
    colors: {
      plum: "#4D2939", primary: "#B85C4D", accent: "#85B846", mint: "#E5F0C8",
      background: "#FAF8F2", surface: "#FFFFFF", soft: "#F3F5E7", border: "#D5DFBE",
      text: "#201B1D", muted: "#706A62",
    },
  },
];

export function getAvisPalette(id: string): AvisPalette {
  return AVIS_PALETTES.find((palette) => palette.id === id) ?? AVIS_PALETTES[1];
}

export function applyAvisPalette(palette: AvisPalette): void {
  const root = document.documentElement;
  const variables: Record<string, string> = {
    "--avis-plum": palette.colors.plum,
    "--avis-primary": palette.colors.primary,
    "--avis-accent": palette.colors.accent,
    "--avis-mint": palette.colors.mint,
    "--avis-background": palette.colors.background,
    "--avis-surface": palette.colors.surface,
    "--avis-soft": palette.colors.soft,
    "--avis-border": palette.colors.border,
    "--avis-text": palette.colors.text,
    "--avis-muted": palette.colors.muted,
  };
  Object.entries(variables).forEach(([name, value]) => root.style.setProperty(name, value));
}
