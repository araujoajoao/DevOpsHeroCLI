#!/usr/bin/env bash
# scripts/install_linux.sh - Instalador Nativo DevOpsHero para Linux (Desktop Launcher & PATH)
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo -e "\033[1;34m⚡ [DevOpsHero Linux Installer]\033[0m Configurando integração nativa..."

APPS_DIR="$HOME/.local/share/applications"
ICONS_DIR="$HOME/.local/share/icons/hicolor/scalable/apps"
BIN_DIR="$HOME/.local/bin"

mkdir -p "$APPS_DIR" "$ICONS_DIR" "$BIN_DIR"

# 1. Instalar ícone oficial
cp "$DIR/assets/icon.svg" "$ICONS_DIR/devopshero.svg"
echo -e "\033[1;32m✓\033[0m Ícone copiado para $ICONS_DIR/devopshero.svg"

# 2. Instalar wrapper no PATH de usuário
cat << 'EOF' > "$BIN_DIR/dh"
#!/usr/bin/env bash
REPO_DIR="%%REPO_DIR%%"
exec "$REPO_DIR/dh" "$@"
EOF
sed -i.bak "s|%%REPO_DIR%%|$DIR|g" "$BIN_DIR/dh" && rm -f "$BIN_DIR/dh.bak"
chmod +x "$BIN_DIR/dh"
ln -sf "$BIN_DIR/dh" "$BIN_DIR/devopshero"
echo -e "\033[1;32m✓\033[0m Comando 'dh' e 'devopshero' vinculados em $BIN_DIR"

# 3. Criar arquivo .desktop
cat << EOF > "$APPS_DIR/devopshero.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=DevOpsHero
GenericName=DevOps & SRE Terminal RPG
Comment=Jogo terminal TUI com 80 missões de incidentes reais
Icon=devopshero
Exec=$BIN_DIR/dh
Terminal=true
Categories=Game;Development;System;Utility;
Keywords=devops;sre;terminal;game;tui;kubernetes;linux;cloud;
StartupNotify=true
EOF
chmod +x "$APPS_DIR/devopshero.desktop"

# Atualizar database de aplicativos se o comando existir
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APPS_DIR" >/dev/null 2>&1 || true
fi

echo -e "\033[1;32m✓\033[0m Atalho de aplicativo criado em $APPS_DIR/devopshero.desktop"
echo ""
echo -e "\033[1;32m🚀 DevOpsHero instalado com sucesso no Linux!\033[0m"
echo -e " • Você já pode buscar por \033[1;36mDevOpsHero\033[0m no menu de programas do Gnome/KDE."
echo -e " • Ou digitar \033[1;36mdh\033[0m em qualquer novo terminal."
