import os
import subprocess
import threading
from gi.repository import Gtk, Adw, GLib
from mactahoe_manager.config import REPO_URL, REPO_DIR

class ClonePage:
    def __init__(self, app_window, on_success_callback):
        self.win = app_window
        self.on_success_callback = on_success_callback
        self.page = Adw.PreferencesPage()
        self.page.set_title("Kho lưu trữ (Repository)")
        self.page.set_icon_name("folder-download-symbolic")

        status = Adw.StatusPage()
        status.set_title("Tải mã nguồn")
        status.set_description(f"Cần tải mã nguồn của MacTahoe Theme từ GitHub về máy trước khi cài đặt.\nThư mục lưu trữ: {REPO_DIR}")
        status.set_icon_name("network-server-symbolic")
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_halign(Gtk.Align.CENTER)
        
        self.clone_btn = Gtk.Button(label="Tải về (Clone Repo)")
        self.clone_btn.add_css_class("suggested-action")
        self.clone_btn.add_css_class("pill")
        self.clone_btn.set_size_request(200, -1)
        self.clone_btn.connect("clicked", self.on_clone_clicked)
        
        self.spinner = Gtk.Spinner()
        
        box.append(self.clone_btn)
        box.append(self.spinner)
        
        status.set_child(box)
        
        group = Adw.PreferencesGroup()
        group.add(status)
        self.page.add(group)

    def get_page(self):
        return self.page

    def on_clone_clicked(self, btn):
        self.clone_btn.set_sensitive(False)
        self.spinner.start()
        self.clone_btn.set_label("Đang tải...")
        
        def clone_thread():
            try:
                os.makedirs(os.path.dirname(REPO_DIR), exist_ok=True)
                if not os.path.exists(os.path.join(REPO_DIR, ".git")):
                    subprocess.run(["git", "clone", REPO_URL, REPO_DIR], check=True)
                else:
                    subprocess.run(["git", "pull"], cwd=REPO_DIR, check=True)
                GLib.idle_add(self.on_clone_success)
            except Exception as e:
                GLib.idle_add(self.on_clone_error, str(e))
                
        threading.Thread(target=clone_thread, daemon=True).start()

    def on_clone_success(self):
        self.spinner.stop()
        if self.on_success_callback:
            self.on_success_callback()

    def on_clone_error(self, err):
        self.spinner.stop()
        self.clone_btn.set_sensitive(True)
        self.clone_btn.set_label("Thử lại")
        
        dialog = Adw.MessageDialog(transient_for=self.win, heading="Lỗi", body=f"Không thể tải mã nguồn: {err}")
        dialog.add_response("ok", "Đóng")
        dialog.present()
