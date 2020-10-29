import os
from os.path import join

from cffi import FFI

ffibuilder = FFI()

folder = os.path.dirname(os.path.abspath(__file__))

with open(join(folder, "hmmer_reader", "meta_read.h"), "r") as f:
    ffibuilder.cdef(f.read())

with open(join(folder, "hmmer_reader", "meta_read.c"), "r") as f:
    read_metadata_c = f.read()

ffibuilder.set_source(
    "hmmer_reader._ffi",
    fr"""
    {read_metadata_c}
    """,
    language="c",
)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
