// C wrap for Allium algo

#include <Python.h>

#include "sha3/sph_blake.h"
#include "sha3/sph_groestl.h"
#include "sha3/sph_skein.h"
#include "sha3/sph_keccak.h"
#include "sha3/sph_cubehash.h"

#include "lyra2/Lyra2.h"

// Takes a Python bytes object, runs the Allium hashset on it, and returns a bytes object.

static PyObject* allium_compute_hash(PyObject *self, PyObject *args) {
  const char* input;

  if (!PyArg_ParseTuple(args, "y", &input))
    return NULL;

  uint32_t hashA[8], hashB[8];

  sph_blake256_context     ctx_blake;
  sph_keccak256_context    ctx_keccak;
  sph_cubehash512_context  ctx_cubehash;
  sph_skein256_context     ctx_skein;
  sph_groestl256_context   ctx_groestl;

  sph_blake256_init(&ctx_blake);
  sph_blake256(&ctx_blake, input, 80);
  sph_blake256_close(&ctx_blake, hashA);

  sph_keccak256_init(&ctx_keccak);
  sph_keccak256(&ctx_keccak, hashA, 32);
  sph_keccak256_close(&ctx_keccak, hashB);

  LYRA2(hashA, 32, hashB, 32, hashB, 32, 1, 8, 8);

  sph_cubehash256_init(&ctx_cubehash);
  sph_cubehash256(&ctx_cubehash, hashA, 32);
  sph_cubehash256_close(&ctx_cubehash, hashB);

  sph_skein256_init(&ctx_skein);
  sph_skein256(&ctx_skein, hashA, 32);
  sph_skein256_close(&ctx_skein, hashB);

  sph_groestl256_init(&ctx_groestl);
  sph_groestl256(&ctx_groestl, hashB, 32);
  sph_groestl256_close(&ctx_groestl, hashA);

  PyObject* ret = Py_BuildValue("y", hashA);

  return ret;
}

static PyMethodDef module_methods[] = {
  {"compute_hash", allium_compute_hash, METH_VARARGS, "Run the Allium hashset against some input data"},
  {NULL, NULL, 0, NULL}
};

static struct PyModuleDef moduledef = {
  PyModuleDef_HEAD_INIT,
  "allium",
  "Provides a function for running the Allium hash",
  -1,
  module_methods
};

PyMODINIT_FUNC PyInit_allium(void) {
  Py_Initialize();

  return PyModule_Create(&moduledef);
}