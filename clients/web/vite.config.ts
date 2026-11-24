import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [react(), VitePWA({
    registerType: 'autoUpdate',
    includeAssets: ['avis-agapornis.svg', 'avis-logo.svg'],
    manifest: {
      name: 'AVIS · Análisis Odontológico Integral',
      short_name: 'AVIS',
      description: 'Observa • Analiza • Integra',
      theme_color: '#073C5A',
      background_color: '#F4F8F9',
      display: 'standalone',
      start_url: '/',
      icons: [{ src: '/avis-agapornis.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'any maskable' }]
    },
    workbox: { globPatterns: ['**/*.{js,css,html,svg,png,woff2}'] }
  })],
  server: { host: '0.0.0.0' }
});
