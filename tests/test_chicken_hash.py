import sys
from binascii import hexlify
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))

from crypto.chicken import chicken_hash  # noqa: E402


def test_chicken_hash():
    # Known input data
    input_data = b"chicken_hash_test"
    # Expected output of chicken_hash for the given input
    # Replace the value below with the actual expected hash output (hexadecimal)
    expected_hash_hex = (
        b"6658e0663e280e1cfdd446107c415f085984c3550f6c3d0a2016a9d5391377d9"
    )

    # Compute the hash of the input data
    computed_hash = chicken_hash(input_data)
    computed_hash_hex = hexlify(computed_hash)

    # Assert that the computed hash matches the expected hash
    assert (
        computed_hash_hex == expected_hash_hex
    ), f"Expected hash {expected_hash_hex}, but got {computed_hash_hex}"
