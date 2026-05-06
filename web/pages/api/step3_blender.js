import net from 'node:net';
import path from 'path';

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const width = req.body.width;
  const length = req.body.length;
  const target_z = req.body.target_z;
  
  try {
    // 1. Preparamos el código de Python que Blender ejecutará
    const blenderScriptPath = path.join(process.cwd(), '..', 'autocad', 'generate_blender_twin.py').replace(/\\/g, '/');

    // Usaremos el mismo truco asíncrono para que Blender no se congele durante el render
    const blenderCode = `
import bpy
import sys
def build_warehouse():
    try:
        sys.argv = ['blender', '--', '${width}', '${length}', '${target_z}']
        filepath = r'${blenderScriptPath}'
        with open(filepath, 'r', encoding='utf-8') as f:
            exec(f.read(), {'__name__': '__main__', 'sys': sys})
    except Exception as e:
        print("Error al ejecutar:", e)
    return None
bpy.app.timers.register(build_warehouse, first_interval=0.5)
print("COMMAND_QUEUED_VIA_TCP_SOCKET")
`;

    // 2. Preparamos el Payload EXACTO que espera el Addon MCP (Raw JSON Socket)
    // Según ahujasid/blender-mcp el formato es: { "type": "execute_code", "params": { "code": "..." } }
    const commandObj = {
        type: "execute_code",
        params: { code: blenderCode }
    };
    const commandString = JSON.stringify(commandObj);

    // 3. Enviamos la orden vía Socket TCP Puro (Igual que el CLI)
    let logOutput = '';
    await new Promise((resolve, reject) => {
      let settled = false;
      const timeoutMs = 10000; // 10 segundos
      let sock;
      
      const done = (msg, isError = false) => {
        if (settled) return;
        settled = true;
        clearTimeout(timer);
        if (sock) { try { sock.destroy(); } catch(e){} }
        if (isError) {
          logOutput += '> Aviso MCP Socket: ' + msg + '\\n';
          resolve(); // Resolvemos igual para que el frontend no falle feo
        } else {
          logOutput += '> Ok MCP Socket: ' + msg + '\\n';
          resolve();
        }
      };

      const timer = setTimeout(() => done("Timeout de " + timeoutMs + "ms", true), timeoutMs);

      sock = net.createConnection({ host: '127.0.0.1', port: 9876 }, () => {
        try {
          sock.write(commandString, "utf8");
        } catch (e) {
          done(e.message, true);
        }
      });

      let buf = Buffer.alloc(0);
      sock.on("data", (chunk) => {
        buf = Buffer.concat([buf, chunk]);
        try {
          const text = buf.toString("utf8");
          const parsed = JSON.parse(text); // Si el JSON se parsea, Blender termino
          if (parsed.status === "success") {
             done("Gemelo Digital encolado en Blender exitosamente.");
          } else {
             done("Blender respondio con error: " + (parsed.error || parsed.message), true);
          }
        } catch (e) {
          // El JSON aun esta incompleto, esperamos el siguiente chunk
        }
      });

      sock.on("error", (err) => done(err.message, true));
    });

    res.status(200).json({ log: logOutput });

  } catch (error) {
    res.status(200).json({ log: '> Error Critico Node.js: ' + error.message + '\n' });
  }
}
