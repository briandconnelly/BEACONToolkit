# Statistical Analysis in Python

In this section, we introduce a few useful methods for analyzing your data in Python.
Namely, we cover how to compute the mean, variance, and standard error of a dataset.
For more advanced statistical analysis, we cover how to perform a
Mann-Whitney-Wilcoxon (MWW) RankSum test, how to perform an Analysis of variance (ANOVA)
between multiple datasets, and how to compute bootstrapped 95% confidence intervals for
non-normally distributed datasets.

## Python's SciPy Module

The majority of data analysis in Python can be performed with the SciPy module. SciPy
provides a plethora of statistical functions and tests that will handle the majority of
your analytical needs. If we don't cover a statistical function or test that you require
for your research, SciPy's full statistical library is described in detail at:
http://docs.scipy.org/doc/scipy/reference/tutorial/stats.html

In the examples below, `dataset_list` represents the list of data that you wish to
analyze. e.g., `dataset_list` could be a list of 30 best fitness values from 30 replicate
runs of an Avida experiment. For the purposes of those following along with the examples,
`dataset_list` will be a set of normally-distributed numbers:

	import numpy as np

	dataset_list = np.random.normal(20, 5, 30)

### Mean

The mean performance of an experiment gives a good idea of how the experiment will
turn out *on average* under a given treatment.

	import scipy

	dataset_mean = scipy.mean(dataset_list)
	
	print "Dataset mean: ", dataset_mean

### Variance

The variance in the performance provides a measurement of how consistent the results
of an experiment are. The lower the variance, the more consistent the results are, and
vice versa.

	import scipy
	
	dataset_variance = scipy.var(dataset_list)
	
	print "Variance around the mean: ", dataset_variance

### Standard Error of the Mean (S.E.M.)

Combined with the mean, the S.E.M. enables you to establish a range around a mean that
the majority of any future replicate experiments will most likely fall within. A general
rule of thumb is to have at least 30 replicate runs to compute a reliable S.E.M.

	import scipy

	dataset_stderr = 1.96 * stats.sem(dataset_list)
	
	print "Standard error of the mean: ", dataset_stderr

A single S.E.M. will envelop 68% of the possible replicate means; two S.E.M.s (1.96, to
be precise) envelop 95% of the possible replicate means. Thus, two S.E.M.s are also
called the "estimated 95% confidence interval."

### Mann-Whitney-Wilcoxon (MWW) RankSum test

The MWW RankSum test is a useful test to determine if two datasets are significantly
different or not. Unlike the t-test, the RankSum test does not assume that the datasets
are normally distributed, thus providing a more accurate assessment of the datasets.

As an example, let's say we want to determine if the results of the two following
experiments significantly differ or not:

	import numpy as np

	experiment1 = np.random.rand(1, 30)
	experiment2 = np.random.rand(1, 30)

A quick RankSum test will provide a P value indicating whether or not the two
distributions are the same.

	from scipy import stats
	
	z_stat, p_val = stats.ranksums(experiment1, experiment2)
	
	print "MWW RankSum P = ", p_val
	
If P <= 0.05, we are highly confident that the distributions significantly differ, and
can claim that the treatment has a significant impact on the measured value.

### One-way analysis of variance (ANOVA)

If you need to compare more than two datasets at a time, an ANOVA is your best bet. For
example, we have the results from three experiments with overlapping 95% confidence
intervals, and we want to confirm that the results for all three experiments are not
significantly different.

	import numpy as np

	experiment1 = np.random.rand(1, 30)
	experiment2 = np.random.rand(1, 30)
	experiment3 = np.random.rand(1, 30)

	from scipy import stats
	
	f_val, p_val = stats.f_oneway(experiment1, experiment2, experiment3)
	
	print "One-way ANOVA P = ", p_val
	
If P > 0.05, we can claim with high confidence that the means of the results of all three
experiments are not significantly different.

### Bootstrapped 95% confidence intervals

Oftentimes in wet lab research, it's difficult to perform the 30 replicate runs
recommended for computing reliable confidence intervals with S.E.M. In this case,
bootstrapping the confidence intervals is a much more accurate method of determining
the 95% confidence interval around your experiment's mean performance.

