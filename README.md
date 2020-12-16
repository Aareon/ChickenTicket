# Chicken Ticket
![PyPI](https://img.shields.io/badge/python-3.6-blue.svg)

Chicken Ticket is a Python powered blockchain solution. Users are encouraged to meander about the codebase, learn the nitty gritty details of what makes a coin tick, fork and design your own coin, or use as your every day cryptocurrency.
I'm kind of rewriting things, so things may get weird. I'm doing so to make ChickenTicket even better as a library.
Everything is broken down into finer components. Transactions, blocks, the node, all have a separate file dedicate to their respective logic.
Most, if not all, of the core elements of the blockchain can be serialized into a string. For example:
`<Transaction(id: 0, timestamp: 16089010, inputs: [<Input(0, Decimal("1.0"))>, ...`
So on and so forth. Simply convert any of the following objects (after instantiation) with `str(cls)`:
 • Transaction
 • MempoolTx
 • Block
 • Mempool
 • Input
 • Output
 • Address
 • Alias
 • Peer
 • KeyPair

### Tech
Chicken Ticket uses a number of technologies:
* [Python 3] - A powerful object oriented programming language, we love it!
* [SQLite] - An ACID-compliant database solution for storing information in a single file, locally.
* [SQLAlchemy] - An ORM for SQL databases in Python.
* [PyCryptodomex] - Low-level cryptographic primitives for making the coin secure
* [ECDSA] - Elliptic Curve Digital Signature Algorithm. Used for generating keys fast and securely.

### Installing from source
Chicken Ticket requires [Python](https://python.org/) 3.5+ to run.
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

### Development
Want to contribute? We ❤️❤️❤️ pull requests! 
Please test code extensively before creating a pull request.
Keep in mind, we are strong supporters of idiomatic and beautiful Python code.

### Todos
 - MOAR TESTS
 - ~~Probably need to generate the genesis block, just saying.~~ Done
 - Peers and Nodes (including websocket handling, etc. Should be fun 😅)
 - Sending and receiving transactions
 - Mining
 - Clean up!
 - Graphical Wallet


License
----
MIT
