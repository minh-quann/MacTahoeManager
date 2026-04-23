import os
from gi.repository import Adw
from mactahoe_manager.config import REPO_DIR
from mactahoe_manager.ui.clone_page import ClonePage
from mactahoe_manager.ui.settings_page import SettingsPage

class MacTahoeManagerApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id='com.github.vinceliuice.mactahoe-manager')
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = Adw.PreferencesWindow(application=app)
        self.win.set_title("MacTahoe Theme Manager")
        self.win.set_default_size(650, 780)
        self.win.set_search_enabled(False)
        
        self.check_repo_state()
        self.win.present()

    def check_repo_state(self):
        # Xóa tất cả các trang hiện tại
        while True:
            page = self.win.get_visible_page()
            if page:
                self.win.remove(page)
            else:
                break
                
        if os.path.exists(os.path.join(REPO_DIR, "install.sh")):
            settings = SettingsPage(self.win)
            self.win.add(settings.get_page())
        else:
            clone = ClonePage(self.win, on_success_callback=self.check_repo_state)
            self.win.add(clone.get_page())
