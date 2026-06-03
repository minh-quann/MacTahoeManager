#!/bin/bash
set -e

APP_DIR="$HOME/Documents/MacTahoeManager"
BIN_DIR="$HOME/.local/bin"
APP_SHARE_DIR="$HOME/.local/share/applications"

echo "🔄 Đang cập nhật MacTahoe Manager..."
echo ""

# ── Step 1: Pull latest code ──
echo "📥 Bước 1: Tải mã nguồn mới nhất..."
cd "$APP_DIR"

# Show current version before update
OLD_HASH=$(git rev-parse --short HEAD 2>/dev/null || echo "N/A")
echo "   Phiên bản hiện tại: $OLD_HASH"

git pull origin main
NEW_HASH=$(git rev-parse --short HEAD 2>/dev/null || echo "N/A")
echo "   Phiên bản mới:      $NEW_HASH"

if [ "$OLD_HASH" = "$NEW_HASH" ]; then
    echo "   ℹ️  Đã ở phiên bản mới nhất, không có thay đổi."
else
    echo "   📋 Các thay đổi:"
    git log --oneline "${OLD_HASH}..${NEW_HASH}" 2>/dev/null | while read -r line; do
        echo "      • $line"
    done
fi
echo ""

# ── Step 2: Uninstall old version ──
echo "🗑️  Bước 2: Gỡ cài đặt phiên bản cũ..."

if [ -f "$BIN_DIR/mactahoe_manager" ]; then
    rm "$BIN_DIR/mactahoe_manager"
    echo "   ✓ Đã xóa shortcut ($BIN_DIR/mactahoe_manager)"
fi

if [ -f "$APP_SHARE_DIR/mactahoe-manager.desktop" ]; then
    rm "$APP_SHARE_DIR/mactahoe-manager.desktop"
    echo "   ✓ Đã xóa .desktop entry"
fi
echo ""

# ── Step 3: Clear Python cache ──
echo "🧹 Bước 3: Dọn cache..."
find "$APP_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
echo "   ✓ Đã xóa __pycache__"
echo ""

# ── Step 4: Reinstall ──
echo "📦 Bước 4: Cài đặt lại..."

mkdir -p "$BIN_DIR"
mkdir -p "$APP_SHARE_DIR"

# Create shell wrapper
WRAPPER="$BIN_DIR/mactahoe_manager"
cat <<EOF > "$WRAPPER"
#!/bin/bash
export PYTHONPATH="\$PYTHONPATH:$APP_DIR"
python3 "$APP_DIR/main.py" "\$@"
EOF
chmod +x "$WRAPPER"
echo "   ✓ Đã tạo shortcut ($WRAPPER)"

# Create .desktop file
DESKTOP_FILE="$APP_SHARE_DIR/mactahoe-manager.desktop"
cat <<EOF > "$DESKTOP_FILE"
[Desktop Entry]
Name=MacTahoe Theme Manager
Comment=Manage and install the MacTahoe GTK Theme
Exec=$WRAPPER
Icon=$APP_DIR/mactahoe-manager-icon.svg
Terminal=false
Type=Application
Categories=Utility;Settings;
EOF
echo "   ✓ Đã tạo .desktop entry"

update-desktop-database "$APP_SHARE_DIR"
echo ""

echo "✅ Cập nhật MacTahoe Manager thành công! ($OLD_HASH → $NEW_HASH)"
