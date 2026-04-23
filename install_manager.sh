#!/bin/bash
set -e

APP_DIR="$HOME/Documents/MacTahoeManager"
BIN_DIR="$HOME/.local/bin"
APP_SHARE_DIR="$HOME/.local/share/applications"

mkdir -p "$BIN_DIR"
mkdir -p "$APP_SHARE_DIR"

# Create a shell wrapper in local bin
WRAPPER="$BIN_DIR/mactahoe_manager"
cat <<EOF > "$WRAPPER"
#!/bin/bash
export PYTHONPATH="\$PYTHONPATH:$APP_DIR"
python3 "$APP_DIR/main.py" "\$@"
EOF
chmod +x "$WRAPPER"

# Create .desktop file dynamically
DESKTOP_FILE="$APP_SHARE_DIR/mactahoe-manager.desktop"
cat <<EOF > "$DESKTOP_FILE"
[Desktop Entry]
Name=MacTahoe Theme Manager
Comment=Manage and install the MacTahoe GTK Theme
Exec=$WRAPPER
Icon=preferences-desktop-appearance
Terminal=false
Type=Application
Categories=Utility;Settings;
EOF

update-desktop-database "$APP_SHARE_DIR"

echo "✅ Đã cập nhật và cài đặt MacTahoe Manager thành công!"
