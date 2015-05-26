#!/usr/bin/env python
"""
For use in meta/Neg9's libctf
Copyleft 2015 Ian Gallagher <crash@neg9.org>
"""

import mmap as _mmap
import struct as _struct
import zlib as _zlib

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

    _critical_chunks = (
        bytearray('IHDR'), # Must be the first chunk; it contains (in this order) the image's
                           # width, height, bit depth and color type.

        bytearray('PLTE'), # Contains the palette; list of colors.

        bytearray('IDAT'), # Contains the image, which may be split among multiple IDAT chunks.
                           # Such splitting increases filesize slightly, but makes it possible to
                           # generate a PNG in a streaming manner. The IDAT chunk contains the
                           # actual image data, which is the output stream of the compression algorithm.

        bytearray('IEND'), # Marks the image end.
    )

    _ancillary_chunks = (
        bytearray('bKGD'), # Gives the default background color. It is intended for use when there is no
                           # better choice available, such as in standalone image viewers (but not web
                           # browsers; see below for more details).

        bytearray('cHRM'), # Gives the chromaticity coordinates of the display primaries and white point.

        bytearray('gAMA'), # Specifies gamma.

        bytearray('hIST'), # Can store the histogram, or total amount of each color in the image.

        bytearray('iCCP'), # ICC color profile.

        bytearray('iTXt'), # UTF-8 text, compressed or not, with an optional language tag. iTXt chunk
                           # with the keyword 'XML:com.adobe.xmp' can contain Extensible Metadata Platform (XMP).

        bytearray('pHYs'), # Holds the intended pixel size and/or aspect ratio of the image.

        bytearray('sBIT'), # (Significant bits) indicates the color-accuracy of the source data.

        bytearray('sPLT'), # Suggests a palette to use if the full range of colors is unavailable.

        bytearray('sRGB'), # Indicates that the standard sRGB color space is used.

        bytearray('sTER'), # Stereo-image indicator chunk for stereoscopic images.

        bytearray('tEXt'), # Can store text that can be represented in ISO/IEC 8859-1, with one name=value pair
                           # for each chunk.

        bytearray('tIME'), # Stores the time that the image was last changed.

        bytearray('tRNS'), # Contains transparency information. For indexed images, it stores alpha
                           # channel values for one or more palette entries. For truecolor and
                           # grayscale images, it stores a single pixel value that is to be regarded
                           # as fully transparent.

        bytearray('zTXt'), # Contains compressed text with the same limits as tEXt.

    )

    # Create a tuple of all possible (standardized) chunk types that could be present in a PNG file.
    _potential_chunks = _critical_chunks + _ancillary_chunks


    def __init__(self, strict=False):
        # If strict is set, fail on bad chunks, etc.
        self.strict = strict

        # Class members to hold the actual file data, etc.
        self.mmap = None
        self.raw = None
        self.size = None
        self.file_header = None

        # Slightly higher level structured data
        self.chunks = list()


    def load_from_file(self, path):
        """
        Initialize object from a given file
        """

        # Open the specified file and load it as mmap data
        with open(path, 'rb') as png_fh:
            self.mmap = _mmap.mmap(png_fh.fileno(), 0, access=_mmap.ACCESS_READ)

        # Populate self.size with the file's total size
        self.size = self.mmap.size()

        # Populate self.raw with newly populated mmap data
        self.raw = bytearray(self.mmap.read(self.size))

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
            if(PngFile._valid_signature == self.file_header):
                signature_is_valid = True
        except Exception as ex:
            signature_is_valid = False

        return(signature_is_valid)

    def extract_chunk(self, chunk_offset, reset_pos=True):
        """
        Extract a chunk by it's offset.
        This can be done at any time (random access).
        """

        try:
            # Initialize a new PngChunk object for the next chunk we'll read
            chunk = PngFile.PngChunk()

            # Store current offset of chunk
            chunk.offset = chunk_offset

            # Seek to specified offset
            self.mmap.seek(chunk_offset)

            # Read length of current chunk
            chunk.length = _struct.unpack('>I', self.mmap.read(4))[0]

            # Read chunk type/name (4 bytes, FourCC style)
            chunk.type = bytearray(self.mmap.read(4))

            if self.strict:
                assert(chunk.type in PngFile._potential_chunks)

            # Read chunk data
            chunk.data = bytearray(self.mmap.read(chunk.length))

            # Read claimed CRC value
            chunk.crc_claim = bytearray(self.mmap.read(4))

        except Exception as ex:
            if(self.strict):
                raise
            else:
                return(None)

        finally:
            # Reset mmap to 0 if requested to
            if reset_pos:
                self.mmap.seek(0)

        return(chunk)

    def process_chunks(self):
        # Seek past the fixed header
        self.mmap.seek(len(PngFile._valid_signature))

        # Read chunks!
        try:
            while(self.mmap.tell() < self.mmap.size()):
                # Initialize a new PngChunk object for the next chunk we'll read
                chunk = self.extract_chunk(self.mmap.tell(), reset_pos=False)

                # Chunk processed! Add to the list of chunks
                self.chunks.append(chunk)

        except Exception as ex:
            if(self.strict):
                raise
            else:
                pass

        finally:
            # Reset mmap to 0
            self.mmap.seek(0)

        if(self.chunks):
            return(True)
        else:
            return(False)


    class PngChunk(object):
        """
        A small class to define a single PNG image chunk structure
        """

        def __init__(self):
            self.offset = None
            self.length = None
            self.type = None
            self.data = None
            self.crc_claim = None

def _test(path):
    ret_val = -1

    try:
        # Load the file
        png = PngFile(strict=True)
        png.load_from_file(path)

        # Check if the file signature is valid
        _sig_valid = png.validate_signature()
        if(_sig_valid):
            ret_val = 0
            print("PNG File signature validated!")
        else:
            ret_val = 1
            print("PNG File signature INVALID.")

        # Try to process all chunks
        if(png.process_chunks()):
            ret_val = 0
            print("Processed {0:d} chunks.".format(len(png.chunks)))
        else:
            ret_val = 1
            print("Failed processing chunks.")



    except Exception as ex:
        raise
        ret_val = 255

    return(ret_val)


if '__main__' == __name__:
    import sys
    if (len(sys.argv) < 2):
        sys.stderr.write("Please specify file to test on the command line.\n")
        sys.exit(-1)

    ret_val = _test(sys.argv[1])
    if(0 != ret_val):
        print "test() returned an error."

    sys.exit(ret_val)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
