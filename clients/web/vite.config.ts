import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [react(), VitePWA({
    registerType: 'autoUpdate',
    includeAssets: [],
    manifest: {
      name: 'AVIS · Análisis Dentales',
      short_name: 'AVIS',
      description: 'Expediente y análisis odontológicos locales',
      theme_color: '#6D45A6',
      background_color: '#FFFFFF',
      display: 'standalone',
      start_url: '/',
      icons: []
    },
    workbox: { globPatterns: ['**/*.{js,css,html,svg,png,woff2}'] }
  })],
  server: { host: '0.0.0.0' }
});
