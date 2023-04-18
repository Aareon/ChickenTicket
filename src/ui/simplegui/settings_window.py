from pathlib import Path

import PySimpleGUI as sg

HERE_DIR = Path(__file__).parent
UI_DIR = HERE_DIR.parent
SRC_DIR = UI_DIR.parent
IMAGES_DIR = SRC_DIR.parent / "images"


class SettingsWindow:
    def __init__(self, parent=None) -> None:
        self.parent = parent
        self.title = "ChickenTicket - Settings"
        self.setup()
        self.window = sg.Window(self.title, self.layout)

    def setup(self) -> None:
        theme_name_list = sg.theme_list()
        # fmt: off
        self.layout = [  # settings window layout
            [sg.Text("Look and Feel", font="Arial 12 bold")],
            [sg.Text("UI Theme", font="Arial 10"), sg.Listbox(theme_name_list, default_values=[sg.user_settings_get_entry("-theme-")], size=(15, 10), key="-theme_choice-")],
            [sg.Push(), sg.Button("Apply", key="-apply-"), sg.Button("Done", key="-done-")],
        ]
        # fmt: on


if __name__ == "__main__":
    import sys

    class FakeApp:
        pass

    app = FakeApp()
    win = SettingsWindow(app)
    while True:
        event, values = win.window.read()
        if event in (sg.WIN_CLOSED, "-cancel-"):
            break
    win.window.close()
    sys.exit(0)
