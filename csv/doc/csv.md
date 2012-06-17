# Working with CSV datasets

Comma-separated value (CSV) files provide an application-agnostic way of 
storing and importing data into many applications. Because their content
is plain-text, they have a longer "shelf life" than proprietary file-formats
that depend on particular versions of applications. Dryad, the online data
repository, often requires uploaded data be in plain-text formats such as 
CSVs because of this reason. Despite all the obvious benefits of dealing with 
data in plain-text, several journals such as Evolution, Molecular Ecology, and 
AmNat are requiring data be made available in Dryad.

## Overview

While there is no real structure to CSV files, there is a common format often
followed when dealing with data. In particular, data should be organized as a
table where each entry has the same number of elements. Each of these entries 
in the table is a line in the CSV file, and each element in an entry is
delimited with a specified separator (typically a comma, hence CSV, though it
need not be). Elements are not limited in content, as long as they are
represented as plain-text. For example, this is a valid CSV entry:

    One, 2, 3.0, 8/2

Two other useful conventions in CSV files are headers and comments. Comments 
are identified by a single character, typically `#`, at the beginning of a
line. Any text after the comment character is conventionally ignored by most
(but not all) programs. A header row is used to assign names to each column in
a dataset. Here is a small dataset employing both headers and comments:

    # This data set has both comments and headers
	Treatment, Replicate, Fitness
	1, 1, 1.0
	1, 2, 1.5
	2, 1, 1.1
	2, 2, 1.6

The most unintuitive case (for me) of drafting data sets in the CSV format is
the time-series. But once you get the hang of thinking about your data in a 
tabular format, it will become second nature. Here is an example of a time series in
CSV format:

    # A fake dataset of fitness over time
	Treatmet, Replicate, Time, Fitness
	1, 1, 1, 1.0
	1, 1, 2, 1.1
	1, 1, 3, 1.2
	1, 1, 4, 1.3
	1, 2, 1, 1.0
	1, 2, 2, 1.0
	1, 2, 3, 1.1
	1, 2, 4, 1.5

intro
* format, benefits, etc.
* some common delimiters
* headers
* comments

## Python and CSV files

There are a number of different ways for interacting with CSV data in Python.
All Python distributions include the csv module, described below, which allows
for reading and writing CSV-formatted data. Additional modules such as numpy
and Pandas also offer powerful tools for interacting with CSV-formatted
datasets. This section introduces each of these tools.

### Python's csv Module

* TODO: regular stuff
* TODO: dict stuff

### NumPy/scipy

* TODO: using genfromtxt - delimiter, names, etc.  automatically decompresses. 

    d = np.genfromtxt('Tax_Year_2007_County_Income_Data.csv', delimiter=',', names=True, comments='#', usecols=(0,1,3,4))

    np.mean(d['State_Code'])

Can use the unpack argument, which is helpful for plotting:

    (xvals, yvals) = np.genfromtxt('Tax_Year_2007_County_Income_Data.csv', delimiter=',', names=True, comments='#', usecols=(0,4), unpack=True)


* TODO: working with aggregates of datasets (stacking tables from replicate runs)


### Pandas

[Pandas](http://pandas.pydata.org) is a Python library designed to support data
reading, writing, and manipulation.  Notably, Pandas also includes
functionality for working with timeseries data.


DataFrame

#### Reading CSV

TODO: describe example

    import pandas as p
    data = p.read_csv("Tax_Year_2007_County_Income_Data.csv", header=0)

TODO: adding, deleting, and selecting rows

    sc = a['State Code']
    sc[sc < 3]

TODO: grouping




## R and CSV files

brief overview of R and CSV


### Reading CSV files

TODO


### Writing CSV files

TODO


## Excel and CSV files

* TODO: reading/writing
* TODO: how to transpose data


## CSV files and UNIX shells

your_cmd | sed "1 d" - to remove first line of output

TODO: intro

