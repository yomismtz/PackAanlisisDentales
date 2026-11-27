import type { PaletteId } from "./themePalettes";
import { opus6k01 } from "./audioParts/opus6k01";
import { opus6k02 } from "./audioParts/opus6k02";
import { opus6k03 } from "./audioParts/opus6k03";
import { opus6k04 } from "./audioParts/opus6k04";
import { opus6k05 } from "./audioParts/opus6k05";
import { opus6k06 } from "./audioParts/opus6k06";
import { opus6k07 } from "./audioParts/opus6k07";
import { opus6k08 } from "./audioParts/opus6k08";
import { opus6k09 } from "./audioParts/opus6k09";

/**
 * Bird calls are bundled into the application itself. The Ogg/Opus sprite is
 * split only to keep Git source files manageable; it is reassembled in memory
 * and decoded locally. No network request is made when a palette is selected.
 */
const BIRD_AUDIO_BASE64 = [
  opus6k01, opus6k02, opus6k03, opus6k04, opus6k05,
  opus6k06, opus6k07, opus6k08, opus6k09,
].join("");

const CLIPS: Partial<Record<PaletteId, { start: number; duration: number }>> = {
  buho_real:      { start: 0.000,   duration: 8.005 },
  colibri:        { start: 8.255,   duration: 3.709 },
  guacamayo_azul: { start: 12.214,  duration: 14.545 },
  guacamaya_roja: { start: 27.009,  duration: 3.049 },
  quetzal:        { start: 30.308,  duration: 4.573 },
  faisan:         { start: 35.131,  duration: 9.109 },
  ninfa:          { start: 44.490,  duration: 1.729 },
  pavo_real:      { start: 46.469,  duration: 4.069 },
  tucan:          { start: 50.788,  duration: 13.328 },
  agapornis:      { start: 64.366,  duration: 2.296 },
};

type AudioContextWithWebkit = typeof window & {
  webkitAudioContext?: typeof AudioContext;
};

let audioContext: AudioContext | null = null;
let decodedAudio: Promise<AudioBuffer> | null = null;
let activeSource: AudioBufferSourceNode | null = null;
let playbackRequest = 0;

function getContext(): AudioContext {
  if (audioContext) return audioContext;
  const browserWindow = window as AudioContextWithWebkit;
  const Context = window.AudioContext ?? browserWindow.webkitAudioContext;
  if (!Context) {
    throw new Error("Este navegador no permite reproducir el sonido de las aves.");
  }
  audioContext = new Context();
  return audioContext;
}

function decodeBirdSprite(context: AudioContext): Promise<AudioBuffer> {
  if (decodedAudio) return decodedAudio;
  const binary = atob(BIRD_AUDIO_BASE64);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) {
    bytes[index] = binary.charCodeAt(index);
  }
  const exactBuffer = bytes.buffer.slice(
    bytes.byteOffset,
    bytes.byteOffset + bytes.byteLength,
  );
  decodedAudio = context.decodeAudioData(exactBuffer).catch((error) => {
    decodedAudio = null;
    throw error;
  });
  return decodedAudio;
}

/** Stops the current bird call, including any call still waiting to decode. */
export function stopBirdCall(): void {
  playbackRequest += 1;
  if (activeSource) {
    try {
      activeSource.stop();
    } catch {
      // A source that already ended cannot be stopped again.
    }
    activeSource.disconnect();
    activeSource = null;
  }
}

/**
 * Plays only the clip assigned to the selected palette.
 * Call this directly from the palette selection user interaction.
 */
export async function playBirdCall(paletteId: PaletteId): Promise<void> {
  const clip = CLIPS[paletteId];
  if (!clip) return;

  const request = ++playbackRequest;
  const context = getContext();

  if (activeSource) {
    try {
      activeSource.stop();
    } catch {
      // The previous call may already have finished.
    }
    activeSource.disconnect();
    activeSource = null;
  }

  // Resume is invoked immediately while the palette change still has
  // transient user activation; decoding can then finish asynchronously.
  const resumePromise = context.resume();
  const bufferPromise = decodeBirdSprite(context);
  const [, buffer] = await Promise.all([resumePromise, bufferPromise]);

  if (request !== playbackRequest) return;

  const source = context.createBufferSource();
  source.buffer = buffer;
  source.connect(context.destination);
  source.onended = () => {
    if (activeSource === source) activeSource = null;
    source.disconnect();
  };
  activeSource = source;
  source.start(0, clip.start, clip.duration);
}
