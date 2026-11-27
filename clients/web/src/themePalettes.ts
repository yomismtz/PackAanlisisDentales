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
 * Eight visible bird-derived swatches are defined per palette.
 * The legacy semantic tokens surface/text alias background/plum so that
 * existing report and interface consumers remain compatible.
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
      plum: "#302923", primary: "#805A43", accent: "#D58B31", mint: "#C7A77C",
      background: "#F8F4EB", surface: "#F8F4EB", soft: "#ECE2D2", border: "#CFB999",
      text: "#302923", muted: "#75695C",
    },
  },
  {
    id: "colibri",
    name: "Colibrí",
    bird: "🐦",
    colors: {
      plum: "#252A3A", primary: "#16816D", accent: "#C94B92", mint: "#34BDB4",
      background: "#F4F9F7", surface: "#F4F9F7", soft: "#E3F1EC", border: "#BFDCD4",
      text: "#252A3A", muted: "#63766F",
    },
  },
  {
    id: "guacamayo_azul",
    name: "Guacamayo azul",
    bird: "🦜",
    colors: {
      plum: "#1E3556", primary: "#176FA8", accent: "#E8BE31", mint: "#48B7A1",
      background: "#F4F8FB", surface: "#F4F8FB", soft: "#E4EFF6", border: "#BDD1E0",
      text: "#1E3556", muted: "#60778B",
    },
  },
  {
    id: "guacamaya_roja",
    name: "Guacamaya roja",
    bird: "🦜",
    colors: {
      plum: "#38262C", primary: "#D43B34", accent: "#E9B72F", mint: "#2784A2",
      background: "#FBF5EF", surface: "#FBF5EF", soft: "#F3E4D7", border: "#DCC5B4",
      text: "#38262C", muted: "#77665F",
    },
  },
  {
    id: "quetzal",
    name: "Quetzal",
    bird: "🪶",
    colors: {
      plum: "#183D35", primary: "#168364", accent: "#C8463F", mint: "#42B9A6",
      background: "#F5F9F4", surface: "#F5F9F4", soft: "#E4F1E7", border: "#C8B26D",
      text: "#183D35", muted: "#66796F",
    },
  },
  {
    id: "faisan",
    name: "Faisán",
    bird: "🐦",
    colors: {
      plum: "#21343B", primary: "#A45136", accent: "#D2A12F", mint: "#277B73",
      background: "#FAF6EF", surface: "#FAF6EF", soft: "#F0E6D6", border: "#D8C3A7",
      text: "#21343B", muted: "#74675E",
    },
  },
  {
    id: "ninfa",
    name: "Ninfa",
    bird: "🐦",
    colors: {
      plum: "#3B4146", primary: "#81888D", accent: "#E27C45", mint: "#E8CA56",
      background: "#FAF9F3", surface: "#FAF9F3", soft: "#EEECE3", border: "#D2D0C6",
      text: "#3B4146", muted: "#74777B",
    },
  },
  {
    id: "pavo_real",
    name: "Pavo real",
    bird: "🦚",
    colors: {
      plum: "#23304F", primary: "#176C83", accent: "#B58B34", mint: "#25946F",
      background: "#F4F8F8", surface: "#F4F8F8", soft: "#E3F0ED", border: "#BBD5CF",
      text: "#23304F", muted: "#677985",
    },
  },
  {
    id: "tucan",
    name: "Tucán",
    bird: "🐦",
    colors: {
      plum: "#202328", primary: "#323D43", accent: "#EF8A28", mint: "#E8C638",
      background: "#FBF8F0", surface: "#FBF8F0", soft: "#EEE8DA", border: "#CEC7B7",
      text: "#202328", muted: "#76746E",
    },
  },
  {
    id: "agapornis",
    name: "Agapornis",
    bird: "🦜",
    colors: {
      plum: "#5D3B62", primary: "#62A54D", accent: "#EE927A", mint: "#41B9B0",
      background: "#FFFCF4", surface: "#FFFCF4", soft: "#BBA6D2", border: "#E3C65A",
      text: "#5D3B62", muted: "#4687B6",
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
