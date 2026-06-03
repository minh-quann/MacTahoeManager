import subprocess
import threading
from gi.repository import Gtk, Adw, GLib
import mactahoe_manager.config as cfg
from mactahoe_manager.core.version_checker import (
    check_version, pull_and_get_changelog,
    UpdateStatus, VersionInfo
)


class SettingsPage:
    def __init__(self, app_window):
        self.win = app_window
        self.page = Adw.PreferencesPage()
        self.page.set_icon_name("preferences-desktop-appearance-symbolic")
        self.page.set_title("Cài đặt")

        self.ACCENTS = ["default", "blue", "purple", "pink", "red", "orange", "yellow", "green", "grey", "all"]

        self._build_ui()
        # Auto-check version on page load
        self._start_version_check()

    def get_page(self):
        return self.page

    def _build_ui(self):
        # ── 0. Version Info ──
        self._build_version_section()

        # ── 1. Appearance ──
        group_colors = Adw.PreferencesGroup(title="Giao diện cơ bản (Appearance)")
        self.page.add(group_colors)

        self.row_light = Adw.SwitchRow(title="Giao diện Sáng (Light Theme)")
        self.row_light.set_active(True)
        group_colors.add(self.row_light)

        self.row_dark = Adw.SwitchRow(title="Giao diện Tối (Dark Theme)")
        self.row_dark.set_active(True)
        group_colors.add(self.row_dark)

        model_accent = Gtk.StringList.new(["Mặc định (Tahoe)", "Xanh dương (Blue)", "Tím (Purple)", "Hồng (Pink)", "Đỏ (Red)", "Cam (Orange)", "Vàng (Yellow)", "Xanh lá (Green)", "Xám (Grey)", "Tất cả (All)"])
        self.row_accent = Adw.ComboRow(title="Màu nhấn (Accent Color)", model=model_accent)
        group_colors.add(self.row_accent)

        # ── 2. Window Styling ──
        group_window = Adw.PreferencesGroup(title="Tùy chỉnh Cửa sổ (Window Styling)")
        self.page.add(group_window)

        model_opacity = Gtk.StringList.new(["Bình thường (Normal)", "Đục hoàn toàn (Solid)"])
        self.row_opacity = Adw.ComboRow(title="Độ trong suốt (Opacity)", model=model_opacity)
        group_window.add(self.row_opacity)

        model_controls = Gtk.StringList.new(["Mặc định (Normal)", "Kiểu thay thế (Alt)", "Cả hai (All)"])
        self.row_controls = Adw.ComboRow(title="Nút điều khiển (Window Controls)", model=model_controls)
        group_window.add(self.row_controls)

        self.row_round = Adw.SwitchRow(title="Ép bo tròn góc cửa sổ (Force Rounded)")
        group_window.add(self.row_round)

        self.row_libadwaita = Adw.SwitchRow(title="Áp dụng cho GTK4 / Libadwaita")
        group_window.add(self.row_libadwaita)

        # ── 3. GNOME Shell ──
        group_shell = Adw.PreferencesGroup(title="Tinh chỉnh GNOME Shell")
        self.page.add(group_shell)

        self.row_apple = Adw.SwitchRow(title="Biểu tượng Apple")
        group_shell.add(self.row_apple)

        self.row_blur = Adw.SwitchRow(title="Hỗ trợ làm mờ (Blur Support)")
        group_shell.add(self.row_blur)

        # ── 4. Actions ──
        group_actions = Adw.PreferencesGroup(title="Thực thi")
        self.page.add(group_actions)

        row_install = Adw.ActionRow(title="Tiến hành Cài đặt")
        btn_install = Gtk.Button(label="Cài đặt Theme")
        btn_install.add_css_class("suggested-action")
        btn_install.add_css_class("pill")
        btn_install.set_valign(Gtk.Align.CENTER)
        btn_install.connect("clicked", self.on_install_clicked)
        row_install.add_suffix(btn_install)
        group_actions.add(row_install)

        row_uninstall = Adw.ActionRow(title="Gỡ cài đặt hoàn toàn")
        btn_uninstall = Gtk.Button(label="Gỡ (Uninstall)")
        btn_uninstall.add_css_class("destructive-action")
        btn_uninstall.add_css_class("pill")
        btn_uninstall.set_valign(Gtk.Align.CENTER)
        btn_uninstall.connect("clicked", self.on_uninstall_clicked)
        row_uninstall.add_suffix(btn_uninstall)
        group_actions.add(row_uninstall)

    # ── Version Section ──

    def _build_version_section(self):
        """Build the version info and update section at the top of the page."""
        self.group_version = Adw.PreferencesGroup(title="Phiên bản & Cập nhật")
        self.page.add(self.group_version)

        # Local version row
        self.row_local_ver = Adw.ActionRow(
            title="Phiên bản hiện tại",
            subtitle="Đang kiểm tra..."
        )
        self.row_local_ver.set_icon_name("drive-harddisk-symbolic")
        self.group_version.add(self.row_local_ver)

        # Remote version row
        self.row_remote_ver = Adw.ActionRow(
            title="Phiên bản mới nhất",
            subtitle="Đang kiểm tra..."
        )
        self.row_remote_ver.set_icon_name("network-server-symbolic")
        self.group_version.add(self.row_remote_ver)

        # Update status row with action buttons
        self.row_update_status = Adw.ActionRow(
            title="Trạng thái",
            subtitle="Đang kiểm tra cập nhật..."
        )
        self.row_update_status.set_icon_name("emblem-synchronizing-symbolic")

        # Spinner for checking state
        self.version_spinner = Gtk.Spinner()
        self.version_spinner.start()
        self.row_update_status.add_suffix(self.version_spinner)

        # Status badge label (hidden initially)
        self.status_badge = Gtk.Label()
        self.status_badge.set_valign(Gtk.Align.CENTER)
        self.status_badge.set_visible(False)
        self.row_update_status.add_suffix(self.status_badge)

        # Check version button
        self.btn_check = Gtk.Button(icon_name="view-refresh-symbolic")
        self.btn_check.set_valign(Gtk.Align.CENTER)
        self.btn_check.set_tooltip_text("Kiểm tra phiên bản mới")
        self.btn_check.add_css_class("flat")
        self.btn_check.connect("clicked", self._on_check_clicked)
        self.btn_check.set_visible(False)
        self.row_update_status.add_suffix(self.btn_check)

        self.group_version.add(self.row_update_status)

        # Update + reinstall button row (hidden until update available)
        self.row_update_action = Adw.ActionRow(
            title="Cập nhật Theme",
            subtitle="Tải mã nguồn mới và cài đặt lại theme"
        )
        self.row_update_action.set_icon_name("software-update-available-symbolic")

        self.btn_update_theme = Gtk.Button(label="Cập nhật ngay")
        self.btn_update_theme.add_css_class("suggested-action")
        self.btn_update_theme.add_css_class("pill")
        self.btn_update_theme.set_valign(Gtk.Align.CENTER)
        self.btn_update_theme.connect("clicked", self._on_update_theme_clicked)
        self.row_update_action.add_suffix(self.btn_update_theme)

        self.row_update_action.set_visible(False)
        self.group_version.add(self.row_update_action)

    def _format_date(self, date_str):
        """Format git date string to a more readable form."""
        if not date_str:
            return "N/A"
        # Git date format: 2026-05-29 16:24:45 +0800
        try:
            parts = date_str.split(" ")
            return f"{parts[0]}  {parts[1]}"
        except Exception:
            return date_str

    def _start_version_check(self):
        """Initiate an async version check."""
        self.version_spinner.set_visible(True)
        self.version_spinner.start()
        self.status_badge.set_visible(False)
        self.btn_check.set_visible(False)
        self.row_update_action.set_visible(False)
        self.row_update_status.set_subtitle("Đang kiểm tra cập nhật...")

        check_version(cfg.REPO_DIR, lambda info: GLib.idle_add(self._on_version_checked, info))

    def _on_version_checked(self, info):
        """Callback when version check completes. Runs on main thread."""
        self.version_spinner.stop()
        self.version_spinner.set_visible(False)
        self.btn_check.set_visible(True)
        self.status_badge.set_visible(True)

        # Update local version info
        if info.local_short_hash:
            local_date = self._format_date(info.local_date)
            self.row_local_ver.set_subtitle(
                f"{info.local_short_hash}  •  {local_date}\n{info.local_message}"
            )
        else:
            self.row_local_ver.set_subtitle("Không xác định")

        # Update remote version info
        if info.remote_short_hash:
            remote_date = self._format_date(info.remote_date)
            self.row_remote_ver.set_subtitle(
                f"{info.remote_short_hash}  •  {remote_date}\n{info.remote_message}"
            )
        else:
            self.row_remote_ver.set_subtitle("Không thể kiểm tra")

        # Update status badge and action row visibility
        if info.status == UpdateStatus.UP_TO_DATE:
            self.status_badge.set_label("✓ Đã mới nhất")
            self.status_badge.add_css_class("success")
            self.row_update_status.set_subtitle("Theme đang ở phiên bản mới nhất.")
            self.row_update_status.set_icon_name("emblem-ok-symbolic")
            self.row_update_action.set_visible(False)

        elif info.status == UpdateStatus.UPDATE_AVAILABLE:
            behind_text = f"{info.commits_behind} commit" if info.commits_behind > 0 else ""
            self.status_badge.set_label(f"⬆ Có bản mới ({behind_text})" if behind_text else "⬆ Có bản mới")
            self.status_badge.add_css_class("accent")
            self.row_update_status.set_subtitle(
                f"Có {info.commits_behind} commit mới cần cập nhật." if info.commits_behind > 0
                else "Có phiên bản mới cần cập nhật."
            )
            self.row_update_status.set_icon_name("software-update-available-symbolic")
            self.row_update_action.set_visible(True)

        else:
            self.status_badge.set_label("⚠ Lỗi")
            self.status_badge.add_css_class("error")
            self.row_update_status.set_subtitle("Không thể kiểm tra cập nhật. Kiểm tra kết nối mạng.")
            self.row_update_status.set_icon_name("dialog-warning-symbolic")
            self.row_update_action.set_visible(False)

        return False

    def _on_check_clicked(self, btn):
        """Re-check version when refresh button is clicked."""
        # Remove old CSS classes from badge
        for cls in ["success", "accent", "error"]:
            self.status_badge.remove_css_class(cls)
        self._start_version_check()

    def _on_update_theme_clicked(self, btn):
        """Pull latest code and reinstall theme automatically."""
        btn.set_sensitive(False)
        btn.set_label("Đang cập nhật...")

        def run_update():
            # Step 1: Pull latest code
            success, changelog, error = pull_and_get_changelog(cfg.REPO_DIR)
            if not success:
                GLib.idle_add(self._on_update_complete, btn, False, f"Lỗi khi tải mã nguồn: {error}", [])
                return

            # Step 2: Reinstall theme with current settings
            try:
                args = self._build_install_args()
                subprocess.run(args, cwd=cfg.REPO_DIR, check=True)

                # Apply theme via gsettings
                theme_name = self._build_theme_name()
                subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", theme_name])
                subprocess.run(["gsettings", "set", "org.gnome.desktop.wm.preferences", "theme", theme_name])

                GLib.idle_add(self._on_update_complete, btn, True, theme_name, changelog)
            except Exception as e:
                GLib.idle_add(self._on_update_complete, btn, False, str(e), [])

        threading.Thread(target=run_update, daemon=True).start()

    def _on_update_complete(self, btn, success, detail, changelog):
        """Handle update completion on the main thread."""
        btn.set_sensitive(True)
        btn.set_label("Cập nhật ngay")

        if success:
            # Build success message with changelog
            msg = f"Theme [{detail}] đã được cập nhật và kích hoạt!"
            if changelog:
                msg += "\n\nCác thay đổi mới:\n"
                # Show max 10 entries to avoid overly long dialog
                for entry in changelog[:10]:
                    msg += f"  • {entry}\n"
                if len(changelog) > 10:
                    msg += f"  ... và {len(changelog) - 10} thay đổi khác"

            self.show_success(msg)
            # Re-check version to update the UI
            self._start_version_check()
        else:
            self.show_error(detail)

        return False

    # ── Build helpers ──

    def _build_theme_name(self):
        name = "MacTahoe"
        if self.row_dark.get_active(): name += "-Dark"
        else: name += "-Light"
        idx = self.row_accent.get_selected()
        if idx > 0 and idx < len(self.ACCENTS) - 1:
            name += "-" + self.ACCENTS[idx]
        return name

    def _build_install_args(self):
        args = ["./install.sh"]
        if self.row_light.get_active(): args.extend(["-c", "light"])
        if self.row_dark.get_active(): args.extend(["-c", "dark"])
        idx = self.row_accent.get_selected()
        args.extend(["-t", self.ACCENTS[idx]])
        opacity = ["normal", "solid"][self.row_opacity.get_selected()]
        args.extend(["-o", opacity])
        controls = ["normal", "alt", "all"][self.row_controls.get_selected()]
        args.extend(["-a", controls])
        if self.row_apple.get_active(): args.extend(["--shell", "-i", "apple"])
        if self.row_blur.get_active(): args.append("-b")
        if self.row_round.get_active(): args.append("--round")
        if self.row_libadwaita.get_active(): args.append("-l")
        return args

    # ── Action handlers ──

    def on_install_clicked(self, btn):
        if not self.row_light.get_active() and not self.row_dark.get_active():
            dialog = Adw.MessageDialog(transient_for=self.win, heading="Cảnh báo", body="Vui lòng chọn ít nhất một biến thể màu!")
            dialog.add_response("ok", "OK")
            dialog.present()
            return

        args = self._build_install_args()

        def run_install():
            try:
                subprocess.run(args, cwd=cfg.REPO_DIR, check=True)
                theme_name = self._build_theme_name()
                subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", theme_name])
                subprocess.run(["gsettings", "set", "org.gnome.desktop.wm.preferences", "theme", theme_name])
                GLib.idle_add(self.show_success, f"Theme [{theme_name}] đã được cài đặt và kích hoạt!")
            except Exception as e:
                GLib.idle_add(self.show_error, str(e))

        btn.set_sensitive(False)
        btn.set_label("Đang cài...")

        thread = threading.Thread(target=run_install, daemon=True)
        thread.start()

        def restore_btn():
            btn.set_sensitive(True)
            btn.set_label("Cài đặt Theme")
            return False

        GLib.timeout_add(100, lambda: restore_btn() if not thread.is_alive() else True)

    def on_uninstall_clicked(self, btn):
        dialog = Adw.MessageDialog(
            transient_for=self.win,
            heading="Xác nhận Gỡ cài đặt",
            body="Bạn có chắc chắn muốn xóa toàn bộ theme MacTahoe ra khỏi hệ thống không?"
        )
        dialog.add_response("cancel", "Hủy")
        dialog.add_response("uninstall", "Gỡ cài đặt")
        dialog.set_response_appearance("uninstall", Adw.ResponseAppearance.DESTRUCTIVE)

        def on_response(dlg, response):
            if response == "uninstall":
                try:
                    subprocess.run(["./install.sh", "-r"], cwd=cfg.REPO_DIR, check=True)
                    subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", "Adwaita"])
                    subprocess.run(["gsettings", "set", "org.gnome.desktop.wm.preferences", "theme", "Adwaita"])
                    self.show_success("Đã gỡ cài đặt và khôi phục về Adwaita!")
                except Exception as e:
                    self.show_error(str(e))

        dialog.connect("response", on_response)
        dialog.present()

    def show_success(self, msg):
        dlg = Adw.MessageDialog(transient_for=self.win, heading="Thành công", body=msg)
        dlg.add_response("ok", "Hoàn tất")
        dlg.present()

    def show_error(self, msg):
        dlg = Adw.MessageDialog(transient_for=self.win, heading="Lỗi", body=msg)
        dlg.add_response("ok", "Đóng")
        dlg.present()
