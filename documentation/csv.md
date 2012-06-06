# Working with CSV datasets

Comma-separated value (CSV) files are a plain-text

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

