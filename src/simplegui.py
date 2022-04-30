# ChickenTicket simple GUI based on PySimpleGUI
from decimal import Decimal
from pathlib import Path

import pyperclip as clip
import PySimpleGUI as sg
import qrcode

from config import Config
from keys import KeyPair
from wallet import Wallet

images_dir = Path(__file__).parent.parent / "images"
print(f"Images dir: {images_dir}")

# attempt to load wallet file from default location
WALLET = None

wallet_fp = Config.DEFAULT_WALLET_FP

if not wallet_fp.exists():

    wallet_fp = Path(sg.popup_get_folder("Select wallet folder"))

    if not (wallet_fp / "wallet.der").exists():
        kp = KeyPair.new()
        WALLET = Wallet()
        WALLET.create_wallet_address(kp)
        WALLET.save_to_der(wallet_fp / "wallet.der")
    else:
        WALLET = Wallet.load_from_der(wallet_fp / "wallet.der")

else:
    print("Wallet exists. Loading...")
    WALLET = Wallet().load_from_der(wallet_fp)

AVAILABLE = 100  # testing

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

window.close()
