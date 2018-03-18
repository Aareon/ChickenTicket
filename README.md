# Chicken Ticket
[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)

Chicken Ticket is a Python powered blockchain solution. Users are encouraged to meander about the codebase, learn the nitty gritty details of what makes a coin tick, fork and design your own coin, or use as your every day cryptocurrency.

### Tech
Chicken Ticket uses a number of technologies:
* [Python 3] - A powerful object oriented programming language, we love it!
* [SQLite] - An ACID-compliant database solution for storing information in a single file, locally.
* [SQLAlchemy] - An ORM for SQL databases in Python.
* [PyCryptodomex] - Low-level cryptographic primitives for making the coin secure
* [ECDSA] - Elliptic Curve Digital Signature Algorithm. Used for generating keys fast and securely.

### Installing from source
Chicken Ticket requires [Python](https://python.org/) 3.5+ to run.

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
Want to contribute? We ❤️ pull requests!

### Todos
 - MOAR TESTS
 - Probably need to generate the genesis block, just saying.
 - Release to the public

License
----
GPL
