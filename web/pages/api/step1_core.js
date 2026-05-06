var spawn = require('child_process').spawn;
var path = require('path');
var fs = require('fs');

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  var area = req.body.area;
  var logOutput = '';
  
  try {
    // 1. Ejecutar solo la IA y Presupuesto
    var coreScriptPath = path.join(process.cwd(), '..', 'core', 'calculate_optimal_grade.py');
    var budgetScriptPath = path.join(process.cwd(), '..', 'core', 'budget_generator.py');
    var pythonExec = 'C:\\Users\\llopez\\Documents\\autocad-ai-automation\\venv\\Scripts\\python.exe';
    
    // Calcular Terreno
    logOutput += '> Ejecutando algoritmo de optimizacion topografica...\n';
    await new Promise(function(resolve, reject) {
        var p = spawn(pythonExec, [coreScriptPath]);
        p.stdout.on('data', function(d) { logOutput += d.toString(); });
        p.on('close', function(code) { code === 0 ? resolve() : reject(); });
    });

    // Leer Resultados
    var terrainResultsPath = path.join(process.cwd(), '..', 'core', 'terrain_results.json');
    var terrainData = JSON.parse(fs.readFileSync(terrainResultsPath, 'utf8'));
    
    // Calcular Presupuesto
    var width = Math.floor(Math.sqrt(area / 1.25));
    var length = Math.floor(area / width);
    var cols = Math.floor(length / 25) * Math.floor(width / 25);
    
    logOutput += '> Generando presupuesto financiero...\n';
    await new Promise(function(resolve, reject) {
        var p = spawn(pythonExec, [budgetScriptPath, area, terrainData.volumen_corte_m3, cols]);
        p.on('close', function(code) { code === 0 ? resolve() : reject(); });
    });

    var budgetData = JSON.parse(fs.readFileSync('last_budget.json', 'utf8'));

    res.status(200).json({ 
      log: logOutput,
      cota_z: terrainData.cota_optima,
      budget: budgetData
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}
