#!/usr/bin/env bash
# scripts/build_icons.sh - Pipeline Oficial Apple Swift para Geração de Ícones a partir de assets/icon.svg
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null 2>&1 && pwd )"
cd "$DIR"

SVG_SOURCE="$DIR/assets/icon.svg"
ICNS_OUTPUT="$DIR/assets/DevOpsHero.icns"
ICO_OUTPUT="$DIR/assets/DevOpsHero.ico"

echo -e "\033[1;34m⚡ [Icon Pipeline]\033[0m Utilizando assets/icon.svg como padrão oficial..."

if [ ! -f "$SVG_SOURCE" ]; then
    echo -e "\033[1;31m[ERRO]\033[0m assets/icon.svg não encontrado."
    exit 1
fi

TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

ICONSET_DIR="$TEMP_DIR/DevOpsHero.iconset"
mkdir -p "$ICONSET_DIR"

# 1. Renderiza todas as 10 resoluções Retina com Apple Swift + AppKit (100% alfa, sem fundo branco)
echo -e "\033[1;34m⚡ [Icon Pipeline]\033[0m Renderizando via Apple Swift (AppKit NSGraphicsContext)..."
"$DIR/scripts/render_icon.swift" "$SVG_SOURCE" "$ICONSET_DIR"

# 2. Compilar ICNS oficial para macOS
echo -e "\033[1;34m⚡ [Icon Pipeline]\033[0m Compilando assets/DevOpsHero.icns via iconutil..."
iconutil -c icns "$ICONSET_DIR" -o "$ICNS_OUTPUT"
echo -e "\033[1;32m✓\033[0m assets/DevOpsHero.icns gerado com sucesso."

# 3. Gerar ICO oficial para Windows a partir da renderização 1024x1024 transparente do Swift
echo -e "\033[1;34m⚡ [Icon Pipeline]\033[0m Gerando assets/DevOpsHero.ico a partir do render Swift..."
PYTHON_EXEC="python3"
if [ -f "$DIR/.venv/bin/python" ]; then
    PYTHON_EXEC="$DIR/.venv/bin/python"
fi

"$PYTHON_EXEC" -c '
import sys
from PIL import Image

src_png = sys.argv[1]
ico_dest = sys.argv[2]
im = Image.open(src_png).convert("RGBA")
sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
im.save(ico_dest, format="ICO", sizes=sizes)
' "$ICONSET_DIR/icon_512x512@2x.png" "$ICO_OUTPUT"

echo -e "\033[1;32m✓\033[0m assets/DevOpsHero.ico gerado com sucesso."
echo -e "\033[1;32m🚀 [Icon Pipeline]\033[0m Todos os ícones estão perfeitamente sincronizados com o padrão Apple Swift e assets/icon.svg!"
