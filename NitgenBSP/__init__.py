#!/usr/bin/env python
# coding: utf-8

from PIL import Image
from NitgenBSP import _bsp_core

"""Nitgen fingerprint recognition API"""

PURPOSE_VERIFY = 0x01
PURPOSE_ENROLL = 0x03

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
    def __init__(self, handler, FIR, buffer, width, height):
        self.FIR = FIR
        self.width = width
        self.height = height
        self.buffer = buffer
        self.__handler = handler
        self.payload = ""

    def set_payload(self, text):
        self.payload = text
        self.FIR = _bsp_core.payload(self.__handler, self.FIR, text)
 
    def text(self):
        """Return the Text-Encoded version of the FIR for this
        fingerprint, which may be used to store the fingerprint
        in a database as well as later verification.
        """
        return FingerText(_bsp_core.text_fir(self.__handler, self.FIR))

    def image(self):
        """Return the PIL image of this fingerprint, which may be
        used to be saved on disk as JPG, PNG, etc.
        """
        return Image.fromstring("L",
            (self.width, self.height), self.buffer)

    def __del__(self):
        del(self.buffer)
        _bsp_core.free_fir(self.__handler, self.FIR)
 

class Handler:
    """A Nitgen device handler
    """
    def __init__(self):
        """Initialize the Nitgen API and open the first available device
        using the auto-detection mode.
        """
        self.__handler, self.__image_width, self.__image_height = _bsp_core.open()

    def capture(self, payload=None, purpose=PURPOSE_VERIFY, timeout=5):
        """Capture a fingerprint from the device and return an instance
        of the Finger class.
        `payload` is an optional STRING which is encoded within the FIR,
        and retrieved during the verify() process.
        Default `purpose` of capture is VERIFY, but may also be ENROLL.
        The optional `timeout` is defined in seconds.
        """
        if purpose not in (PURPOSE_VERIFY, PURPOSE_ENROLL):
            raise TypeError("unknown capture purpose")

        FIR, buffer = _bsp_core.capture(self.__handler,
            self.__image_width, self.__image_height, purpose, timeout)

        finger = Finger(self.__handler, FIR, buffer,
            self.__image_width, self.__image_height)

        if payload is not None:
            finger.set_payload(payload)

        return finger

    def verify(self, cap1, cap2=None, timeout=5):
        """Perform verification of two fingerprints.
        `cap1` is mandatory and must be an instance of Finger or FingerText class.
        `cap2` is optional. When it is not available, a new capture() is done in
        order to verify both fingerprints. However, if it is passed by the user,
        it must be the same type of `cap1`. It is not possible to verify an instance
        of Finger against FingerText and vice-versa.
        `timeout` is only used when `cap2` is not available. In this case, it will
        be passed in to the capture() method.

        The return value is 0 when fingerprints doesn't match. When they match, the
        default return value is 1, unless `cap1` has an embedded payload. In this case,
        the payload of `cap1` is returned.
        """
        if isinstance(cap1, Finger):
            if cap2 is None:
                cap1 = str(cap1.text())
                cap2 = self.capture(timeout=timeout).text()
            else:
                cap1 = cap1.FIR
        elif isinstance(cap1, FingerText):
            cap1 = str(cap1)
            if cap2 is None:
                cap2 = self.capture(timeout=timeout).text()
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
        
        match, payload = _bsp_core.verify(self.__handler, cap2, cap1)
        return match == 1 and (payload or match) or 0

    def close(self):
        """Close the currently opened Nitgen device
        """
        _bsp_core.close(self.__handler)
