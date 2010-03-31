#!/usr/bin/env python
# coding: utf-8

import types
from PIL import Image
from NitgenBSP import _bsp_core
from NitgenBSP import _bsp_search

"""Nitgen fingerprint recognition API"""

PURPOSE_VERIFY = 0x01
PURPOSE_ENROLL = 0x03

class FingerText:
    """The Text-Encoded version of a fingerprint's FIR.
    FingerText objects are created automatically by instances of
    the Finger class, when invoking the Finger.text() method.
    """
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text

class Finger:
    """The Finger class provides the FIR Handle, raw
    image buffer provided by the device, as well as
    image dimentions (width and height).
    It may also convert the raw buffer to a PIL image,
    as well as the Text-Encoded FIR.
    """
    def __init__(self, handler, FIR, buffer, width, height):
        """Finger objects are created automatically by instances of
        the Handler class, when invoking the Handler.capture() method.
        """
        self.FIR = FIR
        self.width = width
        self.height = height
        self.buffer = buffer
        self.__handler = handler
        self.payload = ""

    def set_payload(self, text):
        """Add text (user data) into this fingerprint record.
        """
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
        self._handler, self.__image_width, self.__image_height = _bsp_core.open()

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

        FIR, buffer = _bsp_core.capture(self._handler,
            self.__image_width, self.__image_height, purpose, timeout)

        finger = Finger(self._handler, FIR, buffer,
            self.__image_width, self.__image_height)

        if payload is not None:
            finger.set_payload(payload)

        return finger

    def verify(self, finger1, finger2=None, timeout=5):
        """Perform verification of two fingerprints.
        `finger1` is mandatory and must be an instance of Finger or FingerText class.
        `finger2` is optional. When it is not available, a new capture() is done in
        order to verify both fingerprints. However, if it is passed by the user,
        it must be the same type of `finger1`. It is not possible to verify an instance
        of Finger against FingerText and vice-versa.
        `timeout` is only used when `finger2` is not available. In this case, it will
        be passed in to the capture() method.

        The return value is 0 when fingerprints doesn't match. When they match, the
        default return value is 1, unless `finger1` has an embedded payload. In this case,
        the payload of `finger1` is returned.
        """
        if isinstance(finger1, Finger):
            finger1 = finger1.FIR
            if finger2 is None:
                finger2 = self.capture(timeout=timeout).text()
        elif isinstance(finger1, FingerText):
            finger1 = str(finger1)
            if finger2 is None:
                finger2 = self.capture(timeout=timeout).text()
        else:
            raise TypeError("finger1 must be an instance of Finger or FingerText")
        
        if isinstance(finger2, Finger):
            finger2 = finger2.FIR
        elif isinstance(finger2, FingerText):
            finger2 = str(finger2)
        else:
            raise TypeError("finger2 must be an instance of Finger or FingerText")

        if type(finger1) != type(finger2):
            raise TypeError("cannot verify Finger against FingerText and vice-versa")
        
        match, payload = _bsp_core.verify(self._handler, finger2, finger1)
        return match == 1 and (payload or match) or 0

    def close(self):
        """Close the currently opened Nitgen device
        """
        _bsp_core.close(self._handler)


class SearchEngine(object):
    """The Nitgen's built-in in-memory Search Engine interface
    """
    def __init__(self, handler):
        if not isinstance(handler, Handler):
            raise TypeError("SearchEngine must be initialize with an instance of the Handler class")

        self.__handler = handler._handler
        self.__capture = handler.capture
        _bsp_search.initialize(self.__handler)

    def __del__(self):
        _bsp_search.terminate(self.__handler)

    def insert_user(self, userID, finger):
        """Add new userID with its fingerprint into the DB
        """
        if isinstance(finger, Finger):
            finger = finger.FIR
        elif isinstance(finger, FingerText):
            finger = str(finger)
        else:
            raise TypeError("finger must be an instance of either Finger or FingerText")

        if not isinstance(userID, types.IntType):
            raise TypeError("userID must be an integer")

        _bsp_search.insert(self.__handler, userID, finger)

    def remove_user(self, userID):
        """Remove userID from the DB
        """
        if not isinstance(userID, types.IntType):
            raise TypeError("userID must be an integer")

        _bsp_search.remove(self.__handler, userID)

    def identify(self, finger=None, security_level=5, timeout=5):
        if finger is None:
            finger = self.__capture(timeout=timeout).text()
        elif isinstance(finger, Finger):
            finger = finger.FIR
        elif isinstance(finger, FingerText):
            finger = str(finger)
        else:
            raise TypeError("finger must be an instance of Finger or FingerText")

        if security_level not in range(1, 10):
            raise TypeError("security_level must be an integer betweeen 1 (lowest) and 9 (highest)")

        if not isinstance(timeout, types.IntType):
            raise TypeError("timeout (seconds) must be an integer")

        return _bsp_search.identify(self.__handler, finger, security_level)

    def save(self, filename):
        """Save DB into filename
        """
        _bsp_search.save(self.__handler, filename)

    def load(self, filename):
        """Load DB from filename
        """
        _bsp_search.load(self.__handler, filename)
