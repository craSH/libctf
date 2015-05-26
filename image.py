#!/usr/bin/env python
"""
For use in meta/Neg9's libctf
Copyleft 2015 Ian Gallagher <crash@neg9.org>
"""

class PngFile(object):
    """
    Low-level representation of a PNG (Portable Network Graphics/PNG's Not GIF) image file.
    Any multibyte values are in network byte order (big-endian), e.g. ! or > for the struct module.

    References:
        * https://en.wikipedia.org/wiki/Portable_Network_Graphics
        * http://www.libpng.org/pub/png/spec/1.2/PNG-DataRep.html
        * http://www.libpng.org/pub/png/spec/1.2/PNG-Decoders.html
    """

    # Signature and header values that are common to all PNG files
    _valid_signature = bytearray('\x89PNG\x0D\x0A\x1A\x0A')
    assert(8 == len(_valid_signature))

    def __init__(self):
        self.mmap = None
        self.raw = bytearray()
        self.file_header = bytearray()


    def load_from_file(self, path):
    """
    Initialize object from a given file
    """

    # Open the specified file and load it as mmap data
    with open(path, 'rb') as png_fh:
        self.mmap = mmap.mmap(png_fh, 0)

    # Populate self.raw with newly populated mmap data
    self.raw = self.mmap.read()

    # Reset mmap to beginning
    self.mmap.seek(0)

    # Set file header
    try:
        self.file_header = bytearray(self.raw[:8])
    except Exception as ex:
        raise


    def validate_signature(self):
        """
        Validate that this object's magic header is correct
        Return: True if valid, False if invalid
        """

        signature_is_valid = False

        try:
            if(_valid_signature == self.file_header):
                signature_is_valid = True
        except Exception as ex:
            signature_is_valid = False

        return(signature_is_valid)



# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
