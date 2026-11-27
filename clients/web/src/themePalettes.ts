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
  | "agapornis"
  | "colorin_siete_colores"
  | "flamenco"
  | "tangara_paraiso";

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

export type PaletteSwatches = readonly [
  string, string, string, string, string, string, string, string
];

export type AvisPalette = {
  id: PaletteId;
  name: string;
  bird: string;
  birdImage: string;
  clinicLogoImage: string;
  /** Eight distinctive colors inspired by this bird's plumage and markings. */
  swatches: PaletteSwatches;
  /** Accessible semantic colors used by the interface and reports. */
  colors: PaletteColors;
};

export const AVIS_PALETTES: AvisPalette[] = [
  {
    id: "buho_real",
    name: "Búho real",
    bird: "🦉",
    birdImage: "/palette-birds/Búho real sobre rama con hojas.png",
    clinicLogoImage: "/palette-logos/Logo YOM Dental en tonos búho.png",
    swatches: ["#49372D", "#795A42", "#D58B31", "#C7A77C", "#F8F4EB", "#D1B895", "#B6A18D", "#34383A"],
    colors: {
      plum: "#49372D", primary: "#795A42", accent: "#D58B31", mint: "#E9DDC8",
      background: "#F8F4EB", surface: "#FFFFFF", soft: "#ECE2D2", border: "#CFB999",
      text: "#302923", muted: "#75695C",
    },
  },
  {
    id: "colibri",
    name: "Colibrí",
    bird: "🐦",
    birdImage: "/palette-birds/Colibrí vectorial de colores vibrantes.png",
    clinicLogoImage: "/palette-logos/Logo dental Yom en paleta Colibrí (2).png",
    swatches: ["#263C50", "#087F75", "#14A6A0", "#2674B8", "#C34C8A", "#D5B94B", "#7B4CA0", "#E2F2EB"],
    colors: {
      plum: "#263C50", primary: "#087F75", accent: "#C34C8A", mint: "#D9F0E8",
      background: "#F4F9F7", surface: "#FFFFFF", soft: "#E3F1EC", border: "#BFDCD4",
      text: "#263C50", muted: "#536A66",
    },
  },
  {
    id: "guacamayo_azul",
    name: "Guacamayo azul",
    bird: "🦜",
    birdImage: "/palette-birds/Guacamayo azul y amarillo caricaturesco.png",
    clinicLogoImage: "/palette-logos/Logotipo Yom Dental Guacamaya Azul.png",
    swatches: ["#173B63", "#1769AA", "#E9C72E", "#168B55", "#F07A24", "#B9D8E8", "#D9272E", "#F4F8FB"],
    colors: {
      plum: "#173B63", primary: "#1769AA", accent: "#D49B18", mint: "#D8EEE5",
      background: "#F4F8FB", surface: "#FFFFFF", soft: "#E4EFF6", border: "#BDD1E0",
      text: "#173B63", muted: "#60778B",
    },
  },
  {
    id: "guacamaya_roja",
    name: "Guacamaya roja",
    bird: "🦜",
    birdImage: "/palette-birds/Guacamaya roja colorida en vuelo (1).png",
    clinicLogoImage: "/palette-logos/Logotipo YOM Dental Guacamaya Roja Multicolor.png",
    swatches: ["#38262C", "#D9272E", "#E9C72E", "#168B55", "#F07A24", "#1769AA", "#F4D9D2", "#FBF5EF"],
    colors: {
      plum: "#38262C", primary: "#D9272E", accent: "#D9A51E", mint: "#F4E4D6",
      background: "#FBF5EF", surface: "#FFFFFF", soft: "#F3E4D7", border: "#DCC5B4",
      text: "#38262C", muted: "#77665F",
    },
  },
  {
    id: "quetzal",
    name: "Quetzal",
    bird: "🪶",
    birdImage: "/palette-birds/Quetzal Adorable de Plumas Esmeralda.png",
    clinicLogoImage: "/palette-logos/Logotipo Yom Dental quetzal.png",
    swatches: ["#183D35", "#087E70", "#159A78", "#42B9A6", "#C8463F", "#A58A36", "#2764B4", "#F5F9F4"],
    colors: {
      plum: "#183D35", primary: "#087E70", accent: "#C8463F", mint: "#D8EEE5",
      background: "#F5F9F4", surface: "#FFFFFF", soft: "#E4F1E7", border: "#C8B26D",
      text: "#183D35", muted: "#60766E",
    },
  },
  {
    id: "faisan",
    name: "Faisán",
    bird: "🐦",
    birdImage: "/palette-birds/Faisán colorido de estilo caricaturesco.png",
    clinicLogoImage: "/palette-logos/Logo dental YOM con degradados Faisán.png",
    swatches: ["#49352D", "#A45136", "#D2A12F", "#79513D", "#277B73", "#D8C3A7", "#E8DDC9", "#FAF6EF"],
    colors: {
      plum: "#49352D", primary: "#A45136", accent: "#C18B2B", mint: "#E9DDC9",
      background: "#FAF6EF", surface: "#FFFFFF", soft: "#F0E6D6", border: "#D8C3A7",
      text: "#49352D", muted: "#74675E",
    },
  },
  {
    id: "ninfa",
    name: "Ninfa",
    bird: "🐦",
    birdImage: "/palette-birds/Cacatúa Ninfa Adorable en Perfil.png",
    clinicLogoImage: "/palette-logos/Logo dental Yom en paleta Ninfa.png",
    swatches: ["#3B4146", "#81888D", "#E27C45", "#E8CA56", "#F5F1E8", "#EEECE3", "#D2D0C6", "#A9A9A4"],
    colors: {
      plum: "#3B4146", primary: "#737B81", accent: "#D87542", mint: "#EEECE3",
      background: "#FAF9F3", surface: "#FFFFFF", soft: "#EEECE3", border: "#D2D0C6",
      text: "#30363B", muted: "#74777B",
    },
  },
  {
    id: "pavo_real",
    name: "Pavo real",
    bird: "🦚",
    birdImage: "/palette-birds/Pavo caricaturesco con cola vibrante.png",
    clinicLogoImage: "/palette-logos/Logo dental Yom en tonos pavorreal.png",
    swatches: ["#23304F", "#087E80", "#176C9B", "#159A78", "#A58A36", "#4B347C", "#2764B4", "#F4F8F8"],
    colors: {
      plum: "#23304F", primary: "#087E80", accent: "#A58A36", mint: "#D9EEE7",
      background: "#F4F8F8", surface: "#FFFFFF", soft: "#E3F0ED", border: "#BBD5CF",
      text: "#23304F", muted: "#61747D",
    },
  },
  {
    id: "tucan",
    name: "Tucán",
    bird: "🐦",
    birdImage: "/palette-birds/Tucán colorido de estilo mascotín.png",
    clinicLogoImage: "/palette-logos/Logotipo Yom Dental Tucán en degradado tropical.png",
    swatches: ["#202124", "#323D43", "#F0C928", "#E97824", "#D94B25", "#B8B8B8", "#F5F1E8", "#FBF8F0"],
    colors: {
      plum: "#202124", primary: "#323D43", accent: "#E97824", mint: "#F5E8C8",
      background: "#FBF8F0", surface: "#FFFFFF", soft: "#F5F1E8", border: "#CEC7B7",
      text: "#202124", muted: "#686A6B",
    },
  },
  {
    id: "agapornis",
    name: "Agapornis",
    bird: "🦜",
    birdImage: "/palette-birds/Agapornis colorido en rama (1).png",
    clinicLogoImage: "/palette-logos/Logo YOM Dental Agaporni Multicolor.png",
    swatches: ["#713B68", "#328C55", "#F2A16D", "#35B9B0", "#FFFCF4", "#B8A0D4", "#E8D84A", "#277DA1"],
    colors: {
      plum: "#553B59", primary: "#328C55", accent: "#D98567", mint: "#D9EEE6",
      background: "#FFFCF4", surface: "#FFFFFF", soft: "#EFE7F2", border: "#D7C9D9",
      text: "#3F3643", muted: "#5F6F69",
    },
  },
  {
    id: "colorin_siete_colores",
    name: "Colorín siete colores",
    bird: "🐦",
    birdImage: "/palette-birds/Colorín Siete Colores en Rama.png",
    clinicLogoImage: "/palette-logos/Logo dental Colorn de 7 colorese.png",
    swatches: ["#183D67", "#087E9B", "#168B62", "#D83C43", "#F0C92E", "#F28A32", "#7B4A9E", "#F6F8F2"],
    colors: { plum: "#183D67", primary: "#087E9B", accent: "#D83C43", mint: "#DCEFE7", background: "#F6F8F2", surface: "#FFFFFF", soft: "#E7F0F1", border: "#BFD4D9", text: "#26384A", muted: "#62727C" },
  },
  {
    id: "flamenco",
    name: "Flamenco",
    bird: "🦩",
    birdImage: "/palette-birds/Flamenco rosa de estilo adhesivo.png",
    clinicLogoImage: "/palette-logos/Logotipo Dental Rosa Flamingo en 3D.png",
    swatches: ["#593B4A", "#D96B8A", "#F2A6B8", "#F28C76", "#F5C7B9", "#F8E9DF", "#A94D70", "#FFF8F3"],
    colors: { plum: "#593B4A", primary: "#C95F80", accent: "#F28C76", mint: "#F8E4E7", background: "#FFF8F3", surface: "#FFFFFF", soft: "#F9E9E8", border: "#E8C7CE", text: "#49343D", muted: "#806B70" },
  },
  {
    id: "tangara_paraiso",
    name: "Tángara del paraíso",
    bird: "🐦",
    birdImage: "/palette-birds/Tángara del paraíso sobre una rama.png",
    clinicLogoImage: "/palette-logos/Logotipo Yom DentalTángara del paraíso.png",
    swatches: ["#153D36", "#087F65", "#21A9A0", "#E84A42", "#F0D52C", "#F28B32", "#2455C5", "#F5F3E9"],
    colors: { plum: "#153D36", primary: "#087F65", accent: "#E84A42", mint: "#DDF0E7", background: "#F5F3E9", surface: "#FFFFFF", soft: "#E7EFE8", border: "#BFD8CE", text: "#253B37", muted: "#65766E" },
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
