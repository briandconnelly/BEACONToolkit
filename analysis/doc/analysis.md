## Some Preliminary Thoughts (in R)

### What p-values aren't

Before we can get into analyzing data with computational tools, we first need to
understand a few basics about probability and statistics. Let's take a totally 
fictitious example of fish. Maybe we expect a particular species of fish to have
evolved larger bodies in cold environments but not hot ones. We can start by 
looking at the distributions of weight between samples of fish caught in these 
two different environments.

	cold_fish = rnorm(5000, mean=20.5, sd=5)
	hot_fish = rnorm(5000, mean=20, sd=5)
	
![Weight Boxplots](https://github.com/briandconnelly/BEACONToolkit/raw/master/analysis/doc/figures/fake_boxplot.png)

While this isn't really the analysis I would suggest, it appears there is no
difference between environments. Perhaps a slight increase in weight in cold
environments, but no more than a single kilogram. But, it turns out that if we
do a simple t-test our p-value is very small, less than 0.001.

	t.test(a,b)
	
	#output
	t = 4.0446, df = 9997.997, p-value = 5.281e-05

The point I'm trying to illustrate here is that p-values, while often important
for publication, tell you very little about what is actually important. In this 
case, the p-value is so small because we have so many samples. The slight 
difference is real and the p-value reflects that, but less than one kilogram 
difference has no biological meaning. Instead of thinking primarily about
p-values, you should think about effect sizes and what they mean for your 
hypotheses. 

### What p-values are

So what does a p-value tell you then? The p-value is simply the probability of 
observing as extreme data under the null hypothesis. The null hypothesis usually
ends up being that the slope is 0, or the mean is 0, or the difference between 
two samples is 0. We can demonstrate what exactly that means by computing the 
p-value of a sample, with the null hypothesis that the true mean is equal to 
zero, by resampling our data over and over again and counting the number of 
times we observe a mean less than or equal to zero. This technique is called 
bootstraping and sometimes more generally resampling. 

![New Fake Distribution](https://github.com/briandconnelly/BEACONToolkit/raw/master/analysis/doc/figures/fake_hist.png)

	cold_effects = rnorm(50, mean=1.0, sd=5)
	
Let's say this is the measured effect of cold temperature on bodyweight in some 
other species of fish. We want to know if there is really a trend of colder
temperatures and heavier fish. We can think about testing this by asking how
often we would see as extreme a mean if the true mean was zero. This would
require us to specify the distribution, and would be called a parametric 
Monte Carlo test. However, another way to ask this question would be how
often we would observe a mean less than or equal to zero if we resampled from
our data over and over again. This would be a resampling/bootstrap test.

![Resampled Distributions](https://github.com/briandconnelly/BEACONToolkit/raw/master/analysis/doc/figures/resamples.png)

Just to illustrate a bit of the variation we get when resampling from our data
over and over again, here are a few boxplots of individual resamplings. We can
perform a single resampling event by calling the `sample` function, specifiying
we want to sample with replacement by setting `replace=T`:

	sample(cold_effects, size=length(a), replace=T)

![Histogram of Resampled Means](https://github.com/briandconnelly/BEACONToolkit/raw/master/analysis/doc/figures/sampling_means.png)

And if we calculate the mean of these resampled distributions many many times, 
we get what is known as the sampling distribution of means. We can repeate this 
sampling process using the `replicate` function, here replicating it 100,000
times.

	sample_means <- replicate(100000, mean(sample(cold_effects, size=length(cold_effects), replace=T)))
	
Now we can ask how often, given our data, we see a mean that is equal or less
than zero, we can get a p-value out of this resampling process! 

	length(sample_means[sample_means <= 0])/num_samples
	
	#output
	[1] 0.07355

And we can compare this to the p-value given a normal one-tailed t-test:

	t.test(cold_effects, alternative="greater")
	
	#output
	t = 1.4379, df = 49, p-value = 0.07842
	
If you do these sort of resampling and bootstrap statistics often, you'll 
notice they are often the same as the parametric estimates. The power of these 
resampling and bootstrap statistics is in how easy they are to make and taylor 
to your specific hypotheses and data, not neccesariy in getting better or 
different results. 

## Analysis in R

Now that we have gone over a little bit about what statistics is (and what it 
isn't), we can go through a few of the traditional analysis methods using R. 
For this exercise, there is real data form a few runs of Avida studying 
host-parasite coevolution in `BEACONToolkit/analysis/data/parasite_data.csv`. 
This dataset has the diversity of the final host population using Shannon 
Diversity, which balances even distributions of abundance as well as species 
richness, measured at the end of runs with varying levels of parasite 
virulence. Here virulence just means the percentage of CPU cycles, or energy, the parasites steal from their hosts. 

We will go into more detail on plotting tools with R and Python in future tutorials, but it is always useful to look at your data. This includes using the `summary`, `head`, and `tail` functions as mentioned before, but also with plots. Just to get a sense of each level of virulence, we can plot these as factors as opposed to the continuous variable they really are.

	plot(ShannonDiversity ~ as.factor(Virulence), data=parasite_data)

![Diversity by Virulence Treatment](https://github.com/briandconnelly/BEACONToolkit/raw/master/analysis/doc/figures/diversity_vs_virulence.png)

My typical runs are done with virulence set to 0.8, so lets focus on that set of data.

	normal_parasites <-  parasite_data[na.omit(parasite_data$Virulence == 0.8), ]
	
We use `na.omit` because there are some Virulence values that are NA, or not present in the dataset. These are runs that do not have parasites, and we should hold on to those too as a control.

	no_parasites <- parasite_data[is.na(parasite_data$Virulence), ]

We can make a boxplot of just these two distributions to get a sense of how parasites affect host diversity with parasites at 0.8 virulence.

	boxplot(no_parasites$ShannonDiversity, normal_parasites$ShannonDiversity, ylab="Shannon Diversity", xlab="W and W.O. Parasites", main="Normal Parasite Runs (0.8 Virulence)")
	
![Diversity With and Without Parasites](https://github.com/briandconnelly/BEACONToolkit/raw/master/analysis/doc/figures/normal_parasites.png)

It is pretty obvious from just looking at the data that parasites have a large effect on host diversity, but we can start to quantify this difference using some of R's built-in functions. 

	mean(normal_parasites$ShannonDiversity)
	[1] 1.269134
	
	mean(no_parasites$ShannonDiversity)
	[1] 0.2519426
	
Well, those are pretty different! But, means doesn't tell us about the variation in our distributions. The variance and standard deviation are two common measures of spread that have built in functions in R. 

	var(normal_parasites$ShannonDiversity)
	[1] 0.6110384

	sqrt(var(normal_parasites$ShannonDiversity))
	[1] 0.7816895
	
	#or just sd()
	sd(normal_parasites$ShannonDiversity)
	[1] 0.7816895
	
This tells us about the variation in our observed data but not the sample distribution, which is what we care about. We want to know if we repeated this experiment over and over again, what would the variation in our observed mean be. We can get at this using the standard error of the mean or S.E.M., which is estimating the variation in the sampling distribution. Unfortunately there is no built-in R function for this, but it is relatively simple to compute.

	sem <- function(values) {sd(values)/sqrt(length(values))}
	sem(normal_parasites$ShannonDiversity)
	[1] 0.1105476
	
A very useful measure of our uncertainty in the estimated mean is the 95% confidence interval. These are roughly 2*S.E.M above and below the mean, but the exact number of S.E.Ms can be calculated using the t-distribution quantiles. Here we want the middle 95% of the values, so we want to know where the extreme 5% of the data falls, but split between extreme low and extreme high values (i.e., the lower 0.025 and upper 0.975 quantiles). 

	qt(c(0.025, 0.975), df=length(normal_parasites$ShannonDiversity))
	[1] -2.008559  2.008559
	
In this case, it is slightly more than 2 S.E.Ms. In general, with more than 20 or so samples, 2 is a good approximation for the 95% confidence intervals. Now we can calculate what our 95% confidence intervals are for the mean host diversity of typical parasite runs.

	c( mean(normal_parasites$ShannonDiversity) -2.008559*sem(normal_parasites$ShannonDiversity),  
	   mean(normal_parasites$ShannonDiversity) + 2.008559*sem(normal_parasites$ShannonDiversity))
	[1] 1.047092 1.491175
	
We could also use the `t.test` function to compute the 95% confidence intervals for us.

	t.test(normal_parasites$ShannonDiversity, conf.int=T)
	
	#output ignoring the rest, since it isn't relevant in this case
	95 percent confidence interval:
	 1.046980 1.491288
	 
The `t.test` function also returned a p-value, but for the null hypothesis that the true mean of this distribution is zero. While this may have some biological meaning, we have a control that we really want to test against. The `t.test` function can also perform a two-sample t-test and compare the means of two distributions. 


	t.test(normal_parasites$ShannonDiversity, no_parasites$ShannonDiversity)
	
	#output
	data:  normal_parasites$ShannonDiversity and no_parasites$ShannonDiversity 
	t = 8.1697, df = 73.546, p-value = 6.439e-12
	alternative hypothesis: true difference in means is not equal to 0 
	95 percent confidence interval:
	 0.7690772 1.2653053 
	sample estimates:
	mean of x mean of y 
	1.2691338 0.2519426
	
This time the p-value is telling us the probability of observing as extreme a difference between distributions given the null hypothesis that they have the same mean, and it is very very small. But, as we argued earlier, the more important measure is the actual difference between treatments rather than the p-value. In this case, the means are quite different: 1.26 as compared to 0.25. Conveniently, the 95% confidence intervals that are returned from a two-sample t-test is giving us information about the uncertainty in the estimated difference between distributions. We can see the difference is pretty substantial in this case. 

Now, if you remember back to the boxplot of diversities from runs without parasites, it didn't look very normally distributed. The median and lower quartile were squashed together close to zero. The t-test is parametric and makes the assumption that our data is normally distributed. While it is fairly robust to violations of that assumption, there are non-parametric tests designed to deal with data like these. In particular, the Wilcox Rank-Sum test, also known as the Mann-Whitney U Test, is a general non-parametric statistic. 

	 wilcox.test(normal_parasites$ShannonDiversity, no_parasites$ShannonDiversity, conf.int=T)

	 #output
	 	Wilcoxon rank sum test with continuity correction

	 data:  normal_parasites$ShannonDiversity and no_parasites$ShannonDiversity 
	 W = 2137.5, p-value = 3.787e-10
	 alternative hypothesis: true location shift is not equal to 0 
	 95 percent confidence interval:
	  0.9308314 1.4284676 
	 sample estimates:
	 difference in location 
	               1.140251

In this case, using a non-parametric test actually gave us more extreme values for our differences in means! 

## Statistical Analysis in Python

In this section, we introduce a few useful methods for analyzing your data in Python.
Namely, we cover how to compute the mean, variance, and standard error from a dataset.
For more advanced statistical analysis, we cover how to perform a
Mann-Whitney-Wilcoxon (MWW) RankSum test, how to perform an Analysis of variance (ANOVA)
between multiple distributions, and how to compute bootstrapped 95% confidence
intervals for non-normally distributed data.

### Python's SciPy Module

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

#### Mean

The mean performance of an experiment gives a good idea of how the experiment will
turn out *on average* under a given treatment.

	import scipy

	dataset_mean = scipy.mean(dataset_list)
	
	print "Dataset mean: ", dataset_mean

#### Variance

The variance in the performance provides a measurement of how consistent the results
of an experiment are. The lower the variance, the more consistent the results are, and
vice versa.

	import scipy
	
	dataset_variance = scipy.var(dataset_list)
	
	print "Variance around the mean: ", dataset_variance

#### Standard Error of the Mean (S.E.M.)

Combined with the mean, the S.E.M. enables you to establish a range around a mean that
the majority of any future replicate experiments will most likely fall within. 

	import scipy

	dataset_stderr = 1.96 * stats.sem(dataset_list)
	
	print "Standard error of the mean: ", dataset_stderr

A single S.E.M. will usually envelop 68% of the possible replicate means
and two S.E.M.s envelop 95% of the possible replicate means. Two
S.E.M.s are called the "estimated 95% confidence interval." The confidence
interval is estimated because the exact width depend on how many replicates
you have; this approximation is good when you have more than 20 replicates.

#### Mann-Whitney-Wilcoxon (MWW) RankSum test

The MWW RankSum test is a useful test to determine if two distributions are significantly
different or not. Unlike the t-test, the RankSum test does not assume that the data
are normally distributed, potentially providing a more accurate assessment of the datasets.

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
	
If P <= 0.05, we are confident that the distributions significantly differ, and
can claim that the treatment has a significant impact on the measured value.

#### One-way analysis of variance (ANOVA)

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
	
If P > 0.05, we can claim with confidence that the means of the results of all three
experiments are not significantly different.

#### Bootstrapped 95% confidence intervals

Oftentimes it's difficult to perform the 20+ replicate runs
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

### Python's pandas Module

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

#### Mean

Conveniently, DataFrames have all kinds of built-in functions to perform standard
operations on them en masse: `add()`, `sub()`, `mul()`, `div()`, `mean()`, `std()`, etc.
The full list is located at: http://pandas.sourceforge.net/generated/pandas.DataFrame.html

Thus, computing the mean of an entire DataFrame only takes one line of code:

	from pandas import *

	meanDF = experimentDF.mean()

#### Variance

Computing the variance is similarly easy:

	from pandas import *

	varianceDF = experimentDF.var()

#### Standard Error of the Mean (S.E.M.)

Since DataFrames don't have a built-in S.E.M. function, you have to compute it yourself:

	from pandas import *
	
	# standard error = standard deviation / sqrt(number of samples)
	standardDeviationDF = experimentDF.std()
	
	numSamples = len(experimentList)
	
	standardErrorDF = standardDeviationDF.div( sqrt(numSamples) )
	
	# 95% confidence interval around the mean = 1.96 * standard error
	confidenceIntervalDF = standardErrorDF.mul(1.96)

#### NumPy/SciPy methods on pandas DataFrames

Finally, NumPy and SciPy methods can be applied directly to pandas DataFrames with the
`aggregate()` function.

	import numpy as np

	meanDF = experimentDF.aggregate(np.mean)
	
	varianceDF = experimentDF.aggregate(np.var)
	
	# etc.