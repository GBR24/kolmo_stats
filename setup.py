"""
Build the kolmo_stats C++ extension (_core).

Run once after cloning:
    pip install pybind11
    pip install -e .

Or for in-place development:
    python setup.py build_ext --inplace
"""
import sys
from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext

_core_src = "src/kolmo_stats/retrieval_engine/_core"

import platform as _platform

extra_compile = ["-O3", "-std=c++17"]
if sys.platform == "win32":
    extra_compile = ["/O2", "/std:c++17"]
elif sys.platform == "darwin":
    # -march=native breaks universal2 builds on Apple Silicon
    extra_compile += ["-ffast-math", "-funroll-loops"]
else:
    extra_compile += ["-march=native", "-ffast-math", "-funroll-loops"]

ext_modules = [
    Pybind11Extension(
        "kolmo_stats.retrieval_engine._core",
        sources=[f"{_core_src}/bindings.cpp"],
        include_dirs=[_core_src],
        extra_compile_args=extra_compile,
        cxx_std=17,
    )
]

setup(
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)
