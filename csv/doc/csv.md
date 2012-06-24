# Working with CSV Datasets

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

    # Luminescence of evolved V. harveyi
    # Eric Bruger - 2012/06/27
    Temperature,Row,Column,Luminescence
    26.3,0,0,7444.945
    26.3,0,1,4845.375
    26.3,0,2,4056.362
    # Look at this luminescence!!!
    26.3,0,3,4883.137
    26.3,0,4,3593.289
    26.3,0,5,2645.281
    26.3,1,2,10507.588

It is important to note, however, that not all programs that support
CSV-formatted files support headers or comments. When using these programs,
these metadata should first be stripped from the file. This can easily be done
with several common tools available on the Unix command line, which will be
introduced later in this chapter. Alternately, thee metadata can be removed
manually or with a script.

## Including Replicates

In most cases, data sets will contain measurements from multiple replicates.
For example, the luminescence data might contain data from reads of multiple
plates. Since these data describe the same thing, it makes sense for them to be
stored in the same file.  However, if we just added these data to the end of
file, it would not be possible to differentiate between the data for row 0,
column 0 of the one plate and any other plate if we keep with the
Temperature-Row-Column-Luminescene format.

To handle replicates, we can add a new column for each entry that specifies the
plate from which each data point were acquired.

    # Luminescence of evolved V. harveyi
    # Eric Bruger - 2012/06/27
    Plate,Temperature,Row,Column,Luminescence
    Plate#1,26.3,0,0,7444.945
    Plate#1,26.3,0,1,4845.375
    Plate#1,26.3,0,2,4056.362
    Plate#1,26.3,0,3,4883.137
    Plate#1,26.3,0,4,3593.289
    Plate#1,26.3,0,5,2645.281
    Plate#2,30.0,0,0,5713.744
    Plate#2,30.0,0,1,3491.94
    Plate#2,30.0,0,2,2851.252
    Plate#2,30.0,0,3,3872.232
    Plate#2,30.0,0,4,2632.069
    Plate#2,30.0,0,5,1594.228

## Working with Time Series Data

Similarly, time series can be thought of as measurements replicated over time.
To augment our data set to show multiple reads of the plates over time, we can
simply add a column that indicates when the measurement was taken:

    # Luminescence of evolved V. harveyi
    # Eric Bruger - 2012/06/27
    Plate,Time,Temperature,Row,Column,Luminescence
    Plate#1,0:00,26.3,0,0,7444.945
    Plate#1,0:00,26.3,0,1,4845.375
    Plate#1,15:00,30.1,0,0,6088.0
    Plate#1,15:00,30.1,0,1,3976.694
    Plate#1,30:00,30.0,0,0,6563.678
    Plate#1,30:00,30.0,0,1,4188.048
    Plate#2,0:00,30.0,0,0,6716.929
    Plate#2,0:00,30.0,0,1,4153.633
    Plate#2,15:00,30.0,0,0,6672.662
    Plate#2,15:00,30.0,0,1,4167.991
    Plate#2,30:00,30.0,0,0,5810.844
    Plate#2,30:00,30.0,0,1,3652.258

As another example, the data below show reaction counts in one Avida population
over 1,000 updates for one population:

    # Reaction counts
    # Brian Connelly - 2012/03/03
    Update,NOT,NAND,AND,ORN,OR,ANDN,NOR,XOR,EQU
    98000.0,172.0,2.0,33.0,35.0,2167.0,1007.0,4377.0,0.0,0.0
    98100.0,195.0,4.0,40.0,28.0,2185.0,1085.0,4408.0,0.0,0.0
    98200.0,191.0,2.0,37.0,31.0,2147.0,1004.0,4278.0,0.0,0.0
    98300.0,177.0,5.0,32.0,27.0,2239.0,904.0,4363.0,0.0,0.0
    98400.0,191.0,6.0,45.0,30.0,2285.0,986.0,4390.0,0.0,0.0
    98500.0,187.0,11.0,34.0,22.0,2277.0,1072.0,4485.0,0.0,0.0
    98600.0,205.0,6.0,38.0,38.0,2417.0,956.0,4449.0,0.0,0.0
    98700.0,158.0,7.0,48.0,21.0,2461.0,930.0,4501.0,0.0,0.0
    98800.0,176.0,8.0,58.0,20.0,2265.0,931.0,4267.0,0.0,0.0
    98900.0,150.0,5.0,45.0,31.0,2199.0,1030.0,4440.0,0.0,0.0

Avida output data can be converted to CSV using the `avida2csv.py` script
included with BEACONToolkit.

## Excel and CSV files

Support for reading and writing data in CSV format is included in Microsoft
Excel and each of the Excel-like spreadsheet programs (e.g., Numbers, Google
Docs, OpenOffice Calc). Like with the native formats, CSV files can be opened
with the **Open** item in the **File** menu.

To save data as a CSV file in Excel, the **Save As** item in the **File** menu
is used. Shown below, the *Format*  should be set to *Comma Separated Values
(.csv)*.  Menu options for other spreadsheets vary slightly.

