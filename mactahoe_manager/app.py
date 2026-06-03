import os
from gi.repository import Adw
import mactahoe_manager.config as cfg
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
        # Clear all current pages
        while True:
            page = self.win.get_visible_page()
            if page:
                self.win.remove(page)
            else:
                break

        # Re-discover repo location each time
        cfg.REPO_DIR = cfg.find_repo_dir()
        repo_exists = os.path.isfile(os.path.join(cfg.REPO_DIR, "install.sh"))

        if repo_exists:
            # Repo found → show settings page
            settings = SettingsPage(self.win)
            self.win.add(settings.get_page())
        else:
            # No repo → show clone page
            clone = ClonePage(self.win, on_success_callback=self.check_repo_state)
            self.win.add(clone.get_page())
