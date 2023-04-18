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
        word_list = generate_recovery_phrase()
        self.layout = [
            [sg.Text("Recovery Phrase", font=("Arial 12 bold"))],
            [sg.Text("Write the following words down somewhere safe!\nThis will be used to recover your wallet if you ever lock yourself out or lose the file.")],
            [sg.Multiline(" ".join(w for w in word_list), no_scrollbar=True, size=(30, 3), disabled=True, key='-words-')],
            [sg.Button("Refresh", key="-refresh-"), sg.HSeparator(), sg.Button("Next", key="-next-")]
        ]
        # fmt: on


if __name__ == "__main__":
    import sys

    class FakeApp:
        pass

    app = FakeApp()
    win = RecoveryPhraseWindow(app)
    while True:
        event, values = win.window.read()
        if event in (sg.WIN_CLOSED, "-cancel-"):
            break
    win.window.close()
    sys.exit(0)
