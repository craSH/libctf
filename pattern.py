#!/usr/bin/env python

"""
This code originally from Eugene Ching
https://github.com/eugeneching/exploit-pattern
"""

import re
import sys
import argparse

uppercase = [chr(x) for x in xrange(65, 91)]
lowercase = [chr(x) for x in xrange(97, 123)]
digits = [str(x) for x in xrange(0, 10)]

def pattern_gen(length):
    """
    Generate a pattern of a given length up to a maximum
    of 20280 - after this the pattern would repeat
    """
    pattern = ''
    for upper in uppercase:
        for lower in lowercase:
            for digit in digits:
                if len(pattern) < length:
                    pattern += upper+lower+digit
                else:
                    out = pattern[:length]
                    print out
                    return


def pattern_search(search_pattern):
    """
    Search for search_pattern in pattern.  Convert from hex if needed
    Looking for needle in haystack
    """
    needle = search_pattern

    try:
        if needle.startswith('0x'):
            # Strip off '0x', convert to ASCII and reverse
            needle = needle[2:].decode('hex')
            needle = needle[::-1]
    except TypeError as e:
        print 'Unable to convert hex input:', e
        sys.exit(1)

    haystack = ''
    for upper in uppercase:
        for lower in lowercase:
            for digit in digits:
                haystack += upper+lower+digit
                found_at = haystack.find(needle)
                if found_at > -1:
                    print('Pattern %s first occurrence at position %d in pattern.' %
                                (search_pattern, found_at))
                    return

    print ('Couldn`t find %s (%s) anywhere in the pattern.' %
            (search_pattern, needle))


def print_help():
    print 'Usage: %s LENGTH|PATTERN' % sys.argv[0]
    print
    print 'Generate a pattern of length LENGTH or search for PATTERN and '
    print 'return its position in the pattern.'
    print
    sys.exit(0)


if __name__ == '__main__':
	if len(sys.argv) < 2:
		print_help()

	if sys.argv[1] == '-s':
		pattern_search(sys.argv[2])
	elif sys.argv[1].isdigit():
		pattern_gen(int(sys.argv[1]))
	else:
		print_help()
