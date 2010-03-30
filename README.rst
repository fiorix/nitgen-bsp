=========
NitgenBSP
=========
:Info: See `github <http://github.com/fiorix/nitgen-bsp>`_ for the latest source.
:Author: Alexandre Fiori <fiorix@gmail.com>

About
=====

NitgenBSP is a Python extentension based on the `Nitgen SDK for Linux <http://www.nitgen.com/eng/product/enbsp_sdk.html>`_. It currently supports Nitgen fingerprint recognition devices such as `Fingkey Hamster <http://www.nitgen.com/eng/product/finkey.html>`_ and `Fingkey Hamster II <http://www.nitgen.com/eng/product/finkey2.html>`_.

Implementation details
----------------------

- It has been tested under Ubuntu Linux 9.10
- Require root access level (actually depends on file permission of /dev/nitgen0)
- Only supports the auto-detection mode (I don't have 2 devices do try manual selection)
- Supports verification with the FIR Handle and Text-Encoded FIR (not the FULL FIR)
- Allows the Text-Encoded FIR to be saved on remote database for later verification
- Text-Encoded FIR does not allow multi-byte encoding
- Ships with `PIL <http://www.pythonware.com/products/pil/>`_ support and allows saving fingerprint images as JPG, PNG, etc

Documentation and Examples
==========================

The source code ships with built-in Python Docstring documentation for class reference. It also ships with examples in the `examples/ <http://github.com/fiorix/nitgen-bsp/tree/master/examples/>`_ subdirectory.

However, using NitgenBSP is pretty straightforward even for those with no experience with biometric devices.
Here is an example of simple usage::

 #!/usr/bin/env python
 # coding: utf-8
 
 import NitgenBSP

 if __name__ == "__main__":
    handler = NitgenBSP.Handler()

    finger = handler.capture()
    image = finger.image()
    image.save("out.png")

    print "your fingerprint text-encoded FIR is:", finger.text()

In the near future I'll provide support for the SDK's Search Engine API, and probably other features such as manual device selection. See the `TODO <http://github.com/fiorix/nitgen-bsp/tree/master/TODO>`_ for details.

Credits
=======
Thanks to (in no particular order):

- Nitgen Brazil
  
  - For providing documentation and granting permission for this code to be published
