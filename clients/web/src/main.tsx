import React from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

function App() {
  return <main className="shell">
    <header>
      <img className="brand-mark" src="/avis-icon.svg" alt="Icono de AVIS con colibrí" />
      <div className="brand-copy"><strong>AVIS</strong><small>ANÁLISIS ODONTOLÓGICO INTEGRAL</small></div>
      <span className="local"><i /> DATOS LOCALES</span>
    </header>
    <section className="hero">
      <img className="hero-logo" src="/avis-logo.svg" alt="AVIS · Análisis Odontológico Integral" />
      <img className="hero-slogan" src="/avis-slogan.svg" alt="Observa, Analiza, Integra" />
      <p className="eyebrow">PLATAFORMA DE ANÁLISIS ODONTOLÓGICO</p>
      <h1>Observa. Analiza. Integra.</h1>
      <p>Expedientes, estudios y análisis en un entorno local. Esta versión no sincroniza datos ni los envía a servidores.</p>
    </section>
    <section className="grid">
      <article><span>01</span><h2>Expedientes</h2><p>Organiza pacientes y estudios en este dispositivo.</p><button disabled>Próxima etapa</button></article>
      <article><span>02</span><h2>Análisis</h2><p>Acceso progresivo a cefalometría, fotografías, panorámica y modelos.</p><button disabled>Próxima etapa</button></article>
      <article><span>03</span><h2>Informes</h2><p>Generación local de reportes y respaldos manuales.</p><button disabled>Próxima etapa</button></article>
    </section>
    <footer><strong>AVIS</strong> · Análisis Odontológico Integral · Observa • Analiza • Integra<br/>Versión de arquitectura inicial. No usar aún con datos identificables de pacientes.</footer>
  </main>;
}
createRoot(document.getElementById('root')!).render(<React.StrictMode><App /></React.StrictMode>);
