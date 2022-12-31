from kivy.app import App
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
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

    # WARNING: Permission request for API_LEVEL < 30 is not handled
    if api_version >= 30 and not Environment.isExternalStorageManager():
        try:
            activity = mActivity.getApplicationContext()
            uri = Uri.parse('package:' + activity.getPackageName())
            intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION, uri)
            currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
            currentActivity.startActivityForResult(intent, 101)
        except:
            intent = Intent()
            intent.setAction(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION)
            currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
            currentActivity.startActivityForResult(intent, 101)


class MyApp(App):
    filepath = Label()

    def build(self):
        layout = BoxLayout(orientation='vertical')
        delete_media_btn = DeleteMediaButton()
        gps_btn = ToggleLocationServiceButton()
        airplane_mode_btn = ToggleAirplaneModeButton()

        # layout.add_widget(self.filepath) # Show selected filepath for debugging
        layout.add_widget(delete_media_btn)
        layout.add_widget(gps_btn)
        layout.add_widget(airplane_mode_btn)
        return layout


class DeleteMediaButton(Button):
    selection = ListProperty([])

    def select(self):
        filechooser.open_file(on_selection=self.handle_file_selection)

    def handle_file_selection(self, selection):
        App.get_running_app().filepath.text = str(selection)
        self.selection = selection

    def on_selection(self, *a, **k):
        for item in self.selection:
            # Delete the file and refresh media cache
            if platform == 'android':
                from jnius import autoclass, cast

                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                File = autoclass('java.io.File')

                selected_file = File(item)
                selected_file.delete()

                intent = Intent()
                intent.setAction(Intent.ACTION_MEDIA_SCANNER_SCAN_FILE)
                intent.setData(Uri.fromFile(selected_file))
                currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
                currentActivity.sendBroadcast(intent)

    text = 'Delete selected media'
    on_release = select


class ToggleLocationServiceButton(Button):
    def show_location_settings(self):
        if platform == 'android':
            from jnius import autoclass, cast

            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            Settings = autoclass('android.provider.Settings')
            
            # Redirect to the location source settings page
            intent = Intent(Settings.ACTION_LOCATION_SOURCE_SETTINGS)
            currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
            currentActivity.startActivity(intent)

    text = 'Toggle location service'
    on_release = show_location_settings


class ToggleAirplaneModeButton(Button):
    def show_airplane_mode_settings(self):
        if platform == 'android':
            from jnius import autoclass, cast

            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            Settings = autoclass('android.provider.Settings')
            
            # Redirect to the airplane mode settings page
            intent = Intent()
            intent.setAction(Settings.ACTION_AIRPLANE_MODE_SETTINGS)
            currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
            currentActivity.startActivity(intent)

    text = 'Toggle airplane mode'
    on_release = show_airplane_mode_settings


if __name__ == '__main__':
    MyApp(title='My App').run()
