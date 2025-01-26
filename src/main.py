# main.py
#
# Copyright 2025 yucef sourani
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Gst', '1.0')
from gi.repository import Gtk, Gio, Adw,Gst
from .window import AlbasheerWindow
Gst.init(None)

class AlbasheerApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(application_id='com.github.yucefsourani.albasheer-electronic-quran-browser',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('about', self.on_about_action)


    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        win = self.props.active_window
        if not win:
            win = AlbasheerWindow(application=self)
        win.present()

    def on_about_action(self, *args):
        """Callback for the app.about action."""
        about = Adw.AboutDialog(application_name='albasheer',
                                application_icon='com.github.yucefsourani.albasheer-electronic-quran-browser',
                                developer_name='yucef sourani',
                                website='https://github.com/yucefsourani/albasheer-electronic-quran-browser',
                                version='3.0',
                                developers=['yucef sourani'],
                                copyright='© 2025 yucef sourani')
        about.set_comments("Electronic Mus-haf")
        about.set_license("""
        Released under terms of Waqf Public License.
        This program is free software; you can redistribute it and/or modify
        it under the terms of the latest version Waqf Public License as
        published by Ojuba.org.

        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

        The Latest version of the license can be found on
        "https://ojuba.org/waqf:license/"

        """)
        about.add_credit_section("Based on/Special thanks",["Othman Electronic Quran Browser","https://github.com/ojuba-org/othman"])
        about.add_credit_section("Special thanks",["Amiri Font","https://www.amirifont.org/"])
        about.add_credit_section("This program uses ",["Ayat to provides tilawa/tafasir/tarajem","https://quran.ksu.edu.sa/ayat/"])
        # Translators: Replace "translator-credits" with your name/username, and optionally an email or URL.
        about.set_translator_credits(_('translator-credits'))
        about.present(self.props.active_window)


    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


def main(version):
    """The application's entry point."""
    app = AlbasheerApplication()
    return app.run(sys.argv)
