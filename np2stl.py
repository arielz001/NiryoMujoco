import os
from stl import mesh
import stl  # Importamos el módulo completo para acceder a las constantes

folder = "STL"

for filename in os.listdir(folder):
    if filename.endswith(".STL") or filename.endswith(".stl"):
        path = os.path.join(folder, filename)
        try:
            # Lee el archivo (sea ASCII o Binario)
            your_mesh = mesh.Mesh.from_file(path)
            
            # Lo guarda estrictamente como Binario usando la constante correcta
            your_mesh.save(path, mode=stl.Mode.BINARY)
            print(f"✅ Convertido con éxito: {filename}")
        except Exception as e:
            print(f"❌ Error con {filename}: {e}")