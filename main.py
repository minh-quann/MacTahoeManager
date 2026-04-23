import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from mactahoe_manager.app import MacTahoeManagerApp

if __name__ == '__main__':
    app = MacTahoeManagerApp()
    app.run(sys.argv)