Unfortunately, SciPy doesn't have bootstrapping built into its standard library yet. On
the bright side, however, we have a pre-built bootstrapping function below:

	# Confidence interval bootstrapping function
	# Written by: cevans
	# URL: https://bitbucket.org/cevans/bootstrap/
	#
	# Input parameters:
   	#	data        = data to get bootstrapped CIs for
    #	statfun     = function to compute CIs over (usually, mean)
    #	alpha       = size of CIs (0.05 --> 95% CIs). default = 0.05
    #	n_samples   = # of bootstrap populations to construct. default = 10,000
	#
	# Returns:
   	#	bootstrapped confidence interval: [low, high]

	from numpy.random import randint
	from scipy.stats import norm
	from numpy import *

	def ci(data, statfun, alpha=0.05, n_samples=10000, method='bca'):
       
        # Ensure that our data is, in fact, an array.
        data = array(data)

        # First create array of bootstrap sample indexes:
        indexes = randint(data.shape[0],size=(n_samples,data.shape[0]))

        # Then apply this to get the bootstrap samples and statistics over them.
        samples = data[indexes]

        stat = array([statfun(x) for x in samples])
        
        # Normal-theory Interval --- doesn't use sorted statistics.
        if method == 'nti':
                bstd = std(stat)
                pass
        
        stat_sorted = sort(stat)
        
        # Percentile Interval
        if method == 'pi':
                return ( stat_sorted[round(n_samples*alpha/2)],	stat_sorted[round(n_samples*(1-alpha/2))] )

        # Bias-Corrected Accelerated Interval
        elif method == 'bca':
                ostat = statfun(data)

                z = norm.ppf( ( 1.0*sum(stat < ostat) + 0.5*sum(stat == ostat) ) / (n_samples + 1) )
                
                # Calculate the jackknife distribution and corresponding statistics quickly.
                j_indexes = (lambda n: delete(tile(array(range(0,n)),n),range(0,n*n,n+1)).reshape((n,n-1)))(len(data))
                jstat = [statfun(x) for x in data[j_indexes]]
                jmean = mean(jstat)

                a = sum( (jstat - jmean)**3 ) / ( 6.0 * sum( (jstat - jmean)**2 )**1.5 )

                zp = z + norm.ppf(1-alpha/2)
                zm = z - norm.ppf(1-alpha/2)

                a1 = norm.cdf(z + zm/(1-a*zm))
                a2 = norm.cdf(z + zp/(1-a*zp))

                return (stat_sorted[round(n_samples*a1)],stat_sorted[round(n_samples*a2)])

        else:
                raise "Method %s not supported" % method

Bootstrapping 95% confidence intervals around the mean with this function is simple:

	import scipy
	import numpy as np

	experiment1 = np.random.rand(1, 10)

	CIs = ci(experiment1, scipy.mean)
	
	print "Bootstrapped 95% confidence interval low: ", CIs[0], ", high: ", CIs[1]
	
Note that you can change the range of the confidence interval by setting the alpha:

	# 90% confidence interval
	ci(experiment1, scipy.mean, alpha=0.1)

And also modify the size of the bootstrapped sample pool that the confidence intervals
are taken from:

	# bootstrap 20,000 samples instead of only 10,000
	ci(experiment1, scipy.mean, n_samples=20000)
	
Generally, bootstrapped 95% confidence intervals provide more accurate confidence
intervals than 95% confidence intervals computed from the S.E.M.

## Python's pandas Module

The pandas module provides powerful, efficient, R-like DataFrame objects capable of
calculating statistics en masse on the entire DataFrame. DataFrames are very useful
for when you need to compute statistics over multiple replicate runs.

For the purposes of this tutorial, `experimentList` and `experimentDF` shall be assigned
by the following Python code:

	from pandas import *
	import glob
	
	experimentList = []
  	
  	# read all of the csv files into a list of DataFrames
    for datafile in glob.glob("*.csv"):
  
        experimentList.append(read_csv(datafile))
    
    # concatenate all of the DataFrames together into a single DataFrame,
    # then group the data by columns
    experimentDF = (concat(experimentList, axis=1, keys=range(len(dataLists[key])))
            		.swaplevel(0, 1, axis=1)
            		.sortlevel(axis=1)
            		.groupby(level=0, axis=1)

### Mean

Conveniently, DataFrames have all kinds of built-in functions to perform standard
operations on them en masse: `add()`, `sub()`, `mul()`, `div()`, `mean()`, `std()`, etc.
The full list is located at: http://pandas.sourceforge.net/generated/pandas.DataFrame.html

Thus, computing the mean of an entire DataFrame only takes one line of code:

	from pandas import *

	meanDF = experimentDF.mean()

### Variance

Computing the variance is similarly easy:

	from pandas import *

	varianceDF = experimentDF.var()

### Standard Error of the Mean (S.E.M.)

Since DataFrames don't have a built-in S.E.M. function, you have to compute it yourself:

	from pandas import *
	
	# standard error = standard deviation / sqrt(number of samples)
	standardDeviationDF = experimentDF.std()
	
	numSamples = len(experimentList)
	
	standardErrorDF = standardDeviationDF.div( sqrt(numSamples) )
	
	# 95% confidence interval around the mean = 1.96 * standard error
	confidenceIntervalDF = standardErrorDF.mul(1.96)

### NumPy/SciPy methods on pandas DataFrames

Finally, NumPy and SciPy methods can be applied directly to pandas DataFrames with the
`aggregate()` function.

	import numpy as np

	meanDF = experimentDF.aggregate(np.mean)
	
	varianceDF = experimentDF.aggregate(np.var)
	
	# etc.