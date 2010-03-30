#!/usr/bin/env python
# coding: utf-8

import os
import NitgenBSP

if __name__ == "__main__":
    assert os.getuid() == 0, "please run as root"

    # get the bsp handler
    handler = NitgenBSP.Handler()
    
    raw_input("place your finger in the device and press enter: ")
    finger = handler.capture(payload="hello, world!", purpose=NitgenBSP.PURPOSE_ENROLL)

    raw_input("ok. do it again... press enter when ready: ")
    match = handler.verify(finger, timeout=5)

    print "your fingerprints " + (match and "do match" or "do not match")
    if match:
        print "FIR payload is:", match

    # that's it
    handler.close()
