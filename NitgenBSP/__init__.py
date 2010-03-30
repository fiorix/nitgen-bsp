#!/usr/bin/env python
# coding: utf-8

from PIL import Image
from NitgenBSP import _bsp_module

"""Nitgen fingerprint recognition API"""

class FingerText(str):
    """The Text-Encoded version of a fingerprint's FIR.
    """
    pass

class Finger(object):
    """The Finger class provides the FIR Handle, raw
    image buffer provided by the device, as well as
    image dimentions (width and height).
    It may also convert the raw buffer to a PIL image,
    as well as the Text-Encoded FIR.
    """
    def __init__(self, handler, data, width, height):
        self.__handler = handler
        self.buffer, self.FIR = data
        self.width = width
        self.height = height

    def text(self):
        """Return the Text-Encoded version of the FIR for this
        fingerprint, which may be used to store the fingerprint
        in a database as well as later verification.
        """
        return FingerText(_bsp_module.text_fir(self.__handler, self.FIR))

    def image(self):
        """Return the PIL image of this fingerprint, which may be
        used to be saved on disk as JPG, PNG, etc.
        """
        return Image.fromstring("L",
            (self.width, self.height), self.buffer)

    def __del__(self):
        _bsp_module.free_fir(self.__handler, self.FIR)
 

class Handler:
    """A Nitgen device handler
    """
    def __init__(self):
        """Initialize the Nitgen API and open the first available device
        using the auto-detection mode.
        """
        self.__bsp = _bsp_module.open()
        self.__handler = self.__bsp[0]
        self.__image_width = self.__bsp[1]
        self.__image_height = self.__bsp[2]

    def capture(self):
        """Capture a fingerprint from the device and return an instance
        of the Finger class.
        """
        return Finger(self.__handler,
            _bsp_module.capture(*self.__bsp),
            self.__image_width, self.__image_height)

    def verify(self, cap1, cap2):
        """Perform verification of two fingerprints by receiving either
        a pair of Finger or FingerText instances.
        Returns 0 or 1, depending on finger verification.
        """
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
        """Close the currently opened Nitgen device
        """
        _bsp_module.close(self.__handler)
