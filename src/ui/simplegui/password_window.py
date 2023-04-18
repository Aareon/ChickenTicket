from pathlib import Path

import PySimpleGUI as sg

HERE_DIR = Path(__file__).parent
UI_DIR = HERE_DIR.parent
SRC_DIR = UI_DIR.parent
IMAGES_DIR = SRC_DIR.parent / "images"


class PasswordWindow:
    def __init__(self, parent=None) -> None:
        self.parent = parent
        self.title = "ChickenTicket - Password"
        self.setup()
        self.window = sg.Window(self.title, self.layout)

    def setup(self) -> None:
        # fmt: off
        self.layout = [
            [sg.Text("Enter a password: "), sg.Input(size=(30, 10), key="-pass1-", password_char='*')],
            [sg.Push(), sg.Text("Confirm: "), sg.Input(size=(30, 10), key="-pass2-", password_char='*')],
            [sg.Push(), sg.Button("Next", key="-next-")]
        ]
        # fmt: on


if __name__ == "__main__":
    import sys

    class FakeApp:
        nconns = 99
        AVAILABLE = 99
        PENDING = 101
        height = 999
        IN_SYNC = True

    app = FakeApp()
    win = PasswordWindow(app)
    while True:
        event, values = win.window.read()
        if event in (sg.WIN_CLOSED, "-cancel-"):
            break
    win.window.close()
    sys.exit(0)
