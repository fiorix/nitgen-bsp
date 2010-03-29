#!/usr/bin/env python
# coding: utf-8

from distutils.core import setup, Extension

setup(
    name="bsp",
    version="0.1",
    author="Alexandre Fiori",
    author_email="fiorix@gmail.com",
    url="http://github.com/fiorix/nitgen_bsp",
    packages=["BSP"],
    ext_modules=[
        Extension("BSP/_bsp_module", [
            "BSP/bsp_module.c",
        ],
        include_dirs=["/usr/local/NITGEN/eNBSP/include"],
        libraries=["pthread", "NBioBSP"], )
    ]
)
