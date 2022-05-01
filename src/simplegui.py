# ChickenTicket simple GUI based on PySimpleGUI
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

WALLET = None
AVAILABLE = 0
PENDING = 0

node = HTTPNode(config=Config)
node.setup()

images_dir = Path(__file__).parent.parent / "images"
print(f"Images dir: {images_dir}")

# attempt to load wallet file from default location

wallet_fp = Config.DEFAULT_WALLET_FP

if not wallet_fp.exists():

    wallet_fp = Path(sg.popup_get_folder("Select wallet folder"))

    if not (wallet_fp / "wallet.der").exists():

        def phrase_layout():
            # fmt: off
            return [
                [sg.Text("Recovery Phrase", font=("Arial 12 bold"))],
                [sg.Text("Write the following words down somewhere safe!\nThis will be used to recover your wallet if you ever lock yourself out or lose the file.")],
                [sg.Multiline(no_scrollbar=True, size=(30, 3), disabled=True, key='-words-')],
                [sg.Button("Refresh", key="-refresh-"), sg.HSeparator(), sg.Button("Next", key="-next-")]
            ]
            # fmt: on

        # generate a new wallet
        # get 12 random words from mnemonics.txt
        def generate_wordlist():
            with open(Path(__file__).parent / "mnemonics.txt", "r") as f:
                words = f.read().splitlines()
                word_list = []
                for _ in range(0, 12):
                    r = randint(0, len(words))
                    while words[r] in word_list:
                        r = randint(0, len(words))
                    else:
                        word_list.append(words[r])
                return word_list
        
        # show keyphrase
        word_win = sg.Window("ChickenTicket Create Wallet", phrase_layout()).finalize()
        word_win["-words-"].update(" ".join(w for w in generate_wordlist()))
        while True:
            event, values = word_win.read()
            if event == sg.WIN_CLOSED:
                if sg.popup("Are you sure you want to exit?", button_type=1) == "Yes":
                    sys.exit(1)
                else:
                    word_win = sg.Window("ChickenTicket Create Wallet", phrase_layout()).finalize()
                    word_win["-words-"].update(" ".join(w for w in generate_wordlist()))
            elif event == "-refresh-":
                word_win["-words-"].update(" ".join(w for w in generate_wordlist()))
        word_win.close()

        kp = KeyPair.new()
        WALLET = Wallet()
        WALLET.create_wallet_address(kp)
        WALLET.save_to_der(wallet_fp / "wallet.der")
    else:
        WALLET = Wallet().load_from_der(wallet_fp / "wallet.der")

else:
    print("Wallet exists. Loading...")
    WALLET = Wallet().load_from_der(wallet_fp)


def run():
    # fmt: off
    layout = [
        # main layout
        [sg.Text("Wallet", font="Arial 14 bold"), sg.Text("(Out of sync)", text_color="#f00", key='-sync-')],
        [sg.Text("Balances", font="Arial 12 bold")],
        [sg.Text("Available:"), sg.Text("0 CHKN", font=("Arial 10 bold"), key='-available-')],
        [sg.Text("Pending:"), sg.Text("0 CHKN", font=("Arial 10 bold"), key='-pending-')],
        [sg.HSeparator()],
        [sg.Text("Total:"), sg.Text("0 CHKN", font=("Arial 10 bold"), key='-total-')],
        [sg.Button("Send", key="-send-"), sg.VSeperator(), sg.Button("Receive", key="-receive-"), sg.VSeperator(), sg.Button("Settings", key='-settings-')],
        [sg.ProgressBar(100, orientation='h', size=(20, 20), key='-sync progress-'), sg.Text("0 connections", key='-connections-')]
    ]
    # fmt: on
    window = sg.Window("ChickenTicket simple GUI", layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == "-send-":
            # fmt: off
            send_win = sg.Window("Send", [
                [sg.Text("Send", font="Arial 12 bold")],
                [sg.Input(key="-input-"), sg.Image(str(images_dir / "red.png"), size=(20, 20), key='-status-')],
                [sg.Text("Available:"), sg.Text(f"{AVAILABLE} CHKN", font="Arial 10 bold")],
                [sg.Button("Cancel", key="-cancel-"), sg.HSeparator(), sg.Button("Check", key="-check-"), sg.Button("Send", key="-send-")]
            ])
            # fmt: on
            while True:
                event, vals = send_win.read()
                if event == "-cancel-" or event == sg.WIN_CLOSED:
                    break
                if event == "-check-":
                    if Decimal(vals["-input-"]) <= Decimal(0):
                        send_win["-status-"].Update(
                            str(images_dir / "orange.png"), size=(20, 20)
                        )
                    elif Decimal(vals["-input-"]) > Decimal(AVAILABLE):
                        send_win["-status-"].Update(
                            str(images_dir / "red.png"), size=(20, 20)
                        )
                    elif Decimal(vals["-input-"]) <= Decimal(AVAILABLE):
                        send_win["-status-"].Update(
                            str(images_dir / "green.png"), size=(20, 20)
                        )
                if event == "-send-":
                    if Decimal(vals["-input-"]) <= Decimal(0):
                        send_win["-status-"].Update(
                            str(images_dir / "orange.png"), size=(20, 20)
                        )
                    elif Decimal(vals["-input-"]) > Decimal(AVAILABLE):
                        send_win["-status-"].Update(
                            str(images_dir / "red.png"), size=(20, 20)
                        )
                    elif Decimal(vals["-input-"]) <= Decimal(AVAILABLE):
                        send_win["-status-"].Update(
                            str(images_dir / "green.png"), size=(20, 20)
                        )
                        break

            send_win.close()

        if event == "-receive-":
            # Receive button pressed, show address popup
            address = WALLET.addresses[0][0]
            qr = qrcode.make(address, box_size=6)
            qr.save(images_dir / "addressqr.png")
            # fmt: off
            rx_win = sg.Window("Receive", [
                [sg.Image(str(images_dir / "addressqr.png"))],
                [sg.Text(f"Address: {address}"), sg.Button("Copy", key="-copy-")],
                [sg.Button("OK", key='-ok-')]
            ])
            # fmt: on
            while True:
                event, _ = rx_win.read()
                if event == "-ok-" or event == sg.WIN_CLOSED:
                    break
                if event == "-copy-":
                    clip.copy(str(address))
            rx_win.close()

    print("Closing!")
    window.close()
    sys.exit(0)

    node_thread.join()


if __name__ == "__main__":
    node_thread = threading.Thread(target=lambda: node.run(), daemon=True)

    window_thread = threading.Thread(target=lambda: run())

    window_thread.start()
    node_thread.start()
