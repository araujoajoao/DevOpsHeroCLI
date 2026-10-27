#!/usr/bin/env bash
# scripts/build_macos_app.sh - Gera o DevOpsHero.app e DevOpsHero.dmg nativo para macOS
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo -e "\033[1;34m⚡ [macOS Packager]\033[0m Iniciando empacotamento do DevOpsHero para macOS..."

# 1. Validação de Sistema Operacional
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "\033[1;31m[ERRO]\033[0m Este script requer macOS para utilizar iconutil, sips e hdiutil."
    exit 1
fi

DIST_DIR="$DIR/dist"
APP_NAME="DevOpsHero"
APP_BUNDLE="$DIST_DIR/$APP_NAME.app"
DMG_OUTPUT="$DIST_DIR/$APP_NAME.dmg"
ICNS_FILE="$DIR/assets/DevOpsHero.icns"

mkdir -p "$DIST_DIR"

# 2. Gerar o arquivo .icns em alta resolução a partir do icon.svg (se necessário)
echo -e "\033[1;34m⚡ [macOS Packager]\033[0m Gerando ícone Apple ICNS (16x16 até 1024x1024 Retina)..."
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

qlmanage -t -s 1024 -o "$TEMP_DIR" "$DIR/assets/icon.svg" >/dev/null 2>&1
BASE_PNG="$TEMP_DIR/icon.svg.png"

if [ ! -f "$BASE_PNG" ]; then
    echo -e "\033[1;31m[ERRO]\033[0m Falha ao renderizar icon.svg para 1024px."
    exit 1
fi

ICONSET_DIR="$TEMP_DIR/DevOpsHero.iconset"
mkdir -p "$ICONSET_DIR"

sips -z 16 16     "$BASE_PNG" --out "$ICONSET_DIR/icon_16x16.png" >/dev/null 2>&1
sips -z 32 32     "$BASE_PNG" --out "$ICONSET_DIR/icon_16x16@2x.png" >/dev/null 2>&1
sips -z 32 32     "$BASE_PNG" --out "$ICONSET_DIR/icon_32x32.png" >/dev/null 2>&1
sips -z 64 64     "$BASE_PNG" --out "$ICONSET_DIR/icon_32x32@2x.png" >/dev/null 2>&1
sips -z 128 128   "$BASE_PNG" --out "$ICONSET_DIR/icon_128x128.png" >/dev/null 2>&1
sips -z 256 256   "$BASE_PNG" --out "$ICONSET_DIR/icon_128x128@2x.png" >/dev/null 2>&1
sips -z 256 256   "$BASE_PNG" --out "$ICONSET_DIR/icon_256x256.png" >/dev/null 2>&1
sips -z 512 512   "$BASE_PNG" --out "$ICONSET_DIR/icon_256x256@2x.png" >/dev/null 2>&1
sips -z 512 512   "$BASE_PNG" --out "$ICONSET_DIR/icon_512x512.png" >/dev/null 2>&1
cp "$BASE_PNG" "$ICONSET_DIR/icon_512x512@2x.png"

iconutil -c icns "$ICONSET_DIR" -o "$ICNS_FILE"
echo -e "\033[1;32m✓ [macOS Packager]\033[0m Ícone gerado com sucesso: assets/DevOpsHero.icns"

# 3. Montar a estrutura de diretórios do DevOpsHero.app
echo -e "\033[1;34m⚡ [macOS Packager]\033[0m Criando estrutura de bundle macOS ($APP_NAME.app)..."
rm -rf "$APP_BUNDLE"
mkdir -p "$APP_BUNDLE/Contents/MacOS"
mkdir -p "$APP_BUNDLE/Contents/Resources/app"

# Copiar ícone oficial
cp "$ICNS_FILE" "$APP_BUNDLE/Contents/Resources/DevOpsHero.icns"

# Criar PkgInfo
echo "APPL????" > "$APP_BUNDLE/Contents/PkgInfo"

# Criar Info.plist
cat <<EOF > "$APP_BUNDLE/Contents/Info.plist"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>pt-BR</string>
    <key>CFBundleDisplayName</key>
    <string>DevOpsHero</string>
    <key>CFBundleExecutable</key>
    <string>DevOpsHero</string>
    <key>CFBundleIconFile</key>
    <string>DevOpsHero</string>
    <key>CFBundleIconName</key>
    <string>DevOpsHero</string>
    <key>CFBundleIdentifier</key>
    <string>com.devopshero.cli</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>DevOpsHero</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

