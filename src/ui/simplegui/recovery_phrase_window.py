from pathlib import Path
from random import randint

import PySimpleGUI as sg

HERE_DIR = Path(__file__).parent
UI_DIR = HERE_DIR.parent
SRC_DIR = UI_DIR.parent
IMAGES_DIR = SRC_DIR.parent / "images"


def generate_recovery_phrase(nwords=12):
    """Generate a 12 item list of words for recovery phrase"""
    with open(SRC_DIR / "mnemonics.txt", "r") as f:
        words = f.read().splitlines()
        word_list = []
        for _ in range(0, nwords):
            r = randint(0, len(words))
            while words[r] in word_list:
                r = randint(0, len(words))
            else:
                word_list.append(words[r])
        return word_list


class RecoveryPhraseWindow:
    def __init__(self, parent=None) -> None:
        self.parent = parent
        self.title = "ChickenTicket - Recovery Phrase"
        self.setup()
        self.window = sg.Window(self.title, self.layout)

    def setup(self) -> None:
        # fmt: off
        self.layout = [
            [sg.Text("Recovery Phrase", font=("Arial 12 bold"))],
            [sg.Text("Write the following words down somewhere safe!\nThis will be used to recover your wallet if you ever lock yourself out or lose the file.")],
            [sg.Multiline(" ".join(w for w in self.parent.word_list), no_scrollbar=True, size=(30, 3), disabled=True, key='-words-')],
            [sg.Button("Refresh", key="-refresh-"), sg.HSeparator(), sg.Button("Next", key="-next-")]
        ]
        # fmt: on


class ConfirmRecoveryPhraseWindow:
    def __init__(self, parent=None) -> None:
        self.parent = parent
        self.title = "ChickenTicket - Confirm Recovery Phrase"
        self.setup()
        self.window = sg.Window(self.title, self.layout)
    
    def setup(self) -> None:
        rows = [[], [], []]
        x = 0
        for i in range(3):
            for j in range(4):
                n = randint(0, len(self.parent.word_list) - 1)
                rows[i].append(sg.Button(self.parent.word_list.pop(n), key=f"-word{x}-"))
                x += 1
        # fmt: off
        self.layout = [
            [sg.Text("Confirm your recovery phrase", font=("Arial 10 bold"))],
            [sg.Multiline(no_scrollbar=True, disabled=True, size=(30, 3), key="-words-")],
            rows,
            [sg.HSeparator()],
            [sg.Button("Reset", key="-reset-"), sg.HSeparator(), sg.Button("Confirm", disabled=True, key="-confirm-")]
        ]
        # fmt: on


if __name__ == "__main__":
    import sys

    class FakeApp:
        word_list = generate_recovery_phrase()

    app = FakeApp()
    win = RecoveryPhraseWindow(app)
    while True:
        event, values = win.window.read()
        if event in (sg.WIN_CLOSED, "-cancel-"):
            break
    win.window.close()

    win = ConfirmRecoveryPhraseWindow(app)
    while True:
        event, values = win.window.read()
        if event in (sg.WIN_CLOSED, "-cancel-"):
            break
    win.window.close()
    sys.exit(0)
