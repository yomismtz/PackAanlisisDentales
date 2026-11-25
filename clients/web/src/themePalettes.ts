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
  id: "colibri" | "agapornis" | "quetzal" | "guacamaya";
  name: string;
  bird: string;
  colors: PaletteColors;
};

export const AVIS_PALETTES: AvisPalette[] = [
  {
    id: "colibri",
    name: "Colibrí",
    bird: "🐦",
    colors: {
      plum: "#48263F",
      primary: "#6D45A6",
      accent: "#22B8B0",
      mint: "#C8F0E2",
      background: "#F7F7FA",
      surface: "#FFFFFF",
      soft: "#F1EBF2",
      border: "#D8C7D7",
      text: "#141414",
      muted: "#6D6872",
    },
  },
  {
    id: "agapornis",
    name: "Agapornis",
    bird: "🦜",
    colors: {
      plum: "#4D2939",
      primary: "#B85C4D",
      accent: "#85B846",
      mint: "#E5F0C8",
      background: "#FAF8F2",
      surface: "#FFFFFF",
      soft: "#F3F5E7",
      border: "#D5DFBE",
      text: "#201B1D",
      muted: "#706A62",
    },
  },
  {
    id: "quetzal",
    name: "Quetzal",
    bird: "🪶",
    colors: {
      plum: "#173E3A",
      primary: "#1D775D",
      accent: "#22A9A7",
      mint: "#C9EDE3",
      background: "#F4F8F5",
      surface: "#FFFFFF",
      soft: "#E6F3EE",
      border: "#BFDCCF",
      text: "#172B28",
      muted: "#637772",
    },
  },
  {
    id: "guacamaya",
    name: "Guacamaya",
    bird: "🦜",
    colors: {
      plum: "#57263A",
      primary: "#D33E42",
      accent: "#D9A72D",
      mint: "#F9E6B7",
      background: "#FBF6F1",
      surface: "#FFFFFF",
      soft: "#F7EBDC",
      border: "#EAC9AD",
      text: "#24191D",
      muted: "#77665F",
    },
  },
];

export function getAvisPalette(id: string): AvisPalette {
  return AVIS_PALETTES.find((palette) => palette.id === id) ?? AVIS_PALETTES[0];
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
