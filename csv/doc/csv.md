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

While there is no official structure to CSV files, there is a common format
often followed when dealing with data. In particular, data should be organized
as a table, with one record per row, and where each record has the same number
of elements.  Each record in the table is a line in the CSV file, and each
element in a record is delimited with a specified *delimiter* (typically a
comma, hence CSV, though it need not be). Each element can be text, numeric
data, or a combination of the two.  For example, this is a valid CSV entry:

    Wild Type, 2, 3.0, 8/2

## Annotating CSV Files
To aid in understanding a dataset, *metadata*, or additional information about
the data, can be added by the use of *headers* and *comments*.  A header row is
used to describe the data stored in each column of a dataset.  Comments allow
CSV files to contain additional notes about the data, such as a description of
when and where the data were acquired, how the dataset was obtained, or any
remarks about a specific data point.  Comments are identified by a single
character, typically `#`, at the beginning of a line, and specify that all
subsequent text on that line should be ignored.  For comments that span
multiple lines, a comment character must be included at the beginning of each
line.  The following dataset includes both headers and comments:

    # This data set has both comments and headers
	Treatment, Replicate, Fitness
	1, 1, 1.0
	1, 2, 1.5
	2, 1, 1.1
	2, 2, 1.6

It is important to note, however, that not all programs that support
CSV-formatted files support headers or comments. When using these programs,
these metadata should first be stripped from the file. This can easily be done
with several common tools available on the Unix command line, which will be
introduced later in this chapter. Alternately, thee metadata can be removed
manually or with a script.

## Working with Time Series Data
The most unintuitive case (for me) of drafting data sets in the CSV format is
the time-series. But once you get the hang of thinking about your data in a 
tabular format, it will become second nature. Here is an example of a time series in
CSV format:

    # A fake dataset of fitness over time
	Treatment, Replicate, Time, Fitness
	1, 1, 1, 1.0
	1, 1, 2, 1.1
	1, 1, 3, 1.2
	1, 1, 4, 1.3
	1, 2, 1, 1.0
	1, 2, 2, 1.0
	1, 2, 3, 1.1
	1, 2, 4, 1.5


## Excel and CSV files

TODO: intro.  excel kind of a natural way to think about csvs.

Support for reading and writing data in CSV format is included in Microsoft
Excel and each of the Excel-like spreadsheet programs (e.g., Numbers, Google
Docs, OpenOffice Calc). Like with the native formats, CSV files can be opened
with the **Open** item in the **File** menu.

To save data as a CSV file in Excel, the **Save As** item in the **File** menu
is used. Shown below, the *Format*  should be set to *Comma Separated Values
(.csv)*.  Menu options for other spreadsheets vary slightly.

