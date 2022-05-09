"""ChickenTicket simple GUI based on PySimpleGUI
"""
import sys
import threading
import time
from decimal import Decimal
from pathlib import Path
from random import randint

import pyperclip as clip
import PySimpleGUI as sg
import qrcode

from config import Config
from httpnode import HTTPNode
from keys import KeyPair
from wallet import Wallet

from copy import deepcopy

WALLET = None
AVAILABLE = 0
PENDING = 0

SRC_DIR = Path(__file__).parent
IMAGES_DIR = SRC_DIR.parent / "images"
PEERS_LIST = SRC_DIR.parent / "peerslist.txt"
SETTINGS_FP = SRC_DIR.parent / "sg_settings"
print(f"Images dir: {IMAGES_DIR}")

sg.user_settings_filename(path=SETTINGS_FP)
theme = sg.user_settings_get_entry("-theme-", "DarkBlue2")
sg.user_settings_set_entry("-theme-", theme)

VERSION = "0.6"
WIN_TITLE = "ChickenTicket"

# NOTE: when defining layouts, be sure to enclose it with `# fmt: off` &
# `# fmt: on` or black will screw up formatting.


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


class App:
    __name__ = "ChickenTicket simplegui"

    def __init__(self):
        self.gui_thread = threading.Thread(target=lambda: self._main())  # PySimpleGUI
        self.node_thread = None

        self.current_theme = sg.user_settings_get_entry("-theme-")

        self.wallet_fp = Config.DEFAULT_WALLET_FP
        self.wallet = None

        with open(PEERS_LIST) as f:
            self.peers_list = f.readlines()

    def run(self):
        self.gui_thread.start()

    def _main(self):
        # load or create wallet
        if not self.wallet_fp.exists():
            self.wallet_fp = Path(sg.popup_get_folder("Select wallet folder"))

            if not (self.wallet_fp / "wallet.der").exists():
                # Create new wallet
                self.show_new_wallet()
            else:
                # Loading existing wallet
                self.wallet = Wallet.load_from_der(self.wallet_fp)
        else:
            # Wallet exists in default location
            self.wallet = Wallet.load_from_der(self.wallet_fp)

        self.show_main_window()

        # create the node
        self.node = HTTPNode(
            wallet=self.wallet, config=Config, peers_list=self.peers_list
        )
        self.node.setup()
        self.node_thread = threading.Thread(
            target=lambda: node.run(), daemon=True
        )  # flask thread
        # self.node_thread.start()

    def show_main_window(self):
        self.main_window = self.make_main_window()
        while True:
            event, values = self.main_window.read()
            if event == sg.WIN_CLOSED:
                break
            if event == "-send-":  # Send popup window

                self.show_send_window()

            if event == "-receive-":  # Receive popup window
                self.show_receive_window()

            if event == "-settings-":  # settings popup window
                self.show_settings_window()

        print("Closing!")
        self.main_window.close()
        sys.exit(0)

    def connections_changed(self, nconns):
        """Called by node when number of connections changes"""
        self.main_window["-connections-"].Update(f"{nconns} connections")

    def show_recovery_phrase(self):
        title = "Recovery phrase"
        win = sg.Window(
            f"{title} - {self.__name__} {VERSION}",
            self.recovery_phrase_layout(),
        ).finalize()
        word_list = generate_recovery_phrase()
        win["-words-"].update(" ".join(w for w in word_list))
        while True:
            event, values = win.read()
            if event == sg.WIN_CLOSED:
                # TODO create method to confirm exit
                if sg.popup("Are you sure you want to exit?", button_type=1) == "Yes":
                    sys.exit(0)
                else:
                    self.show_recovery_phrase()
            elif event == "-refresh-":
                self.show_recovery_phrase()
            elif event == "-next-":
                break
        win.close()
        return word_list

    def show_confirm_phrase(self, word_list):
        title = "Confirm recovery phrase"
        words = deepcopy(word_list)
        win = sg.Window(
            f"{title} - {self.__name__} {VERSION}",
            self.confirm_recovery_phrase_layout(word_list),
        )

        phrase = " ".join(words)
        words = ""
        while True:
            event, values = win.read()
            if event == sg.WIN_CLOSED:
                if sg.popup("Are you sure you want to exit?", button_type=1) == "Yes":
                    sys.exit(1)
            elif "-word" in event and event != "-words-":
                words += f"{win[event].get_text()} "
                win["-words-"].update(f"{words}")
                win[event].update(disabled=True)
                if words.rstrip() == phrase:
                    win["-confirm-"].update(disabled=False)
            elif event == "-reset-":
                words = ""
                win["-words-"].update("")
                for i in range(0, 12):
                    win[f"-word{i}-"].update(disabled=False)
            elif event == "-confirm-":
                # phrase entered correctly
                break
        win.close()
        return phrase

    def make_main_window(self):
        return sg.Window(f"{self.__name__} {VERSION}", self.main_window_layout())

    def show_send_window(self):
        title = "Send"
        win = sg.Window(
            f"{title} - {self.__name__} {VERSION}", self.send_window_layout()
        )
        while True:  # send window loop
            event, vals = win.read()
            if event == "-cancel-" or event == sg.WIN_CLOSED:
                break
            if event == "-check-":
                try:
                    if Decimal(vals["-input-"]) <= Decimal(0):
                        win["-status-"].Update(
                            str(IMAGES_DIR / "orange.png"), size=(20, 20)
                        )
                    elif Decimal(vals["-input-"]) > Decimal(AVAILABLE):
                        win["-status-"].Update(
                            str(IMAGES_DIR / "red.png"), size=(20, 20)
                        )
                    elif Decimal(vals["-input-"]) <= Decimal(AVAILABLE):
                        win["-status-"].Update(
                            str(IMAGES_DIR / "green.png"), size=(20, 20)
                        )
                except:
                    win["-status-"].Update(str(IMAGES_DIR / "red.png"), size=(20, 20))
            if event == "-send-":
                try:
                    if Decimal(vals["-input-"]) <= Decimal(0):
                        win["-status-"].Update(
                            str(IMAGES_DIR / "orange.png"), size=(20, 20)
                        )
                    elif Decimal(vals["-input-"]) > Decimal(AVAILABLE):
                        win["-status-"].Update(
                            str(IMAGES_DIR / "red.png"), size=(20, 20)
                        )
                    elif Decimal(vals["-input-"]) <= Decimal(AVAILABLE):
                        win["-status-"].Update(
                            str(IMAGES_DIR / "green.png"), size=(20, 20)
                        )
                        break
                except:
                    win["-status-"].Update(str(IMAGES_DIR / "red.png"), size=(20, 20))
        win.close()

    def show_receive_window(self):
        title = "Receive"
        win = sg.Window(
            f"{title} - {self.__name__} {VERSION}", self.receive_window_layout()
        )
        # Receive button pressed, show address popup
        self.main_window["-receive-"].update(disabled=True)
        address = self.wallet.addresses[0][0]
        qr = qrcode.make(address, box_size=6)
        if not IMAGES_DIR.exists():
            images_dir.mkdir(parents=True)
        qr.save(IMAGES_DIR / "addressqr.png")

        while True:  # receive window loop
            event, _ = win.read()
            if event == "-ok-" or event == sg.WIN_CLOSED:
                self.main_window["-receive-"].update(disabled=False)
                break
            if event == "-copy-":
                clip.copy(str(address))
        win.close()

    def show_settings_window(self):
        title = "Settings"
        win = sg.Window(
            f"{title} - {self.__name__} {VERSION}", self.settings_window_layout()
        )
        while True:  # settings window loop
            event, values = win.read()
            if event == sg.WIN_CLOSED:
                break
            elif event == "-apply-":
                if values["-theme_choice-"][0] != sg.user_settings_get_entry("-theme-"):
                    sg.user_settings_set_entry(
                        "-theme-", values["-theme_choice-"][0]
                    )  # set theme to choice
                    sg.theme(sg.user_settings_get_entry("-theme-"))
                    # reset windows
                    self.main_window.close()
                    win.close()
                    self.show_settings_window()

            elif event == "-done-":
                break

        win.close()

    def show_new_password(self):
        title = "New password"
        win = sg.Window(
            f"{title} - {self.__name__} {VERSION}", self.new_password_layout()
        )

        def check_password(pwd1, pwd2):
            pwd1, pwd2 = pwd1.get(), pwd2.get()
            if pwd1 == pwd2:
                return True
            return False

        pwd = None

        while True:
            ev, vs = pwd_win.read()

            if ev == sg.WIN_CLOSED:
                sys.exit(0)

            elif ev == "-next-":
                if not check_password(pwd_win["-pass1-"], pwd_win["-pass2-"]):
                    pwd_win["-pass1-"].Widget.configure(
                        highlightcolor="red", highlightthickness=1, bd=0
                    )
                    pwd_win["-pass2-"].Widget.configure(
                        highlightcolor="red", highlightthickness=1
                    )
                    pwd = pwd_win["-pass1-"].get()

                else:
                    break

            if pwd is not None:
                break
        return pwd

    def show_new_wallet(self):
        title = "New wallet"
        win = sg.Window(
            f"{title} - {self.__name__} {VERSION}", self.new_wallet_layout()
        )
        while True:
            event, values = win.read()

            if event == sg.WIN_CLOSED:
                sys.exit(0)  # exit without error

            elif event == "-next-":
                if values["-radio1-"]:
                    # recover from keyphrase
                    # TODO
                    pass

                elif values["-radio2-"]:
                    # new with password encryption and keyphrase
                    pwd = self.show_new_password()

                elif values["-radio3-"]:
                    # new with no password (still uses keyphrase)
                    # TODO
                    word_list = self.show_recovery_phrase()
                    phrase = self.show_confirm_phrase(word_list)
                    kp = KeyPair.from_seed(phrase)
                    self.wallet = Wallet.create_new(kp)
                    self.wallet.save_to_der(self.wallet_fp / "wallet.der")
                    break
        win.close()

    def main_window_layout(self):
        # fmt: off
        layout = [  # main layout
            [sg.Text("Wallet", font="Arial 14 bold"), sg.Text("(Out of sync)", text_color="#f00", key='-sync-')],
            [sg.Text("Balances", font="Arial 12 bold"), sg.Push(), sg.Text("Recent Transactions", font=("Arial 12 bold"))],
            [sg.Text("Available:"), sg.Text("0 CHKN", font=("Arial 10 bold"), key='-available-')],
            [sg.Text("Pending:"), sg.Text("0 CHKN", font=("Arial 10 bold"), key='-pending-')],
            [sg.HSeparator()],
            [sg.Text("Total:"), sg.Text("0 CHKN", font=("Arial 10 bold"), key='-total-')],
            [sg.Button("Send", key="-send-"), sg.VSeperator(), sg.Button("Receive", key="-receive-"), sg.VSeperator(), sg.Button("Settings", key='-settings-')],
            [sg.Text("Height: 0", font="Arial 9"), sg.ProgressBar(100, orientation='h', size=(20, 20), key='-sync progress-'), sg.Text("0 connections", key='-connections-')]
        ]
        # fmt: on
        return layout

    def send_window_layout(self):
        # fmt: off
        layout = [  # send window layout
            [sg.Text("Send", font="Arial 12 bold")], [sg.Input(key="-input-"), sg.Image(str(IMAGES_DIR / "red.png"), size=(20, 20), key="-status-")],
            [sg.Text("Fee: 0.0 CHKN", key="-fee-")],  # estimated transaction fee
            [sg.HSeparator()],
            [sg.Text("Available:"), sg.Text(f"{AVAILABLE} CHKN", font="Arial 10 bold")],
            [sg.Text("Pending:"), sg.Text(f"{PENDING} CHKN", font="Arial 10 bold")],
            [sg.Button("Cancel", key="-cancel-"), sg.HSeparator(), sg.Button("Check", key="-check-"), sg.Button("Send", key="-send-")],
        ]
        # fmt: on
        return layout

    def receive_window_layout(self):
        # fmt: off
        layout = [  # receive window layout
            [sg.Image(str(IMAGES_DIR / "addressqr.png"))],
            [sg.Text(f"Address: {str(self.wallet.addresses[0][0])}"), sg.Button("Copy", key="-copy-")],
            [sg.Button("OK", key="-ok-")],
        ]
        # fmt: on
        return layout

    def settings_window_layout(self):
        theme_name_list = sg.theme_list()
        # fmt: off
        layout = [  # settings window layout
            [sg.Text("Look and Feel", font="Arial 12 bold")],
            [sg.Text("UI Theme", font="Arial 10"), sg.Listbox(theme_name_list, default_values=[sg.user_settings_get_entry("-theme-")], size=(15, 10), key="-theme_choice-")],
            [sg.Push(), sg.Button("Apply", key="-apply-"), sg.Button("Done", key="-done-")],
        ]
        # fmt: on
        return layout

    def new_password_layout(self):
        # fmt: off
        layout = [
            [sg.Text("Enter a password: "), sg.Input(size=(30, 10), key="-pass1-")],
            [sg.Push(), sg.Text("Confirm: "), sg.Input(size=(30, 10), key="-pass2-")],
            [sg.Push(), sg.Button("Next", key="-next-")]
        ]
        # fmt: on
        return layout

    def new_wallet_layout(self):
        # fmt: off
        layout = [  # new wallet prompt layout
            [sg.Text("Create new wallet", font="Arial 12 bold")],
            [sg.Radio("Recover from keyphrase", "RADIO", default=True, key="-radio1-")],
            [sg.Radio("New with password & keyphrase", "RADIO", key="-radio2-")],
            [sg.Radio("New with no password (caution!)", "RADIO", key="-radio3-")],
            [sg.Button("Back", key="-back-"), sg.Push(), sg.Button("Next", key="-next-")]
        ]
        # fmt: on
        return layout

    def recovery_phrase_layout(self):
        # fmt: off
        layout = [
            [sg.Text("Recovery Phrase", font=("Arial 12 bold"))],
            [sg.Text("Write the following words down somewhere safe!\nThis will be used to recover your wallet if you ever lock yourself out or lose the file.")],
            [sg.Multiline(no_scrollbar=True, size=(30, 3), disabled=True, key='-words-')],
            [sg.Button("Refresh", key="-refresh-"), sg.HSeparator(), sg.Button("Next", key="-next-")]
        ]
        # fmt: on
        return layout

    def confirm_recovery_phrase_layout(self, word_list):
        # TODO make buttons disperse evenly
        words = word_list

        rows = [[], [], []]
        x = 0
        for i in range(3):
            for j in range(4):
                n = randint(0, len(words) - 1)
                rows[i].append(sg.Button(words.pop(n), key=f"-word{x}-"))
                x += 1

        # fmt: off
        layout = [
            [sg.Text("Confirm your recovery phrase", font=("Arial 10 bold"))],
            [sg.Multiline(no_scrollbar=True, disabled=True, size=(30, 3), key="-words-")],
            rows,
            [sg.HSeparator()],
            [sg.Button("Reset", key="-reset-"), sg.HSeparator(), sg.Button("Confirm", disabled=True, key="-confirm-")]
        ]
        # fmt: on
        return layout


if __name__ == "__main__":
    app = App()
    app.run()
