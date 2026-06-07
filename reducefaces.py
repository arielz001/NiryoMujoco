import pymeshlab as ml
import os

folder_path = "STL2"
TARGET_FACES = 25000

if not os.path.exists(folder_path):
    print(f"❌ No se encontró la carpeta: {folder_path}")
    exit()

print(f"🚀 Analizando y optimizando mallas en '{folder_path}'...\n")

files = [f for f in os.listdir(folder_path) if f.lower().endswith('.stl')]

for filename in files:
    input_path = os.path.join(folder_path, filename)
    
    try:
        ms = ml.MeshSet()
        ms.load_new_mesh(input_path)
        
        # 📊 AQUÍ OBTENEMOS EL CONTEO EXACTO DE CARAS ACTUALES
        initial_faces = ms.current_mesh().face_number()
        print(f"📦 Archivo: {filename:<20} ➡️  Caras actuales: {initial_faces}")
        
        # Reducir solo si supera el objetivo
        if initial_faces > TARGET_FACES:
            ms.apply_filter(
                'mesimation_decimation_quadric_edge_collapse' if 'mesimation' in dir(ml) else 'meshing_decimation_quadric_edge_collapse',
                targetfacenum=TARGET_FACES,
                preserveboundary=True,
                preservetopology=True
            )
            print(f"   📉 Reducido a: {ms.current_mesh().face_number()} caras.")
        else:
            print(f"   ✅ Ya es ligero ({initial_faces} caras).")

        # Guardar directamente a binario sin pasar por filtros de limpieza problemáticos
        ms.save_current_mesh(input_path, binary=True)
        print(f"   💾 Guardado en formato Binario.\n")
        
    except Exception as e:
        print(f"   ❌ Error al procesar: {e}\n")

print("✨ Proceso terminado.")