import os

from kivy.app import App
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.utils import platform
from plyer import filechooser

if platform == 'android':
    from jnius import autoclass, cast
    from android import mActivity, api_version

    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Environment = autoclass('android.os.Environment')
    Intent = autoclass('android.content.Intent')
    Settings = autoclass('android.provider.Settings')
    Uri = autoclass('android.net.Uri')
    File = autoclass('java.io.File')
    CurrentActivity = cast('android.app.Activity', PythonActivity.mActivity)


class MyApp(App):
    def build(self):
        layout = BoxLayout(padding=50, orientation='vertical')
        delete_media_btn = DeleteMediaButton()
        location_btn = ToggleLocationButton()
        airplane_mode_btn = ToggleAirplaneModeButton()

        layout.add_widget(delete_media_btn)
        layout.add_widget(location_btn)
        layout.add_widget(airplane_mode_btn)

        return layout


class DeleteMediaButton(Button):
    selection = ListProperty([])

    def select(self):
        if platform == 'android' and api_version >= 30 and not Environment.isExternalStorageManager():
            # If permissions not granted, request for file access permissions
            # WARNING: Permission request for API_LEVEL < 30 is not handled
            try:
                activity = mActivity.getApplicationContext()
                uri = Uri.parse('package:' + activity.getPackageName())
                intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION, uri)
                CurrentActivity.startActivity(intent)
            except Exception:
                intent = Intent(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION)
                CurrentActivity.startActivity(intent)
        else:
            # Open build-in file chooser
            filechooser.open_file(on_selection=self.handle_file_selection)

    def handle_file_selection(self, selection):
        self.selection = selection

    def on_selection(self, *a, **k):
        # Delete the file and refresh media cache

        for item in self.selection:
            if platform == 'android':
                selected_file = File(item)
                selected_file.delete()
                intent = Intent(Intent.ACTION_MEDIA_SCANNER_SCAN_FILE)
                intent.setData(Uri.fromFile(selected_file))
                CurrentActivity.sendBroadcast(intent)
            else:
                os.remove(item)

    text = 'Delete selected media'
    on_release = select


class ToggleLocationButton(Button):
    def show_location_settings(self):
        # Redirect to the location source settings page

        if platform == 'android':
            intent = Intent(Settings.ACTION_LOCATION_SOURCE_SETTINGS)
            CurrentActivity.startActivity(intent)

    text = 'Toggle location service'
    on_release = show_location_settings


class ToggleAirplaneModeButton(Button):
    def show_airplane_mode_settings(self):
        # Redirect to the airplane mode settings page

        if platform == 'android':
            intent = Intent(Settings.ACTION_AIRPLANE_MODE_SETTINGS)
            CurrentActivity.startActivity(intent)

    text = 'Toggle airplane mode'
    on_release = show_airplane_mode_settings


if __name__ == '__main__':
    MyApp(title='My Application').run()
