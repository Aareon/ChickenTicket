from dataclasses import dataclass
from typing import List, Union
from keys import KeyPair
from node import Node


@dataclass
class Wallet:
    node: Node
    aliases: List[str]
    address: List[Union[str, KeyPair]]
