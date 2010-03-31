#!/usr/bin/env python
# coding: utf-8

from distutils.core import setup, Extension

setup(
    name="NitgenBSP",
    version="0.1",
    author="Alexandre Fiori",
    author_email="fiorix@gmail.com",
    url="http://github.com/fiorix/nitgen-bsp",
    packages=["NitgenBSP"],
    ext_modules=[
        Extension("NitgenBSP/_bsp_core", ["NitgenBSP/bsp_core.c"],
        Extension("NitgenBSP/_bsp_search", ["NitgenBSP/bsp_search.c"],
        include_dirs=["/usr/local/NITGEN/eNBSP/include"],
        libraries=["pthread", "NBioBSP"], )
    ]
)
