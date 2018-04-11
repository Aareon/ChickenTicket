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
    name="ChickenTicket",
    version="0.5",
    description="Cryptocurrency implementation in Python",
    author="Aareon Sullivan",
    author_email="idk lol",
    url="idk",
    ext_modules=[allium_module])