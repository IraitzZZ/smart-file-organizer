import os
import json
import shutil
from pathlib import Path

REGISTRO = "movimientos.json"

# Reglas inteligentes: no solo extensión, sino también contexto
REGLAS = [
    {
        'nombre': '📸 Fotos y capturas',
        'ext': ['.jpg', '.jpeg', '.png', '.webp', '.bmp'],
        'razon': 'Son imágenes comunes: fotos, capturas de pantalla o gráficos.'
    },
    {
        'nombre': '📄 Documentos importantes',
        'ext': ['.pdf', '.docx', '.doc', '.txt', '.xlsx', '.pptx'],
        'razon': 'Archivos de trabajo, estudio o lectura.'
    },
    {
        'nombre': '🎥 Videos personales o descargas',
        'ext': ['.mp4', '.mkv', '.avi', '.mov'],
        'razon': 'Contenido audiovisual que probablemente no es temporal.'
    },
    {
        'nombre': '🎵 Música o audio',
        'ext': ['.mp3', '.wav', '.ogg', '.flac'],
        'razon': 'Archivos de sonido para escuchar, no efectos efímeros.'
    },
    {
        'nombre': '📦 Archivos comprimidos',
        'ext': ['.zip', '.rar', '.7z', '.tar.gz'],
        'razon': 'Contienen otros archivos; mejor tenerlos agrupados.'
    },
    {
        'nombre': '⚙️ Programas o instaladores',
        'ext': ['.exe', '.msi', '.bat'],
        'razon': 'Software descargado. Puede ser útil tenerlo separado por seguridad.'
    },
]

def analizar_carpeta(ruta):
    ruta = Path(ruta).expanduser()
    if not ruta.exists():
        print(f"❌ La carpeta '{ruta}' no existe.")
        return []

    acciones = []
    for archivo in ruta.iterdir():
        if not archivo.is_file():
            continue

        nombre = archivo.name
        ext = archivo.suffix.lower()

        # Buscar regla que coincida
        destino = "📁 Otros"
        razon = "No coincide claramente con ninguna categoría conocida."
        for regla in REGLAS:
            if ext in regla['ext']:
                destino = regla['nombre']
                razon = regla['razon']
                break

        acciones.append({
            'archivo': str(archivo),
            'nombre': nombre,
            'destino': destino,
            'razon': razon
        })
    return acciones

def mostrar_vista_clara(acciones):
    if not acciones:
        print("\n✅ No hay archivos para organizar.")
        return

    print("\n" + "═" * 60)
    print("🧠 Vista previa inteligente: ¿Qué haré y por qué?")
    print("═" * 60)

    for a in acciones:
        print(f"\n📄 {a['nombre']}")
        print(f"   ➤ {a['destino']}")
        print(f"   💬 {a['razon']}")

    print("\n" + "─" * 60)
    print(f"🔍 Total: {len(acciones)} archivos listos para organizar.")

def confirmar():
    while True:
        r = input("\n¿Aplicar estos cambios? (s/n): ").strip().lower()
        if r in ('s', 'si', 'y', 'yes'):
            return True
        elif r in ('n', 'no'):
            return False
        print("👉 Por favor, responde 's' o 'n'.")

def aplicar(acciones, ruta_base):
    ruta_base = Path(ruta_base).expanduser()
    registro = []

    for a in acciones:
        origen = Path(a['archivo'])
        # Extraer nombre de carpeta desde el destino (solo el texto después del emoji)
        nombre_carpeta = a['destino'].split(' ', 1)[-1] if ' ' in a['destino'] else a['destino'].replace('📁 ', '')
        destino = ruta_base / nombre_carpeta

        destino.mkdir(exist_ok=True)
        nuevo_path = destino / origen.name

        try:
            shutil.move(origen, nuevo_path)
            registro.append({'origen': str(origen), 'destino': str(nuevo_path)})
        except Exception as e:
            print(f"⚠️ Error al mover {origen.name}: {e}")

    with open(REGISTRO, 'w', encoding='utf-8') as f:
        json.dump(registro, f, indent=2, ensure_ascii=False)
    print(f"\n✅ ¡Listo! Registro guardado en '{REGISTRO}'.")

def revertir():
    if not Path(REGISTRO).exists():
        print("❌ No hay acciones recientes que revertir.")
        return

    with open(REGISTRO, 'r', encoding='utf-8') as f:
        movs = json.load(f)

    print("\n🔄 Deshaciendo movimientos...")
    for m in movs:
        src = Path(m['destino'])
        dst = Path(m['origen'])
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(src, dst)
            print(f"⏪ Restaurado: {dst.name}")

    os.remove(REGISTRO)
    print("✅ Reversión completada.")

# ─── PUNTO DE ENTRADA ───────────────────────────────
if __name__ == "__main__":
    import sys

    if "--revertir" in sys.argv:
        revertir()
    else:
        print("🧹 Organizador Inteligente v2")
        carpeta = input("Carpeta a organizar (Enter = ~/Downloads): ").strip() or "~/Downloads"
        acciones = analizar_carpeta(carpeta)

        if not acciones:
            exit()

        mostrar_vista_clara(acciones)

        if confirmar():
            aplicar(acciones, carpeta)
        else:
            print("\n🚫 Cancelado. Todo permanece igual.")