![Saving data as CSV with Excel](https://github.com/briandconnelly/BEACONToolkit/raw/master/csv/doc/figures/excel-saveas.png)

### Transposing Column-Based Data

CSV data is intended to be row-based, with each row representing a data point.
To export data that have been arranged in a column-based layout (see example
below), the data must first be transposed.

![Column-based data in Excel](https://github.com/briandconnelly/BEACONToolkit/raw/master/csv/doc/figures/excel-horizdata.png)

The easiest way to accomplish this is to select the data and copy it. Then,
select the cell that will be at the upper left area of the transpose data,
select **Paste Special...** from the **Edit** menu, and choose the *Transpose*
option before selecting the **OK** button.

![Excel's Paste Special Dialog Window](https://github.com/briandconnelly/BEACONToolkit/raw/master/csv/doc/figures/excel-paste_special.png)

Now that the data are arranged in rows, the other data can be deleted, and the
spreadsheet can be saved as a CSV file as described previously. This method of
copying data and pasting transposed is only supported in Excel and OpenOffice
Calc.

In Google Docs (as well as Excel), data can be transposed using the
**TRANSPOSE** function. To do this, first select a region of empty cells that
is equal in size to the data to be transposed.  For example, if the
column-based data occupies 3 rows by 9 columns as in the picture above, select
an area that is 9 rows by 3 columns.  Once the target region has been selected,
enter:

    =TRANSPOSE(A1:I3)

To take the data from the region bounded by cells A1 in the upper left and I3
in the lower right, transpose it, and paste it into the selected region. Excel
users should conclude entering this formula with Control-Shift-Enter instead of
Enter.

Unfortunately, Numbers does not provide any easy ways to transpose data.  The
best plan for these situations would be to export the column-based data as a
CSV file, read that file using the Python tools described in this Chapter, and
transpose the data in Python with a function like *transpose* in NumPy.


## Python and CSV files

There are a number of different ways for interacting with CSV data in Python.
All Python distributions include the csv module, described below, which allows
for reading and writing CSV-formatted data. Additional modules such as numpy
and Pandas also offer powerful tools for interacting with CSV-formatted
datasets. This section introduces each of these tools.

### Python's csv Module

#### Reading
All Python installations include the `csv` module, which provides functionality
for reading and writing CSV files. First, the following Python code opens and
reads a CSV file named `platedata.csv`:

    import csv

    myreader = csv.reader(open('platedata.csv', 'r'))

where `'r'` specifies that the file will be opened for reading. With this new
object called `myreader`, we can now iterate through the contents of the CSV
file line-by-line:

    for row in myreader:
        print "Read a row:", row

For each iteration of this loop, the `row` variable contains a list of values
from that row.  Because Python's list indices are zero-based, the value in the
second column of the current row is accessed as `row[1]`.

Python reads each row as a collection of string objects. To convert a value to
a numeric value, the `int` and `float` functions can be used:

    for row in myreader:
        as_pct = float(row[2])/100

If the values of all fields are numeric, they can all be converted at once:

    for row in myreader:
        floatvals = map(float, row)

Here, `floatvals` will be a list containing the numeric values of each field.

TODO: more
TODO: handling comments
TODO: handling headers

#### Writing

The `csv` module also supports writing data to CSV files. To create an object
that writes data to the file `platedata_modified.csv`:

    import csv

    mywriter = csv.writer(open('platedata_modified.csv', 'w'))

Where `'w'` specifies that we will be opening the file for writing. We can now
write rows of data to the file using the `writerow` method:

    data = [0.2, 0.3, 1.4]
    mywriter.writerow(data)

As a complete example, let's open `platedata.csv` for reading, read each row of
numeric data, calculate the 


* TODO: regular stuff
* TODO: dict stuff

### NumPy/scipy

* TODO: using genfromtxt - delimiter, names, etc.  automatically decompresses. 

    d = np.genfromtxt('Tax_Year_2007_County_Income_Data.csv', delimiter=',', names=True, comments='#', usecols=(0,1,3,4))

    np.mean(d['State_Code'])

Can use the unpack argument, which is helpful for plotting:

    (xvals, yvals) = np.genfromtxt('Tax_Year_2007_County_Income_Data.csv', delimiter=',', names=True, comments='#', usecols=(0,4), unpack=True)

Numpy expects numeric data.  Strings must be quoted.


* TODO: working with aggregates of datasets (stacking tables from replicate runs)


### Pandas

[Pandas](http://pandas.pydata.org) is a Python library designed to support data
reading, writing, and manipulation.  Notably, Pandas also includes
functionality for working with timeseries data.

Pandas provides a nice interface for interacting with CSV files. Similar to R,
when a CSV file is read with Pandas, the data are stored in a `DataFrame` object.

    import pandas as p
    data = p.read_csv("Tax_Year_2007_County_Income_Data.csv", header=0)

    print data

This code will produce the following output:

    Read Well   OD595
    0      1   A1  0.3501
    1      1   A2  0.3526
    2      1   A3  0.3514
    3      1   A4  0.3489
    4      1   A5  0.3487
    5      1   A6  0.3804
    ...

Individual columns in this `data` DataFrame can be accessed using their names,
which are gathered from the header in the CSV file:

    print data['OD595']

TODO

#### Reading CSV

TODO: describe example

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



## CSV files and UNIX shells

There are many classic command-line tools for Unix that can be used to
manipulate CSV files very quickly. This section prevents a number of them
cookbook style.

### Removing Headers
TODO: text

    your_cmd | sed "1 d"

### Stripping Comments
TODO: stripping comments with grep

### Replacing Newlines
TODO:
