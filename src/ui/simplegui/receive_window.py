from pathlib import Path

import PySimpleGUI as sg

HERE_DIR = Path(__file__).parent
UI_DIR = HERE_DIR.parent
SRC_DIR = UI_DIR.parent
IMAGES_DIR = SRC_DIR.parent / "images"


class ReceiveWindow:
    def __init__(self, parent=None) -> None:
        self.parent = parent
        self.title = "ChickenTicket - Receive"
        self.setup()
        self.window = sg.Window(self.title, self.layout)

    def setup(self) -> None:
        # fmt: off
        self.layout = [  # receive window layout
            [sg.Image(str(IMAGES_DIR / "addressqr.png"))],
            [sg.Text(f"Address: {str(self.parent.wallet.addresses[0][0])}"), sg.Button("Copy", key="-copy-")],
            [sg.Button("OK", key="-ok-")],
        ]
        # fmt: on


if __name__ == "__main__":
    # Test Note: This is a test of the ReceiveWindow class.
    # It is not a test of the ChickenTicket application.
    # To test the ChickenTicket application, run the simplegui.py file.
    # To test the ReceiveWindow class, run this file.
    # A known exception exists in this test.
    # The exception is caused by a QrCode not being found because the scope of this test
    # does not include the QrCode generation.
    import sys

    class Wallet:
        addresses = [("0x01", "0x02")]

    class FakeApp:
        wallet = Wallet()

    app = FakeApp()
    win = ReceiveWindow(app)
    while True:
        event, values = win.window.read()
        if event in (sg.WIN_CLOSED, "-cancel-"):
            break
    win.window.close()
