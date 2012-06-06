#!/usr/bin/env python

""" Plot selected columns from CSV data """

import argparse
import csv
import re
import string
import sys
import warnings

import numpy as np
import matplotlib.pyplot as plt

__version__ = "1.0"
__date__ = "2012-05-18"
__author__ = "Brian Connelly <bdc@msu.edu>"
__credits__ = "Brian Connelly <bdc@msu.edu>"
__maintainer__ = "Brian Connelly <bdc@msu.edu>"
__license__ = "Apache License Version 2.0"
__status__ = "Production"


def is_numeric(s):
    """Determine if a string is numeric"""
    try:
        float(s)
        return True
    except ValueError:
        return False;

def plot_csv():
    """Plot CSV data"""
    parser = argparse.ArgumentParser(description='Create plots from CSV data', version='{v}'.format(v=__version__))
    parser.add_argument('outfile', action='store', help='output file')
    parser.add_argument('-i', '--infile', type=argparse.FileType('rb'), default=sys.stdin, help='input file (default: stdin)')
    parser.add_argument('--title', action='store', help='display the given title')
    parser.add_argument('--legend', action='store_true', default=False, help='display a legend')
    parser.add_argument('--grid', action='store_true', default=False, help='display a grid')
    parser.add_argument('--transparent', action='store_true', default=False, help='use a transparent canvas')
    parser.add_argument('--dpi', action='store', type=float, default=80.0, help='DPI for raster graphics (default: 80)')

    parser.add_argument('-x', '--xcol', type=int, metavar='X', required=True, help='column number of data to be used for X axis (1-based)')
    parser.add_argument('--xlabel', metavar='L', help='label for X axis (default: name from column header)')
    parser.add_argument('--logX', action='store_true', default=False, help='use log scaling along the X axis')
    parser.add_argument('--xlim', type=float, nargs=2, help='minimum and maximum X values to be displayed')

    parser.add_argument('-y', '--ycols', type=int, nargs='+', metavar='Y', required=True, help='column number of data to be used for X axis (1-based)')
    parser.add_argument('--ylabel', metavar='L', help='label for Y axis (default: name from column header)')
    parser.add_argument('--logY', action='store_true', default=False, help='use log scaling along the Y axis')
    parser.add_argument('--ylim', type=float, nargs=2, help='minimum and maximum Y values to be displayed')
    parser.add_argument('--labels', nargs='+', help='labels to be used for plotted columns')

    cmd_args = parser.parse_args()

    if cmd_args.labels and cmd_args.ycols and len(cmd_args.labels) != len(cmd_args.ycols):
        print("Error: number of labels ({nl}) must match number of columns for Y axis ({nc})".format(nl=len(cmd_args.labels), nc=len(cmd_args.ycols)))
        sys.exit(1)

    #----- Read the data -----------------------------------

    reader = csv.reader(cmd_args.infile)
    header = None

    rownum = 0
    xlist = []
    ylist = []

    for row in reader:
        # Skip empty rows
        if len(row) == 0:
            continue

        rownum += 1

        # Skip rows that are not data
        if not is_numeric(row[0]):
            if rownum == 1:
                header = row
            continue

        row = map(float, row)

        xlist.append(row[cmd_args.xcol-1])
        ylist.append([row[r-1] for r in cmd_args.ycols])

    cmd_args.infile.close()

    xvals = np.array(xlist)
    yvals = np.array(ylist)

    #----- Get labels for the legend -----------------------

    if cmd_args.labels:
        labels = cmd_args.labels
    else:
        if header:
            labels = [header[i-1] for i in cmd_args.ycols]
        elif cmd_args.legend:
            print("Error: Must supply labels for legend (data has no header)")
            sys.exit(2)

    #----- Create the plot ---------------------------------

    fig = plt.figure()
    ax = plt.subplot(1,1,1)

    if cmd_args.title:
        plt.title(cmd_args.title)

    if cmd_args.grid:
        ax.grid()

    for c in range(yvals.shape[1]):
        ax.plot(xvals, yvals[:, c], linestyle='solid')

    if cmd_args.xlim:
        ax.set_xlim([cmd_args.xlim[0], cmd_args.xlim[1]])
    if cmd_args.ylim:
        ax.set_ylim([cmd_args.ylim[0], cmd_args.ylim[1]])

    if cmd_args.logX:
        ax.set_xscale('log')
    if cmd_args.logY:
        ax.set_yscale('log')

    if cmd_args.xlabel:
        plt.xlabel(cmd_args.xlabel)
    elif header:
        plt.xlabel(header[cmd_args.xcol-1])

    if cmd_args.ylabel:
        plt.ylabel(cmd_args.ylabel)
    elif len(cmd_args.ycols) == 1:
        plt.ylabel(header[cmd_args.ycols[0]-1])

    if cmd_args.legend:
        plt.legend(labels)

    try:
        plt.tight_layout()
    except AttributeError:
        warnings.warn("Matplotlib is out-of-date.  Consider upgrading.", RuntimeWarning, stacklevel=2)
        pass

    plt.savefig(cmd_args.outfile, transparent=cmd_args.transparent, dpi=cmd_args.dpi)

if __name__ == '__main__':
    plot_csv()
