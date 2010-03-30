#!/usr/bin/env python
# coding: utf-8

import os
import NitgenBSP

if __name__ == "__main__":
    assert os.getuid() == 0, "please run as root"

    # get the bsp handler
    handler = NitgenBSP.Handler()
    
    raw_input("place your finger in the device and press enter: ")
    cap1 = handler.capture()

    raw_input("ok. do it again... press enter when ready: ")
    cap2 = handler.capture()

    # default verification method is via FIR handler in the device
    # but it may also be done by the text-encoded FIR, like this:
    #  match = handler.verify(cap1.text(), cap2.text())
    match = handler.verify(cap1, cap2)
    print "your fingerprints " + (match and "do match" or "do not match")

    # that's it
    handler.close()
