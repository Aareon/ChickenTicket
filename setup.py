from distutils.core import setup, Extension

# Other distutils setup here

allium_module = Extension("allium", [
    "src/allium/allium.c",
    "src/allium/include/lyra2/Lyra2.c",
    "src/allium/include/lyra2/Sponge.c",
    "src/allium/include/sha3/sph_blake.c",
    "src/allium/include/sha3/sph_cubehash.c",
    "src/allium/include/sha3/sph_groestl.c",
    "src/allium/include/sha3/sph_keccak.c",
    "src/allium/include/sha3/sph_skein.c"
    ], include_dirs=["src/allium/include"])

setup(
    name="Chicken Ticket",
    version="0.5",
    description="Pure Python implementation of a cryptocurrency blockchain ",
    author="Aareon Sullivan",
    author_email="aareon@died-in.space",
    url="",
    ext_modules=[allium_module])