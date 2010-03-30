#!/usr/bin/env python
# coding: utf-8

import os
import NitgenBSP

if __name__ == "__main__":
    assert os.getuid() == 0, "please run as root"

    # get the bsp handler
    handler = NitgenBSP.Handler()

    raw_input("place your finger in the reader and press enter: ")

    # get the fingerprint
    finger = handler.capture()

    filename = raw_input("enter the filename to save your fingerprint [out.jpg, out.png, out.gif]: ")

    # get the PIL image
    image = finger.image()
    image.save(filename)

    # close the handler
    handler.close()
