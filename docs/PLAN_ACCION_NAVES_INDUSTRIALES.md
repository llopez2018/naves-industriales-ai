# Plan Maestro de Acción: Plataforma Digital Naves Industriales

## 📍 1. ¿Dónde Estamos? (Estado Actual)

Actualmente hemos superado la fase de ideación teórica y hemos comenzado a asentar las bases técnicas en el entorno local (Workspace).

**Componentes Listos y Configurados:**
1. **Estructura de Datos Base (`naves_industriales_config.json`):** Ya tenemos la "verdad absoluta" del proyecto (actividades, costos, stack tecnológico y roadmap) extraída en un formato que nuestras aplicaciones pueden leer automáticamente.
2. **Generador de Planos (`process_naves_project.py`):** Un script funcional que toma los parámetros de la nave industrial y los traduce en instrucciones geométricas (coordenadas, muros, retícula de columnas).
3. **Plano de Control Frontend (`gemini-blender-industrial`):** Existe un proyecto en Next.js preparado para ser la interfaz de chat y visualización del usuario (el dashboard).
4. **Servidores de Ejecución (MCP):**
   - **AutoCAD Server:** Está activo (`mcp_server.py`), pero actualmente está sufriendo de *timeouts* debido a latencia en la comunicación COM con la aplicación de escritorio.
   - **Blender Server:** El proceso existe, pero requiere reiniciarse o configurarse adecuadamente para recibir comandos de generación del gemelo digital.

---

## 🎯 2. ¿Qué es lo que debemos trabajar? (Próximos Pasos)

Para cumplir con la **Fase 1 (Piloto)** propuesta en el roadmap original, debemos enfocarnos en las siguientes áreas de trabajo, divididas por prioridad:

### Prioridad Alta: Estabilización de Infraestructura (Semana 1)
No podemos automatizar si los motores fallan.
*   **[ ] Reparar Timeouts de AutoCAD:** Modificar el servidor MCP de AutoCAD para manejar grandes volúmenes de entidades (quizás usar procesamiento por lotes o verificar que AutoCAD no tenga cuadros de diálogo bloqueantes abiertos).
*   **[ ] Reconectar Blender MCP:** Asegurar que el addon de Blender en `gemini-blender-industrial/worker` esté corriendo y escuchando en el puerto correcto (9876) para recibir la geometría del gemelo digital.

### Prioridad Media: Desarrollo de Algoritmos Núcleo de la Fase 1 (Semana 2-3)
Aquí es donde entra la IA y la automatización real.
*   **[ ] Script de Cota Óptima de Plataforma:** Crear un script en Python (usando `SciPy` o `NumPy`) en `autocad-ai-automation/scripts` que simule un terreno accidentado y calcule matemáticamente el plano de corte/relleno óptimo para compensar volúmenes.
*   **[ ] Copiloto LLM para Presupuestos:** Integrar un pequeño flujo (usando LangChain o llamadas directas a Gemini) que reciba los metros cuadrados de la nave y los cruce con una base de datos simulada (CMIC) para generar un presupuesto base automático.

### Prioridad Media-Baja: Orquestación e Interfaz (Semana 4-5)
Unificar las piezas para que el usuario no tenga que tocar código.
*   **[ ] Conectar la UI con el Backend:** Hacer que desde el chat de la aplicación web (`localhost:3000`) se pueda escribir: *"Genera una nave de 50,000 m2"* y esto dispare:
    1. El script de presupuesto.
    2. El dibujo en AutoCAD.
    3. La previsualización 3D en Blender.
*   **[ ] Simulación de Salida (OIC/Primavera):** Generar los archivos CSV o JSON finales que emularían la carga de datos hacia Oracle EPM y Primavera, demostrando el "End-to-End".

---

## 🚀 3. ¿Por dónde empezamos hoy?

Si deseas comenzar a trabajar ahora mismo, te sugiero elegir una de estas dos vías:
**Vía A (Backend/Geometría):** Solucionar los timeouts de AutoCAD y lograr que el script dibuje la nave de 50,000 m² exitosamente.
**Vía B (Algoritmia/IA):** Empezar a programar el script de cálculo de **Cota Óptima de Terreno** (movimiento de tierras).
