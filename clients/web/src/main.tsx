import React from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

function App() {
  return <main className="shell">
    <header><div className="mark">A</div><div><strong>AVIS</strong><small>ANÁLISIS DENTALES</small></div><span className="local">● DATOS LOCALES</span></header>
    <section className="hero"><p className="eyebrow">PLATAFORMA DE ANÁLISIS ODONTOLÓGICO</p><h1>Tu espacio de trabajo clínico y académico.</h1><p>Expedientes, estudios y análisis en un entorno local. Esta versión no sincroniza datos ni los envía a servidores.</p></section>
    <section className="grid">
      <article><span>01</span><h2>Expedientes</h2><p>Organiza pacientes y estudios en este dispositivo.</p><button disabled>Próxima etapa</button></article>
      <article><span>02</span><h2>Análisis</h2><p>Acceso progresivo a cefalometría, fotografías, panorámica y modelos.</p><button disabled>Próxima etapa</button></article>
      <article><span>03</span><h2>Informes</h2><p>Generación local de reportes y respaldos manuales.</p><button disabled>Próxima etapa</button></article>
    </section>
    <footer>AVIS · Versión de arquitectura inicial · No usar aún con datos identificables de pacientes.</footer>
  </main>;
}
createRoot(document.getElementById('root')!).render(<React.StrictMode><App /></React.StrictMode>);