![Saving data as CSV with Excel](https://github.com/briandconnelly/BEACONToolkit/raw/master/csv/doc/figures/excel-saveas.png)

It should be noted, though, that formulas included in spreadsheets will not be
saved in the resulting CSV files, only their values.

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



## CSV files and the Unix Shell

Although the Unix command line is a very intimidating place for many people, it
contains many programs that can be used to manipulate CSV files very quickly
and easily.  This is especially useful for those who perform computational work
in Unix-based environments such as high-performance computing centers, Linux
workstations, and even Apple computers.  This section prevents a number of them
cookbook style, showing how to use commands to accomplish different tasks.  As
shown in a few examples, the real power of the Unix shell is in connecting
several of these commands to perform multiple operations at once.

### Replacing Newlines

Before we begin, though, we need to first talk about *newlines*.  Although you
normally don't see them, the end of each line in text files contains a newline
character. For some software, newlines can be a source of problems, because the
specific symbols that Windows computers and Unix computers (including Mac OS X
and Linux) use for newlines is different.

To use any of the commands shown in this section on files which were created on
a Windows machine, the newlines first need to be converted to the Unix format.
For example, the `dos2unix` command can be used to easily convert `myfile.csv`,
which was created on a Windows machine:

    dos2unix myfile.csv

### Stripping Comments

Some programs, such as Apple Numbers, do not support comments in CSV files.
Fortunately, comments can very easily be stripped using the `grep` command.
The following command strips out all lines that begin with the `#` character
from the file `luminescence.csv`:

    grep -v ^# luminescence.csv

This command will print the new contents.  To save them to a new file called
`luminescence-nocomments.csv`:

    grep -v ^# luminescence.csv > luminescence-nocomments.csv

In the Unix shell, the `>` character means to place the output of the previous
command into the given file.  If a file already exists with that name, it will
be replaced by the new one.

### Removing Headers

Headers can also be easily removed. To remove the first line from the
`luminescence.csv` file:

    cat luminescence.csv | sed "1 d"

This uses the Unix *pipe* (`|`) symbol to connect the output of the `cat`
program, which just prints the contents of the file, to the `sed` program,
which we use to filter out the first line. The `1` can be replaced in the
parameters to `sed` to allow a different number of lines to be skipped.

As before, the results of this command are printed. To save these results as a
new file, the output can be redirected:

    cat luminescence.csv | sed "1 d" > luminescence-noheader.csv

This command won't quite have the effect we want, though, because the first
line in `luminescence.csv` is a comment, not a header. We can combine these two
commands using pipes to first strip out comments, remove the first line of the
resulting data, and save the rest to a new file:

    cat luminescence.csv | grep -v ^# | sed "1 d" > luminescence-data.csv


### Combining Multiple Files

The `cat` program, which previously we've used to output the contents of a
file, can be used to combine two or more files. To write add the contents of
`data2.csv` after the contents of `data1.csv`,

    cat data2.csv >> data1.csv

Note that we used `>>` instead of `>`, which would have replaced `data1.csv`
with the contents of `data2.csv`. In the Unix shell, `>>` means to add the
output to the bottom of the given file if it exists.  Otherwise, a new file
will be created.  Now, `data1.csv` has the contents of both files. If
`data2.csv` had a header, this could cause some confusion, as there would be a
second header in the middle of the file. Combining what we did before, we can
first remove the first line of `data2.csv` before adding it to `data1.csv`:

    cat data2.csv | sed "1 d" >> data1.csv

Similarly, we can combine multiple files into 1 by listing all of them as
arguments to `cat`:

    cat data1.csv data2.csv data3.csv > combined.csv

Here, the contents of `data1.csv`, `data2.csv`, and `data3.csv` were combined
and placed in a new file called `combined.csv`. Doing this while also stripping
the headers from the files is a bit more complicated.


### Extracting Specific Columns

The `cut` command can be extrenely useful for extracting columns from a CSV
file. For example, to extract the third column (Temperature) from
`luminescence.csv`:

    cut -f 3 -d , luminescence.csv

where `-f 3` specifies that we want the third field, and `d ,` indicates that
the fields are separated by commas. We can specify multiple columns as well, so
to get the Time and Temperature of each entry in the data file and save it to a
new file called `timetemp.csv`:

    cut -f 2,3 -d , luminescence.csv > timetemp.csv

### Extracting Specific Rows

There are a number of ways in which specific rows can be extracted from CSV
files. The `head` and `tail` commands output the first and last rows of a file,
respectively. For example, to output the first 12 rows of `luminescence.csv`:

    head -n 12 luminescence.csv

Similarly, the last 8 rows of `luminescence.csv` can be shown with `tail`:

    tail -n 8 luminescence.csv

The `sed` command can be used to extract a range of lines. Here, we extract
lines 50 through 97:

    sed -n "50,97 p" luminescence.csv

Often, though, we want to extract rows based on specific criteria. For these
queries, the `grep` command can be used, which searches a file for a particular
pattern. Using `grep`, we can extract all data from Plate#2:

    grep "Plate#2" luminescence.csv

`grep` can support much more complex searches using *regular expressions*.
Many good references for regular expressions can be found online.
