import os
import numpy as np
from stl import mesh

origen_dir = "STL2"
destino_dir = "STL2_CENTRADOS"

# Crear la carpeta de destino si no existe
if not os.path.exists(destino_dir):
    os.makedirs(destino_dir)

print("--- Recentrado de STL (Garantizando compatibilidad con MuJoCo) ---")

try:
    todos_los_archivos = os.listdir(origen_dir)
except FileNotFoundError:
    print(f"❌ Error: La carpeta '{origen_dir}' no existe.")
    exit()

# Filtrar archivos .stl
archivos_stl = [f for f in todos_los_archivos if f.lower().endswith('.stl')]

if not archivos_stl:
    print(f"⚠️ No se encontraron archivos .stl en '{origen_dir}'.")
    exit()

for archivo in archivos_stl:
    ruta_input = os.path.join(origen_dir, archivo)
    ruta_output = os.path.join(destino_dir, archivo)
    
    # 1. Cargar la malla con numpy-stl
    malla = mesh.Mesh.from_file(ruta_input)
    
    # 2. Calcular el centro geométrico real basado en los vértices
    # Aplanamos los vectores para obtener la nube de puntos [N, 3]
    vertices = malla.vectors.reshape(-1, 3)
    centro = np.mean(vertices, axis=0)
    
    print(f"🔄 Procesando: {archivo}")
    print(f"   -> Centro original: [{centro[0]:.4f}, {centro[1]:.4f}, {centro[2]:.4f}]")
    
    # 3. Trasladar la geometría restando el centro de todos sus ejes
    malla.x -= centro[0]
    malla.y -= centro[1]
    malla.z -= centro[2]
    
    # 4. Guardar en formato binario estándar (totalmente compatible con MuJoCo)
    malla.save(ruta_output)
    print(f"   ✅ ¡Guardado limpio! -> {ruta_output}\n")

print(f"--- Proceso terminado. Archivos listos en '{destino_dir}' ---")