# Criar script executável macOS (Contents/MacOS/DevOpsHero)
cat <<'EOF' > "$APP_BUNDLE/Contents/MacOS/DevOpsHero"
#!/usr/bin/env bash
# macOS Application Launcher for DevOpsHeroCLI

APP_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../Resources/app" && pwd )"

# Abre no iTerm2 (se disponível) ou no Terminal.app nativo do macOS
if [ -d "/Applications/iTerm.app" ] || osascript -e 'id of application "iTerm"' >/dev/null 2>&1; then
    osascript <<SCRIPT
    tell application "iTerm"
        activate
        try
            set newWin to (create window with default profile command "bash -c 'cd \"$APP_DIR\" && ./dh; exec bash'")
        on error
            tell current window
                create tab with default profile command "bash -c 'cd \"$APP_DIR\" && ./dh; exec bash'"
            end tell
        end try
    end tell
SCRIPT
else
    osascript <<SCRIPT
    tell application "Terminal"
        activate
        do script "cd \"$APP_DIR\" && ./dh"
    end tell
SCRIPT
fi
EOF

chmod +x "$APP_BUNDLE/Contents/MacOS/DevOpsHero"

# 4. Copiar o código fonte necessário para dentro do pacote
echo -e "\033[1;34m⚡ [macOS Packager]\033[0m Empacotando aplicação e arquivos estritamente necessários..."
cp -R "$DIR/devopsherocli" "$APP_BUNDLE/Contents/Resources/app/"
cp -R "$DIR/assets" "$APP_BUNDLE/Contents/Resources/app/"
cp "$DIR/pyproject.toml" "$APP_BUNDLE/Contents/Resources/app/"
cp "$DIR/README.md" "$APP_BUNDLE/Contents/Resources/app/"
cp "$DIR/dh" "$APP_BUNDLE/Contents/Resources/app/"
chmod +x "$APP_BUNDLE/Contents/Resources/app/dh"

echo -e "\033[1;32m✓ [macOS Packager]\033[0m Aplicativo construído: dist/$APP_NAME.app"

# 5. Criar o instalador DMG com atalho de arrastar para /Applications
echo -e "\033[1;34m⚡ [macOS Packager]\033[0m Gerando instalador disk image (.dmg)..."
DMG_STAGING="$TEMP_DIR/dmg_staging"
mkdir -p "$DMG_STAGING"

# Copia o .app para a raiz do DMG
cp -R "$APP_BUNDLE" "$DMG_STAGING/"

# Cria o link simbólico padrão do macOS para /Applications
ln -s /Applications "$DMG_STAGING/Applications"

# Remove DMG anterior se existir
rm -f "$DMG_OUTPUT"

# Gera o arquivo .dmg comprimido com hdiutil
hdiutil create -volname "DevOpsHero" \
               -srcfolder "$DMG_STAGING" \
               -ov \
               -format UDZO \
               "$DMG_OUTPUT" >/dev/null

echo -e "\033[1;32m✓ [macOS Packager]\033[0m Instalador criado com sucesso: dist/$APP_NAME.dmg"
echo ""
echo -e "\033[1;35m========================================================================\033[0m"
echo -e " 🚀 \033[1;32mDevOpsHeroCLI Instalador macOS Pronto!\033[0m"
echo -e " • Aplicativo direto: \033[1;36mdist/DevOpsHero.app\033[0m"
echo -e " • Imagem de disco:   \033[1;36mdist/DevOpsHero.dmg\033[0m"
echo ""
echo -e " Para instalar no seu Mac:"
echo -e "   1. Abra o arquivo \033[1;33mdist/DevOpsHero.dmg\033[0m no Finder."
echo -e "   2. Arraste o ícone do \033[1;32mDevOpsHero\033[0m para a pasta \033[1;34mApplications\033[0m."
echo -e "   Ou copie diretamente via terminal:"
echo -e "   \033[1;37mcp -R dist/DevOpsHero.app /Applications/\033[0m"
echo -e "\033[1;35m========================================================================\033[0m"
