# Chicken Ticket
![PyPI](https://img.shields.io/badge/python-3.6-blue.svg)

**DEAR USER, THIS BRANCH IS IN DEVELOPMENT. THERE IS CURRENTLY NOT A STABLE BRANCH FOR USE IN PRODUCTION. USE AT YOUR OWN RISK**

Chicken Ticket is a Python powered blockchain solution. Users are encouraged to meander about the codebase, learn the nitty gritty details of what makes a coin tick, fork and design your own coin, or use as your every day cryptocurrency.
I'm kind of rewriting things, so things may get weird. I'm doing so to make ChickenTicket even better as a library.
Everything is broken down into finer components. Transactions, blocks, the node, all have a separate file dedicated to their respective logic.
Most, if not all, of the core elements of the blockchain can be serialized into a string. For example:

Simply convert any of the following objects (after instantiation) with `str(cls)`:

 - Transaction
 - Block
 - Mempool
 - Input
 - Output
 - Address
 - Alias
 - Peer
 - KeyPair
 - Node

### Why?

ChickenTicket is meant to be a PoS coin.
We plan to offer a faucet, a tipbot, and some other services for the coin to incentivize usage and ease getting into the coin.
The coin is based on modules that are included in the Python standard library and other pure Python libraries such that CHKN can run on anything that supports Python.
Speed and reliability is our number 1 goal.

### Tech
Chicken Ticket uses a number of technologies:
* [Python 3] - A powerful object-oriented programming language.
* [SQLite] - An ACID-compliant database solution for storing information in a single file, locally.
* [Msgpack] - Responsible for compressing and serializing network messages.
* [PyCryptodomex] - Low-level cryptographic primitives for making the coin secure (hashlib for pure Python install).
* [ECDSA] - Elliptic Curve Digital Signature Algorithm. Used for generating keys fast and securely.
* [Flask] - Microframework webserver. `httpnode` uses this to provide a very basic node.
* [qrcode] - Generate a QR code from data, such as an address.
* [pillow] - Working with images, used by `qrcode`.
* [PySimpleGUI] - Used by `simplegui` to provide a basic wallet for use by end-users.

### Installing from source
Chicken Ticket requires [Python](https://python.org/) 3.6+ to run.
Chicken Ticket requires [Visual Studio Build Tools](https://www.visualstudio.com/downloads/#build-tools-for-visual-studio-2017) or any GCC compiler to install the C-based libraries.

Clone this repository after installing [Git](https://git-scm.com):
```sh
$ git clone https://github.com/Aareon/chickenticket
```

Install the dependencies after cloning:
#### Unix
```sh
$ cd chickenticket
$ python3 -m pip install -r requirements.txt
```
#### Windows
```sh
$ cd chickenticket
$ py -3 -m pip install -r requirements.txt
```
#### Installing with Pipenv
##### Install Pipenv
```sh
$ py -m pip install pipenv -U
```
```sh
$ cd chickenticket
$ pipenv install
```
### How to use

After installing requirements, launch the wallet with:
```sh
$ python3 src/simplegui.py
```
Or launch using Pipenv environment
```sh
$ pipenv run python3 src/simplegui.py
```
Wallet setup is automated and will guide you through the process.

### Development
Want to contribute? We ❤️❤️❤️ pull requests! 
Please test code extensively before creating a pull request.
Keep in mind, we are strong supporters of idiomatic and beautiful Python code.

### Social

- [Join us on Discord](https://discord.gg/a6UmtndUXy)
- [Subscribe to our subreddit](https://reddit.com/r/ChickenTicket)

### Todos
 - MOAR TESTS
 - ~~Probably need to generate the genesis block, just saying.~~ Done
 - Peers and Nodes (including websocket handling, etc. Should be fun 😅) (Partially done)
 - Sending and receiving transactions
 - DSL for sub-contracts
 - Mining
 - Clean up!
 - Graphical Wallet ([`simplegui.py`](https://github.com/Aareon/chickenticket/blob/master/src/simplegui.py))

## Screenshots
![The ChickenTicket simple GUI](/images/screens.png)


License
----
MIT
