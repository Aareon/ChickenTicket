from pathlib import Path

import PySimpleGUI as sg

HERE_DIR = Path(__file__).parent
UI_DIR = HERE_DIR.parent
SRC_DIR = UI_DIR.parent
IMAGES_DIR = SRC_DIR.parent / "images"


class NewWalletWindow:
    def __init__(self, parent=None) -> None:
        self.parent = parent
        self.title = "ChickenTicket - New Wallet"
        self.setup()
        self.window = sg.Window(self.title, self.layout)

    def setup(self) -> None:
        # fmt: off
        self.layout = [  # new wallet prompt layout
            [sg.Text("Create new wallet", font="Arial 12 bold")],
            [sg.Radio("Recover from keyphrase", "RADIO", default=True, key="-radio1-", tooltip="Choose this if you have trouble remembering passwords.")],
            [sg.Radio("New with password & keyphrase", "RADIO", key="-radio2-", tooltip="This is recommended!")],
            [sg.Radio("New with no password", "RADIO", key="-radio3-", tooltip="This is not recommended!"), sg.Text("(Caution!)", text_color="red", tooltip="This is not recommended!", font="Arial 12 bold")],
            [sg.Button("Back", key="-back-"), sg.Push(), sg.Button("Next", key="-next-")]
        ]
        # fmt: on


if __name__ == "__main__":
    import sys

    class FakeApp:
        pass

    app = FakeApp()
    win = NewWalletWindow(app)
    while True:
        event, values = win.window.read()
        if event in (sg.WIN_CLOSED, "-cancel-"):
            break
    win.window.close()
    sys.exit(0)
