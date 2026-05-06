var spawn = require('child_process').spawn;
var path = require('path');
var fs = require('fs');

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  var area = req.body.area;
  var logOutput = 'Iniciando orquestacion para ' + area + ' m2...\n';

  try {
    var orchestratorPath = path.join(process.cwd(), '..', 'main_orchestrator.py');
    var pythonExec = 'C:\\Users\\llopez\\Documents\\autocad-ai-automation\\venv\\Scripts\\python.exe';
    
    var pythonProcess = spawn(pythonExec, [orchestratorPath, area]);
    
    await new Promise(function(resolve) {
        pythonProcess.stdout.on('data', function(data) { logOutput += data.toString(); });
        pythonProcess.on('close', resolve);
    });

    logOutput += '\n[Blender MCP Live] Solicitando ejecucion del script al Addon...\n';

    // Leer la cota Z del terreno
    var terrainResultsPath = path.join(process.cwd(), '..', 'core', 'terrain_results.json');
    var cota_z = 60; 
    try {
        var terrainData = JSON.parse(fs.readFileSync(terrainResultsPath, 'utf8'));
        cota_z = terrainData.cota_optima;
    } catch(e) {}

    var width = Math.floor(Math.sqrt(area / 1.25));
    var length = Math.floor(area / width);

    // Ruta absoluta al script de Blender que ya validamos que funciona perfecto
    var blenderScriptPath = path.join(process.cwd(), '..', 'autocad', 'generate_blender_twin.py').replace(/\\/g, '/');

    // Código Python ultra-corto: Solo importa y ejecuta la función del archivo existente
    var blenderCode = "import sys\n";
    blenderCode += "import importlib.util\n";
    blenderCode += "script_path = '" + blenderScriptPath + "'\n";
    blenderCode += "spec = importlib.util.spec_from_file_location('generador', script_path)\n";
    blenderCode += "modulo = importlib.util.module_from_spec(spec)\n";
    blenderCode += "spec.loader.exec_module(modulo)\n";
    blenderCode += "modulo.generate_warehouse_twin(" + width + ", " + length + ", " + cota_z + ")\n";

    try {
        var blenderResponse = await fetch('http://localhost:9876/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: blenderCode })
        });

        if (blenderResponse.ok) {
            logOutput += 'Ok: Archivo cargado en vivo en Blender.\n';
        } else {
            logOutput += 'Error: Fallo la inyeccion en Blender MCP. Revisa la consola de Blender.\n';
        }
    } catch (e) {
        logOutput += 'Error: Sin conexion a Blender MCP (puerto 9876 cerrado).\n';
    }

    res.status(200).json({ 
      message: 'Completado', 
      log: logOutput 
    });

  } catch (error) {
    res.status(500).json({ message: 'Error', error: error.message });
  }
}
