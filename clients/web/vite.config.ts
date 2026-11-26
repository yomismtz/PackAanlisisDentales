import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['avis-icon.svg', 'avis-logo.svg', 'avis-slogan.svg', 'avis-colibri.svg'],
      manifest: {
        name: 'AVIS · Análisis Odontológico Integral',
        short_name: 'AVIS',
        description: 'Observa • Analiza • Integra',
        theme_color: '#48263F',
        background_color: '#FFFFFF',
        display: 'standalone',
        start_url: '/',
        icons: [{ src: '/avis-icon.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'any' }]
      },
      workbox: {
        // The ten bird calls are embedded in the bundled JavaScript sprite.
        // Precache that bundle so palette sounds are available without internet.
        globPatterns: ['**/*.{js,css,html,svg,png,woff2}'],
        maximumFileSizeToCacheInBytes: 5 * 1024 * 1024,
      },
    }),
  ],
  server: { host: '0.0.0.0' }
});
