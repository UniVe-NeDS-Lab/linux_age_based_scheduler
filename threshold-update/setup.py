from distutils.core import setup, Extension

# the c++ extension module
extension_mod = Extension("threshold_update", ["threshold_update.c"])

setup(name = "threshold_update", ext_modules=[extension_mod])

