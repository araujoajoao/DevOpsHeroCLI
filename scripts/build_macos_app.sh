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

# 2. Gerar/Atualizar ícones oficiais via pipeline Apple Swift
"$DIR/scripts/build_icons.sh"

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
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT
DMG_STAGING="$TEMP_DIR/dmg_staging"
mkdir -p "$DMG_STAGING"

# Copia o .app para a raiz do DMG
cp -R "$APP_BUNDLE" "$DMG_STAGING/"

# Configura ícone oficial no próprio volume do DMG montado
cp "$ICNS_FILE" "$DMG_STAGING/.VolumeIcon.icns"
if command -v SetFile >/dev/null 2>&1; then
    SetFile -c icnC "$DMG_STAGING/.VolumeIcon.icns" 2>/dev/null || true
    SetFile -a C "$DMG_STAGING" 2>/dev/null || true
fi

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

# Copia também para a raiz do repositório como opção principal
cp "$DMG_OUTPUT" "$DIR/DevOpsHero.dmg"

# Se o aplicativo já estiver instalado em /Applications, sincroniza imediatamente
if [ -d "/Applications/$APP_NAME.app" ]; then
    echo -e "\033[1;34m⚡ [macOS Packager]\033[0m Sincronizando /Applications/$APP_NAME.app e invalidando cache do LaunchServices..."
    rm -rf "/Applications/$APP_NAME.app"
    cp -R "$APP_BUNDLE" "/Applications/"
    touch "/Applications/$APP_NAME.app"
    if [ -x "/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister" ]; then
        /System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "/Applications/$APP_NAME.app" 2>/dev/null || true
    fi
fi

echo -e "\033[1;32m✓ [macOS Packager]\033[0m Instalador criado com sucesso: DevOpsHero.dmg (raiz) e dist/$APP_NAME.dmg"
echo ""
echo -e "\033[1;35m========================================================================\033[0m"
echo -e " 🚀 \033[1;32mDevOpsHeroCLI Instalador macOS Pronto!\033[0m"
echo -e " • Imagem de disco (Raiz): \033[1;36mDevOpsHero.dmg\033[0m"
echo -e " • Aplicativo direto:      \033[1;36mdist/DevOpsHero.app\033[0m"
echo ""
echo -e " Para instalar no seu Mac:"
echo -e "   1. Abra o arquivo \033[1;33mDevOpsHero.dmg\033[0m no Finder (ou 'open DevOpsHero.dmg')."
echo -e "   2. Arraste o ícone do \033[1;32mDevOpsHero\033[0m para a pasta \033[1;34mApplications\033[0m."
echo -e "   Ou copie diretamente via terminal:"
echo -e "   \033[1;37mcp -R dist/DevOpsHero.app /Applications/\033[0m"
echo -e "\033[1;35m========================================================================\033[0m"
