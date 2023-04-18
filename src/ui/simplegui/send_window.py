from pathlib import Path

import PySimpleGUI as sg

HERE_DIR = Path(__file__).parent
UI_DIR = HERE_DIR.parent
SRC_DIR = UI_DIR.parent
IMAGES_DIR = SRC_DIR.parent / "images"


class SendWindow:
    def __init__(self, parent=None):
        self.parent = parent
        self.title = "Send"
        self.setup()
        self.window = sg.Window(self.title, self.layout)

    def setup(self):
        # fmt: off
        self.layout = [  # send window layout
            [sg.Text("Send", font="Arial 12 bold")], [sg.Input(key="-input-"), sg.Image(str(IMAGES_DIR / "red.png"), size=(20, 20), key="-status-")],
            [sg.Text("Fee: 0.0 CHKN", key="-fee-")],  # estimated transaction fee
            [sg.HSeparator()],
            [sg.Text("Available:"), sg.Text(f"{self.parent.AVAILABLE} CHKN", font="Arial 10 bold")],
            [sg.Text("Pending:"), sg.Text(f"{self.parent.PENDING} CHKN", font="Arial 10 bold")],
            [sg.Button("Cancel", key="-cancel-"), sg.HSeparator(), sg.Button("Check", key="-check-"), sg.Button("Send", key="-send-")],
        ]
        # fmt: on


if __name__ == "__main__":
    import sys

    class FakeApp:
        AVAILABLE = 99
        PENDING = 101

    app = FakeApp()
    win = SendWindow(app)
    while True:
        event, values = win.window.read()
        if event in (sg.WIN_CLOSED, "-cancel-"):
            break
    win.window.close()
    sys.exit(0)
