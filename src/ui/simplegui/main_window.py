from pathlib import Path

import PySimpleGUI as sg

HERE_DIR = Path(__file__).parent
UI_DIR = HERE_DIR.parent
SRC_DIR = UI_DIR.parent
IMAGES_DIR = SRC_DIR.parent / "images"


class MainWindow:
    def __init__(self, parent=None) -> None:
        self.parent = parent
        self.title = "ChickenTicket"
        self.setup()
        self.window = sg.Window(self.title, self.layout)
    
    def setup(self) -> None:
        # fmt: off
        sync_text = "(Out of sync)" if not self.parent.IN_SYNC else "(In sync)"
        sync_text_color = "#f00" if not self.parent.IN_SYNC else "#0f0"
        self.layout = [  # main layout
            [sg.Text("Wallet", font="Arial 14 bold"), sg.Text(sync_text, text_color=sync_text_color, key='-sync-')],
            # TODO: add a table for recent transactions
            [sg.Text("Balances", font="Arial 12 bold"), sg.Push(), sg.Text("Recent Transactions", font=("Arial 12 bold"))],
            [sg.Text("Available:"), sg.Text(f"{self.parent.AVAILABLE} CHKN", font=("Arial 10 bold"), key='-available-')],
            [sg.Text("Pending:"), sg.Text(f"{self.parent.PENDING} CHKN", font=("Arial 10 bold"), key='-pending-')],
            [sg.HSeparator()],
            [sg.Text("Total:"), sg.Text(f"{self.parent.AVAILABLE + self.parent.PENDING} CHKN", font=("Arial 10 bold"), key='-total-')],
            [sg.Button("Send", key="-send-"), sg.VSeperator(), sg.Button("Receive", key="-receive-"), sg.VSeperator(), sg.Button("Settings", key='-settings-')],
            [sg.Text(f"Height: {self.parent.height}", font="Arial 9"), sg.ProgressBar(100, orientation='h', size=(20, 20), key='-sync progress-'), sg.Text(f"{self.parent.nconns} connections", key='-connections-')]
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
    win = MainWindow(app)
    while True:
        event, values = win.window.read()
        if event in (sg.WIN_CLOSED, "-cancel-"):
            break
    win.window.close()
    sys.exit(0)