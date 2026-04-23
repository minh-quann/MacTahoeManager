import subprocess
import threading
from gi.repository import Gtk, Adw, GLib
from mactahoe_manager.config import REPO_DIR

class SettingsPage:
    def __init__(self, app_window):
        self.win = app_window
        self.page = Adw.PreferencesPage()
        self.page.set_icon_name("preferences-desktop-appearance-symbolic")
        self.page.set_title("Cài đặt")

        self.ACCENTS = ["default", "blue", "purple", "pink", "red", "orange", "yellow", "green", "grey", "all"]

        self._build_ui()

    def get_page(self):
        return self.page

    def _build_ui(self):
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

        row_update = Adw.ActionRow(title="Cập nhật mã nguồn")
        btn_update = Gtk.Button(label="Cập nhật (Pull)")
        btn_update.add_css_class("pill")
        btn_update.set_valign(Gtk.Align.CENTER)
        btn_update.connect("clicked", self.on_update_clicked)
        row_update.add_suffix(btn_update)
        group_actions.add(row_update)

        row_uninstall = Adw.ActionRow(title="Gỡ cài đặt hoàn toàn")
        btn_uninstall = Gtk.Button(label="Gỡ (Uninstall)")
        btn_uninstall.add_css_class("destructive-action")
        btn_uninstall.add_css_class("pill")
        btn_uninstall.set_valign(Gtk.Align.CENTER)
        btn_uninstall.connect("clicked", self.on_uninstall_clicked)
        row_uninstall.add_suffix(btn_uninstall)
        group_actions.add(row_uninstall)

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

    def on_install_clicked(self, btn):
        if not self.row_light.get_active() and not self.row_dark.get_active():
            dialog = Adw.MessageDialog(transient_for=self.win, heading="Cảnh báo", body="Vui lòng chọn ít nhất một biến thể màu!")
            dialog.add_response("ok", "OK")
            dialog.present()
            return

        args = self._build_install_args()
        
        def run_install():
            try:
                subprocess.run(args, cwd=REPO_DIR, check=True)
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

    def on_update_clicked(self, btn):
        def run_update():
            try:
                subprocess.run(["git", "pull"], cwd=REPO_DIR, check=True)
                GLib.idle_add(self.show_success, "Đã cập nhật mã nguồn thành công!")
            except Exception as e:
                GLib.idle_add(self.show_error, str(e))
                
        btn.set_sensitive(False)
        btn.set_label("Đang pull...")
        
        thread = threading.Thread(target=run_update, daemon=True)
        thread.start()
        
        def restore_btn():
            btn.set_sensitive(True)
            btn.set_label("Cập nhật (Pull)")
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
                    subprocess.run(["./install.sh", "-r"], cwd=REPO_DIR, check=True)
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
