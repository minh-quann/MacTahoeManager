#!/bin/bash
set -e

BIN_DIR="$HOME/.local/bin"
APP_SHARE_DIR="$HOME/.local/share/applications"

echo "Đang gỡ cài đặt MacTahoe Manager..."

# Xóa script wrapper
if [ -f "$BIN_DIR/mactahoe_manager" ]; then
    rm "$BIN_DIR/mactahoe_manager"
    echo "🗑️ Đã xóa shortcut khởi chạy ($BIN_DIR/mactahoe_manager)"
fi

# Xóa file Desktop Entry
if [ -f "$APP_SHARE_DIR/mactahoe-manager.desktop" ]; then
    rm "$APP_SHARE_DIR/mactahoe-manager.desktop"
    echo "🗑️ Đã xóa file .desktop ($APP_SHARE_DIR/mactahoe-manager.desktop)"
fi

# Cập nhật lại database để xoá icon khỏi menu ứng dụng
update-desktop-database "$APP_SHARE_DIR"

echo "✅ Đã gỡ cài đặt MacTahoe Manager thành công!"
