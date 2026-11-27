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

/**
 * Eight bird-derived swatches per palette. The semantic surface/text tokens
 * alias background/plum to preserve compatibility with existing UI and reports.
 */
export const AVIS_SWATCH_KEYS = [
  "plum", "primary", "accent", "mint",
  "background", "soft", "border", "muted",
] as const satisfies readonly (keyof PaletteColors)[];

export type AvisPalette = {
  id: PaletteId;
  name: string;
  bird: string;
  colors: PaletteColors;
};

export const AVIS_PALETTES: AvisPalette[] = [
  {
    id: "buho_real",
    name: "Búho real",
    bird: "🦉",
    colors: {
      plum: "#49372D", primary: "#795A42", accent: "#A98462", mint: "#77746B",
      background: "#F8F4EB", surface: "#F8F4EB", soft: "#D1B895", border: "#B6A18D",
      text: "#49372D", muted: "#34383A",
    },
  },
  {
    id: "colibri",
    name: "Colibrí",
    bird: "🐦",
    colors: {
      plum: "#263C50", primary: "#087F75", accent: "#C34C8A", mint: "#14A6A0",
      background: "#F4F9F7", surface: "#F4F9F7", soft: "#2674B8", border: "#7B4CA0",
      text: "#263C50", muted: "#D5B94B",
    },
  },
  {
    id: "guacamayo_azul",
    name: "Guacamayo azul",
    bird: "🦜",
    colors: {
      plum: "#173B63", primary: "#1769AA", accent: "#E9C72E", mint: "#168B55",
      background: "#F4F8FB", surface: "#F4F8FB", soft: "#F07A24", border: "#B9D8E8",
      text: "#173B63", muted: "#D9272E",
    },
  },
  {
    id: "guacamaya_roja",
    name: "Guacamaya roja",
    bird: "🦜",
    colors: {
      plum: "#38262C", primary: "#D9272E", accent: "#E9C72E", mint: "#168B55",
      background: "#FBF5EF", surface: "#FBF5EF", soft: "#F07A24", border: "#DCC5B4",
      text: "#38262C", muted: "#1769AA",
    },
  },
  {
    id: "quetzal",
    name: "Quetzal",
    bird: "🪶",
    colors: {
      plum: "#183D35", primary: "#087E70", accent: "#C8463F", mint: "#159A78",
      background: "#F5F9F4", surface: "#F5F9F4", soft: "#42B9A6", border: "#A58A36",
      text: "#183D35", muted: "#2764B4",
    },
  },
  {
    id: "faisan",
    name: "Faisán",
    bird: "🐦",
    colors: {
      plum: "#49352D", primary: "#A45136", accent: "#D2A12F", mint: "#79513D",
      background: "#FAF6EF", surface: "#FAF6EF", soft: "#D8C3A7", border: "#B66A43",
      text: "#49352D", muted: "#E8DDC9",
    },
  },
  {
    id: "ninfa",
    name: "Ninfa",
    bird: "🐦",
    colors: {
      plum: "#3B4146", primary: "#81888D", accent: "#E27C45", mint: "#E8CA56",
      background: "#FAF9F3", surface: "#FAF9F3", soft: "#EEECE3", border: "#D2D0C6",
      text: "#3B4146", muted: "#F5F1E8",
    },
  },
  {
    id: "pavo_real",
    name: "Pavo real",
    bird: "🦚",
    colors: {
      plum: "#23304F", primary: "#087E80", accent: "#A58A36", mint: "#159A78",
      background: "#F4F8F8", surface: "#F4F8F8", soft: "#176C9B", border: "#4B347C",
      text: "#23304F", muted: "#2764B4",
    },
  },
  {
    id: "tucan",
    name: "Tucán",
    bird: "🐦",
    colors: {
      plum: "#202124", primary: "#F0C928", accent: "#E97824", mint: "#D94B25",
      background: "#FBF8F0", surface: "#FBF8F0", soft: "#F5F1E8", border: "#454545",
      text: "#202124", muted: "#B8B8B8",
    },
  },
  {
    id: "agapornis",
    name: "Agapornis",
    bird: "🦜",
    colors: {
      plum: "#713B68", primary: "#328C55", accent: "#F2A16D", mint: "#35B9B0",
      background: "#FFFCF4", surface: "#FFFCF4", soft: "#277DA1", border: "#B8A0D4",
      text: "#713B68", muted: "#E8D84A",
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
