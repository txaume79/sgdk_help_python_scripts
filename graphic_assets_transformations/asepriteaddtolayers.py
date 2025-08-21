import os
import re
import subprocess
from pathlib import Path

ASEPRITE_PATH = "C:/Users/txaume/Downloads/Aseprite.v1.3/Aseprite.v1.3/aseprite.exe"  # Modifica si es necesario

def get_matching_images(dir_path, numero):
    pattern = re.compile(rf"^{numero}_z[+-].*_(con|sin)_trapecio\.png$")
    return sorted([f for f in os.listdir(dir_path) if pattern.match(f)])

def create_aseprite_script(image_files, full_paths, output_path):
    lines = ['local spr', 'local final']
    for i, (name, path) in enumerate(zip(image_files, full_paths)):
        escaped_path = path.replace("\\", "/")
        lines.append(f'spr = app.open("{escaped_path}")')
        lines.append('local layer = spr.layers[1]')
        lines.append(f'layer.name = "{name}"')
        if i == 0:
            lines.append('final = spr')
        else:
            lines.append('local newLayer = final:newLayer()')
            lines.append(f'newLayer.name = "{name}"')
            lines.append('for i, cel in ipairs(spr.cels) do')
            lines.append('  final:newCel(newLayer, cel.frameNumber, cel.image)')
            lines.append('end')
        
        
    escaped_output = output_path.replace("\\", "/")
    
    lines.append(f'final:saveAs("{escaped_output}")')
    
    return '\n'.join(lines)

def process_directory(base_dir, numero):
    dir_path = os.path.join(base_dir, str(numero))
    if not os.path.isdir(dir_path):
        return

    image_files = get_matching_images(dir_path, numero)
    if not image_files:
        return

    full_paths = [os.path.abspath(os.path.join(dir_path, f)) for f in image_files]
    output_ase = os.path.abspath(os.path.join(dir_path, f"{numero}_combinado.ase"))
    lua_script = create_aseprite_script(image_files, full_paths, output_ase)
    print(lua_script)

    script_path = os.path.join(dir_path, f"gen_{numero}.lua")
    with open(script_path, "w") as f:
        f.write(lua_script)

    # Ejecutar Aseprite con el script
    script_path = Path(dir_path) / f"gen_{numero}.lua"
    script_path_str = str(script_path).replace("\\", "/")
    subprocess.run([
        ASEPRITE_PATH,
        "--batch",
        "--script", script_path_str
    ])

    os.remove(script_path)
    print(f"[✔] Generado: {output_ase}")

if __name__ == "__main__":
    base_dir = "C:/Users/txaume/Pictures/assests_sgdk_wip/New_Folder/rotateds/azul/"
    for numero in range(20):
        process_directory(base_dir, numero)
