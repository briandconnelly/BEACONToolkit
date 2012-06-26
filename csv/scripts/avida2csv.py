#!/usr/bin/env python

""" Convert Avida output files to CSV format for easier use with programs such as R, Excel, Python, etc."""

import argparse
import csv
import re
import string
import sys

__version__ = "1.0"
__date__ = "2012-05-18"
__author__ = "Brian Connelly <bdc@msu.edu>"
__credits__ = "Brian Connelly <bdc@msu.edu>"
__maintainer__ = "Brian Connelly <bdc@msu.edu>"
__license__ = "Apache License Version 2.0"
__status__ = "Production"


def avida2csv():
    parser = argparse.ArgumentParser(description='Convert Avida output files to CSV format',
                                     version='{v}'.format(v=__version__))

    parser.add_argument('-c', '--comments', dest='comment_char', default='#',
                        metavar='C',
                        help='character to be used for comments (default #)')
    parser.add_argument('-d', '--delimiter', dest='delimiter', default=',',
                        metavar='D', help='delimiter (default ,)')
    parser.add_argument('-H', '--noheader', dest='header', action='store_false',
                        default=True, help='do not write header information')
    parser.add_argument('-i', '--infile', type=argparse.FileType('rb'),
                        default=sys.stdin,
                        help='input file (default: stdin)')
    parser.add_argument('-o', '--outfile', nargs='?', type=argparse.FileType('w'),
                        default=sys.stdout, help='output file (default: stdout)')
    cmd_args = parser.parse_args()

    w = csv.writer(cmd_args.outfile, delimiter=cmd_args.delimiter)

    header = []

    for line in cmd_args.infile:
        line = line.rstrip()

        # Comments describing each column are saved for creating a header row
        # All non-alphanumeric characters are replaced with _
        m = re.match("^\s*#\s*(?P<colnum>\d+):\s*(?P<description>.*)$", line)
        if m:
            header.append(re.sub(r'\W+', '_', m.group('description')))

        m = re.match("^\s*#", line)
        if m:
            # Skip comment lines
            continue
        else:
            line_toks = line.split(" ")

            if len(line_toks) == 0:
                continue
            elif len(line_toks) == 1 and line_toks[0] == '':
                if cmd_args.header:
                    w.writerow(header)
                continue

            vals = map(float, line_toks)
            w.writerow(vals)

    cmd_args.infile.close()
    cmd_args.outfile.close()

if __name__ == '__main__':
    avida2csv()
