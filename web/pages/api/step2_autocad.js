var spawn = require('child_process').spawn;
var path = require('path');

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  var width = req.body.width;
  var length = req.body.length;
  var target_z = req.body.target_z;
  var logOutput = '';
  
  try {
    var autocadScript = path.join(process.cwd(), '..', 'autocad', 'test_directo_autocad_3d.py');
    var pythonExec = 'C:\\Users\\llopez\\Documents\\autocad-ai-automation\\venv\\Scripts\\python.exe';
    
    logOutput += '> Comunicando con API de AutoCAD...\n';
    
    await new Promise(function(resolve, reject) {
        var p = spawn(pythonExec, [autocadScript, width, length, target_z]);
        p.stdout.on('data', function(d) { logOutput += d.toString(); });
        p.stderr.on('data', function(d) { logOutput += 'Error: ' + d.toString(); });
        p.on('close', function(code) { resolve(); });
    });

    res.status(200).json({ log: logOutput });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}
