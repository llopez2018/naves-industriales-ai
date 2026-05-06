import React, { useState } from 'react';

export default function Home() {
  const [area, setArea] = useState(50000);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(0);
  const [status, setStatus] = useState('');
  const [result, setResult] = useState(null);
  const [log, setLog] = useState('');

  const appendLog = (msg) => setLog(prev => prev + msg + '\n');

  const handleGenerate = async () => {
    setLoading(true);
    setResult(null);
    setLog('');
    setStep(1);
    
    setStatus('Fase 2: Ejecutando RandLA-Net + Ingeniería...');
    appendLog('[Fase 2] Iniciando Deep Learning para segmentacion semantica...');
    
    try {
      const res1 = await fetch('/api/step1_core', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ area })
      });
      const data1 = await res1.json();
      if (!res1.ok) throw new Error(data1.error);
      
      appendLog(data1.log);
      setResult(data1); 
      
      setStep(2);
      setStatus('Fase 2: Generando BIM...');
      const res2 = await fetch('/api/step2_autocad', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ width: 200, length: 250, target_z: data1.cota_z })
      });
      const data2 = await res2.json();
      appendLog(data2.log);

      setStep(3);
      setStatus('Fase 2: Gemelo Digital...');
      await fetch('/api/step3_blender', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ width: 200, length: 250, target_z: data1.cota_z })
      });
      appendLog('> Ok: Procesamiento Fase 2 Terminado.');

      setStatus('¡Proyecto Fase 2 Completado!');
      setStep(4);
    } catch (err) {
      setStatus('Error en Fase 2');
      appendLog('ERROR: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ fontFamily: 'sans-serif', backgroundColor: '#f4f3ef', minHeight: '100vh', padding: '40px' }}>
      <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
        
        <div style={{ backgroundColor: 'white', padding: '40px', borderRadius: '16px', boxShadow: '0 4px 20px rgba(0,0,0,0.08)', marginBottom: '20px' }}>
          <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #eee', paddingBottom: '20px', marginBottom: '30px' }}>
             <div>
                <h1 style={{ color: '#1a1830', margin: 0 }}>Plataforma Digital · Fase 2</h1>
                <p style={{ color: '#666', marginTop: '8px' }}>Deep Learning (RandLA-Net) + Automatización BIM</p>
             </div>
             <div style={{ backgroundColor: '#EEEDFE', color: '#534AB7', padding: '8px 16px', borderRadius: '20px', fontWeight: 'bold', fontSize: '12px' }}>
                STATUS: MVP INDUSTRIAL
             </div>
          </header>
          
          <div style={{ margin: '30px 0' }}>
            <label style={{ fontWeight: 'bold', display: 'block', marginBottom: '10px' }}>Tamaño de Nave: {area.toLocaleString()} m²</label>
            <input type="range" min="10000" max="100000" step="5000" value={area} onChange={(e) => setArea(parseInt(e.target.value))} style={{ width: '100%', accentColor: '#534AB7' }} disabled={loading} />
          </div>

          <button onClick={handleGenerate} disabled={loading} style={{ width: '100%', padding: '16px', backgroundColor: loading ? '#ccc' : '#534AB7', color: 'white', border: 'none', borderRadius: '8px', fontWeight: 'bold', fontSize: '16px', cursor: 'pointer' }}>
            {loading ? 'EJECUTANDO PIPELINE FASE 2...' : 'GENERAR PROYECTO (RANDLA-NET + BIM)'}
          </button>
        </div>

        {result && step === 4 && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px', marginBottom: '20px' }}>
            
            {/* IA Segmentación */}
            <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', borderLeft: '5px solid #0F6E56' }}>
              <h3 style={{ fontSize: '14px', color: '#666', margin: '0 0 15px 0' }}>IA RandLA-Net (Segmentación)</h3>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#0F6E56' }}>{Math.round((result.segmentation.ground / result.segmentation.total) * 100)}%</div>
              <p style={{ fontSize: '12px', color: '#888' }}>Superficie útil de suelo detectada.</p>
              <div style={{ marginTop: '10px', fontSize: '12px' }}>
                <div>• Suelo: {result.segmentation.ground.toLocaleString()} pts</div>
                <div>• Veg: {result.segmentation.vegetation.toLocaleString()} pts</div>
              </div>
            </div>

            {/* Presupuesto */}
            <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', borderLeft: '5px solid #534AB7' }}>
              <h3 style={{ fontSize: '14px', color: '#666', margin: '0 0 15px 0' }}>Presupuesto Estimado</h3>
              <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#534AB7' }}>${result.budget.resumen.total_estimado.toLocaleString()}</div>
              <p style={{ fontSize: '12px', color: '#888' }}>Total inversión inicial (Capex).</p>
            </div>

            {/* Agente Normativo */}
            <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', borderLeft: `5px solid ${result.safety.status === 'CRITICAL' ? '#A32D2D' : '#f59e0b'}` }}>
              <h3 style={{ fontSize: '14px', color: '#666', margin: '0 0 15px 0' }}>Dictamen Normativo</h3>
              <div style={{ fontWeight: 'bold', color: result.safety.status === 'CRITICAL' ? '#A32D2D' : '#92400e' }}>
                ESTATUS: {result.safety.status}
              </div>
              <p style={{ fontSize: '11px', color: '#666', marginTop: '5px' }}>{result.safety.warnings[0]}</p>
            </div>

          </div>
        )}

        <div style={{ backgroundColor: '#1a1830', borderRadius: '16px', padding: '20px' }}>
          <pre style={{ color: '#e1f5ee', fontSize: '11px', whiteSpace: 'pre-wrap', margin: 0 }}>{log}</pre>
        </div>

      </div>
    </div>
  );
}
