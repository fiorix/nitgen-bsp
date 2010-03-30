#!/usr/bin/env python
# coding: utf-8

from PIL import Image
from NitgenBSP import _bsp_module

class FingerText(str):
    pass

class Finger(object):
    def __init__(self, handler, data, width, height):
        self.__handler = handler
        self.buffer, self.FIR = data
        self.width = width
        self.height = height

    def text(self):
        return FingerText(_bsp_module.text_fir(self.__handler, self.FIR))

    def image(self):
        return Image.fromstring("L",
            (self.width, self.height), self.buffer)

    def __del__(self):
        _bsp_module.free_fir(self.__handler, self.FIR)
 

class Handler:
    def __init__(self):
        self.__bsp = _bsp_module.open()
        self.__handler = self.__bsp[0]
        self.__image_width = self.__bsp[1]
        self.__image_height = self.__bsp[2]

    def capture(self):
        return Finger(self.__handler,
            _bsp_module.capture(*self.__bsp),
            self.__image_width, self.__image_height)

    def verify(self, cap1, cap2):
        if isinstance(cap1, Finger):
            cap1 = cap1.FIR
        elif isinstance(cap1, FingerText):
            cap1 = str(cap1)
        else:
            raise TypeError("cap1 must be an instance of Finger or FingerText")
        
        if isinstance(cap2, Finger):
            cap2 = cap2.FIR
        elif isinstance(cap2, FingerText):
            cap2 = str(cap2)
        else:
            raise TypeError("cap2 must be an instance of Finger or FingerText")

        if type(cap1) != type(cap2):
            raise TypeError("cannot verify Finger against FingerText and vice-versa")
        
        return _bsp_module.verify(self.__handler, cap1, cap2)

    def close(self):
        _bsp_module.close(self.__handler)
