#!/usr/bin/env python
# coding: utf-8

import os
import time
import NitgenBSP

if __name__ == "__main__":
    assert os.getuid() == 0, "please run as root"

    # get the bsp handler
    nbio = NitgenBSP.Handler()

    # get the search engine handler
    search = NitgenBSP.SearchEngine(nbio)

    # search.load("/tmp/nitgen.db")

    # capture new fingerprint
    raw_input("place your finger in the device and press enter: ")

    # insert into the db
    userID = int(time.time())
    finger = nbio.capture()
    print "adding user %d into the search engine" % userID
    search.insert_user(userID, finger)

    # identify user in the db
    # other = nbio.capture()
    # userID = search.identify(other)

    # automatically capture new fingerprint and identify
    raw_input("place your finger in the device and press enter: ")
    userID = search.identify()
    print "your userID is:", userID

    # search.save("/tmp/nitgen.db")

    # close nbio handler
    nbio.close()
