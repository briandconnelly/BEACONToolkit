## Some Preliminary Thoughts (in R)

### What p-values aren't

Before we can get into analyzing data with computational tools, we first need
to understand a few basics about probability and statistics. Perhaps nothing is
used more frequently in statistics than the p-value, which is used to reject
some null hypothesis. To examine the p-value, let's take a totally fictitious
example of fish. Maybe we expect a particular species of fish to have evolved
larger bodies in cold environments but not hot ones. We can start by looking at
the distributions of weight between samples of fish caught in these two
different environments.

	cold_fish = rnorm(5000, mean=20.5, sd=5)
	hot_fish = rnorm(5000, mean=20, sd=5)
	
![Weight Boxplots](https://github.com/briandconnelly/BEACONToolkit/raw/master/analysis/doc/figures/fake_boxplot.png)

Based on this overly-simplistic analysis, there appears to be no difference
between environments. There may be a slight increase in weight in cold
environments, but no more than a single kilogram. However, it turns out that if
we do a simple t-test, our p-value is very small, less than 0.001.

	t.test(a,b)
	
	#output
	t = 4.0446, df = 9997.997, p-value = 5.281e-05

The point of this example is to demonstrate that p-values, which are often
considered an absolute must for presenting results, can reveal very little
about what is actually important. In this case, the p-value is so small because
we have so many samples. The slight difference is real and the p-value reflects
that, but less than one kilogram difference has no biological meaning. Instead
of thinking primarily about p-values, you should think about effect sizes and
what they mean for your hypotheses. 

### What p-values are

So what does a p-value tell you then? The p-value is simply the probability of
observing data as extreme as those seen in your data set under the null
hypothesis. The null hypothesis usually ends up being that the slope is 0, the
mean is 0, or the difference between two samples is 0. 

Let's say we also have a data set of the measured effect of cold temperature on
body weight in some other species of fish.  We want to know if this effect size
could be explained simply by chance and the real effect is statistically 
indistinguishble from zero.

	cold_effect = rnorm(50, mean=1.0, sd=5)
	
One way to test this would be to ask how often we would see this mean effect 
size if the true mean was zero.  This would be called a parametric 
**Monte Carlo** test. To do this, we would need to specify a distribution for
these temperature means to be drawn from.  In this case we know our data came
from a normal distribution, so we could perform this test by looking at means
from a set of random numbers drawn from this null distribution (with mean=0)
and estimate the probability of observing a mean as extreme as the one we
actually observed in `cold_effects`. 
	
	#first define how many samples we'll be doing -- the more the better
	num_samples <- 100000

	#generate a sample mean distribution under the null hypothesis
	monte_carlo_samples <- replicate(num_samples, mean(rnorm(length(cold_effect), mean=0, sd=sd(cold_effect))))
	
	#we can look at it
	hist(monte_carlo_samples, main="Monte Carlo Simulated Means")

	p_val <- length(monte_carlo_samples[monte_carlo_samples >= mean(cold_effect)])/length(monte_carlo_samples)
	print(paste("p-value = ", p_val))
	
	#output
	[1] "p-value =  0.00105"
	
![Monte Carlo](https://github.com/briandconnelly/BEACONToolkit/raw/master/analysis/doc/figures/monte_carlo.png)
	
We can compare our simulated p-value to the t-test closed form solution and see
that they are quite similar. 

	#compare this to the t-test p-value
	t.test(cold_effect, alternative="greater")
	
	#output
	t = 3.0718, df = 49, p-value = 0.001734


### What 95% confidence intervals are

Another frequently-used statistic is the 95% confidence interval. Along with
p-values, there is often a lot of confusion about what 95% confidence intervals
are.  The most common interpretation is that they are the range of values where
you expect the true mean to fall 95% of the time. Unfortunately, this is not
exactly what they are.  Instead, they tell you where your *estimated mean* will
fall 95% of the time if you were to replicate your experiment over and over
again. In this section, we will quickly show you what this means and how you
can begin using bootstrapping to estimate 95% confidence intervals for your
data sets. 

Lets say we have a distribution, here `cold_effects` will serve as our data.
The 95% confidence interval tells us if we were to go back out to the ocean and
sample fish again thousands and thousands of times, where the mass of our
estimated means would fall. We can think about this process as sampling from
the underlying distribution over and over again, and while we don't have the
underlying distribution, we do have an empirical one. With bootstrapping and
resampling techniques in general, we treat our empirical distribution as the
underlying distribution and sample repeatedly from it. 

Just to illustrate a bit of the variation we get when resampling from our data
over and over again, here are a few box plots of individual resamplings. We can
perform a single resampling event by calling the `sample` function, specifying
we want to sample with replacement by setting `replace=T`:

	sample(cold_effects, size=length(a), replace=T)

![Resampled Distributions](https://github.com/briandconnelly/BEACONToolkit/raw/master/analysis/doc/figures/resamples.png)

If we calculate the mean of these resampled distributions many, many times, we
get what is known as the sampling distribution of means. We can repeat this
sampling process using the `replicate` function, here replicating it 100,000
times.

	sample_means <- replicate(100000, mean(sample(cold_effects, size=length(cold_effects), replace=T)))
	
![Sample Mean Distribution](https://github.com/briandconnelly/BEACONToolkit/raw/master/analysis/doc/figures/sampling_means.png)

We know that if we sample over and over again and calculate the mean, it will
approximate a normal distribution given enough samples. We also know that +/- 2
standard deviations of a normal distribution contain about 96% of the mass. So,
using these two facts, we can estimate our confidence intervals as +/- 2
standard deviations of the sampling distribution. This is where, having
resampled over and over again, the mean will end up about 95% of the time.

	c(mean(cold_effect) - 2 * sd(sample_means), mean(cold_effect) + 2 * sd(sample_means))
	[1] 0.7933669 3.7101643
	
We can compare these bootstrapped confidence intervals to those of a t-test.

	t.test(cold_effect)
	
	#output
	95 percent confidence interval:
	 0.7786423 3.7248889

## Analysis in R

Now that we have gone over a little bit about what statistics is (and what it
isn't), we can go through a few of the traditional analysis methods using R.
For this exercise, there is real data form a few runs of Avida studying
host-parasite coevolution in `BEACONToolkit/analysis/data/parasite_data.csv`.
This data set has the diversity of the final host population using Shannon
Diversity, which balances even distributions of abundance as well as species
richness, measured at the end of runs with varying levels of parasite
virulence. Here virulence just means the percentage of CPU cycles, or energy,
the parasites steal from their hosts. 

We will go into more detail on plotting tools with R and Python in future
tutorials, but it is always useful to look at your data. This includes using
the `summary`, `head`, and `tail` functions as mentioned before, but also with
plots. Just to get a sense of each level of virulence, we can plot these as
factors as opposed to the continuous variable they really are.

	plot(ShannonDiversity ~ as.factor(Virulence), data=parasite_data)

![Diversity by Virulence Treatment](https://github.com/briandconnelly/BEACONToolkit/raw/master/analysis/doc/figures/diversity_vs_virulence.png)

My typical runs are done with virulence set to 0.8, so lets focus on that set
of data.

	normal_parasites <-  parasite_data[na.omit(parasite_data$Virulence == 0.8), ]
	
We use `na.omit` because there are some Virulence values that are NA, or not
present in the data set. These are runs that do not have parasites, and we
should hold on to those too as a control.

	no_parasites <- parasite_data[is.na(parasite_data$Virulence), ]

We can make a box plot of just these two distributions to get a sense of how
parasites affect host diversity with parasites at 0.8 virulence.

	boxplot(no_parasites$ShannonDiversity, normal_parasites$ShannonDiversity, ylab="Shannon Diversity", xlab="W and W.O. Parasites", main="Normal Parasite Runs (0.8 Virulence)")
	
![Diversity With and Without Parasites](https://github.com/briandconnelly/BEACONToolkit/raw/master/analysis/doc/figures/normal_parasites.png)

It is pretty obvious from just looking at the data that parasites have a large
effect on host diversity, but we can start to quantify this difference using
some of R's built-in functions. 

	mean(normal_parasites$ShannonDiversity)
	[1] 1.269134
	
	mean(no_parasites$ShannonDiversity)
	[1] 0.2519426
	
Well, those are pretty different! But, means doesn't tell us about the
variation in our distributions. The variance and standard deviation are two
common measures of spread that have built in functions in R. 

	var(normal_parasites$ShannonDiversity)
	[1] 0.6110384

	sqrt(var(normal_parasites$ShannonDiversity))
	[1] 0.7816895
	
	#or just sd()
	sd(normal_parasites$ShannonDiversity)
	[1] 0.7816895
	
This tells us about the variation in our observed data but not the sample
distribution, which is what we care about. We want to know if we repeated this
experiment over and over again, what would the variation in our observed mean
be. We can get at this using the standard error of the mean or SEM, which is
estimating the variation in the sampling distribution. Unfortunately there is
no built-in R function for this, but it is relatively simple to compute.

	sem <- function(values) {sd(values)/sqrt(length(values))}
	sem(normal_parasites$ShannonDiversity)
	[1] 0.1105476
	
A very useful measure of our uncertainty in the estimated mean is the 95%
confidence interval. These are roughly 2*SEMs above and below the mean, but the
exact number of SEMs can be calculated using the t-distribution quantiles. Here
we want the middle 95% of the values, so we want to know where the extreme 5%
of the data falls, but split between extreme low and extreme high values (i.e.,
the lower 0.025 and upper 0.975 quantiles). 

	qt(c(0.025, 0.975), df=length(normal_parasites$ShannonDiversity))
	[1] -2.008559  2.008559
	
In this case, it is slightly more than 2 SEMs. In general, with more than 20 or
so samples, 2 is a good approximation for the 95% confidence intervals. Now we
can calculate what our 95% confidence intervals are for the mean host diversity
of typical parasite runs.

	c( mean(normal_parasites$ShannonDiversity) -2.008559*sem(normal_parasites$ShannonDiversity),  
	   mean(normal_parasites$ShannonDiversity) + 2.008559*sem(normal_parasites$ShannonDiversity))
	[1] 1.047092 1.491175
	
We could also use the `t.test` function to compute the 95% confidence intervals
for us.

	t.test(normal_parasites$ShannonDiversity, conf.int=T)
	
	#output ignoring the rest, since it isn't relevant in this case
	95 percent confidence interval:
	 1.046980 1.491288
	 
The `t.test` function also returned a p-value, but for the null hypothesis that
the true mean of this distribution is zero. While this may have some biological
meaning, we have a control that we really want to test against. The `t.test`
function can also perform a two-sample t-test and compare the means of two
distributions. 


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
	
This time the p-value is telling us the probability of observing as extreme a
difference between distributions given the null hypothesis that they have the
same mean, and it is very very small. But, as we argued earlier, the more
important measure is the actual difference between treatments rather than the
p-value. In this case, the means are quite different: 1.26 as compared to 0.25.
Conveniently, the 95% confidence intervals that are returned from a two-sample
t-test is giving us information about the uncertainty in the estimated
difference between distributions. We can see the difference is pretty
substantial in this case. 

Now, if you remember back to the box plot of diversities from runs without
parasites, it didn't look very normally distributed. The median and lower
quartile were squashed together close to zero. The t-test is parametric and
makes the assumption that our data is normally distributed. While it is fairly
robust to violations of that assumption, there are non-parametric tests
designed to deal with data like these. In particular, the Wilcox Rank-Sum test,
also known as the Mann-Whitney U Test, is a general non-parametric statistic. 

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

In this case, using a non-parametric test actually gave us more extreme values
for our differences in means! 

## Statistical Analysis in Python

In this section, we introduce a few useful methods for analyzing your data in Python.
Namely, we cover how to compute the mean, variance, and standard error of a data set.
For more advanced statistical analysis, we cover how to perform a
Mann-Whitney-Wilcoxon (MWW) RankSum test, how to perform an Analysis of variance (ANOVA)
between multiple data sets, and how to compute bootstrapped 95% confidence intervals for
non-normally distributed data sets.

### Python's SciPy Module

The majority of data analysis in Python can be performed with the SciPy module. SciPy
provides a plethora of statistical functions and tests that will handle the majority of
your analytical needs. If we don't cover a statistical function or test that you require
for your research, SciPy's full statistical library is described in detail at:
http://docs.scipy.org/doc/scipy/reference/tutorial/stats.html

### Python's pandas Module

The pandas module provides powerful, efficient, R-like DataFrame objects capable of
calculating statistics en masse on the entire DataFrame. DataFrames are useful for when
you need to compute statistics over multiple replicate runs.

For the purposes of this tutorial, we will use Luis' parasite data set:

	from pandas import *
	
	# must specify that blank space " " is NaN
	experimentDF = read_csv("parasite_data.csv", na_values=[" "])
	
	print experimentDF
	
	<class 'pandas.core.frame.DataFrame'>
	Int64Index: 350 entries, 0 to 349
	Data columns:
	Virulence           300  non-null values
	Replicate           350  non-null values
	ShannonDiversity    350  non-null values
	dtypes: float64(2), int64(1)

### Accessing data in pandas DataFrames

You can directly access any column and row by indexing the DataFrame.

	# show all entries in the Virulence column
	print experimentDF["Virulence"]
	
	0     0.5
	1     0.5
	2     0.5
	3     0.5
	4     0.5
	5     0.5
	6     0.5
	7     0.5
	8     0.5
	9     0.5
	10    0.5
	11    0.5
	12    0.5
	13    0.5
	14    0.5
	...
	335   NaN
	336   NaN
	337   NaN
	338   NaN
	339   NaN
	340   NaN
	341   NaN
	342   NaN
	343   NaN
	344   NaN
	345   NaN
	346   NaN
	347   NaN
	348   NaN
	349   NaN
	Name: Virulence, Length: 350
	
	# show the 12th row in the ShannonDiversity column
	print experimentDF["ShannonDiversity"][12]
	
	1.58981
	
You can also access all of the values in a column meeting a certain criteria.

	# show all entries in the ShannonDiversity column > 2.0
	print experimentDF[experimentDF["ShannonDiversity"] > 2.0]
	
	     Virulence  Replicate  ShannonDiversity
	8          0.5          9           2.04768
	89         0.6         40           2.01066
	92         0.6         43           2.90081
	96         0.6         47           2.02915
	105        0.7          6           2.23427
	117        0.7         18           2.14296
	127        0.7         28           2.23599
	129        0.7         30           2.48422
	133        0.7         34           2.18506
	134        0.7         35           2.42177
	139        0.7         40           2.25737
	142        0.7         43           2.07258
	148        0.7         49           2.38326
	151        0.8          2           2.07970
	153        0.8          4           2.38474
	163        0.8         14           2.03252
	165        0.8         16           2.38415
	170        0.8         21           2.02297
	172        0.8         23           2.13882
	173        0.8         24           2.53339
	182        0.8         33           2.17865
	196        0.8         47           2.07718
	208        0.9          9           2.12240
	209        0.9         10           2.46144
	212        0.9         13           2.20476
	229        0.9         30           2.28026
	235        0.9         36           2.19565
	237        0.9         38           2.16535
	243        0.9         44           2.17578
	251        1.0          2           2.16044

### Blank/omitted data (NA or NaN) in pandas DataFrames

Blank/omitted data is a piece of cake to handle in pandas. Here's an example data
set with NA/NaN values.

	print experimentDF[isnan(experimentDF["Virulence"])]
	
		 Virulence  Replicate  ShannonDiversity
	300        NaN          1          0.000000
	301        NaN          2          0.000000
	302        NaN          3          0.833645
	303        NaN          4          0.000000
	304        NaN          5          0.990309
	305        NaN          6          0.000000
	306        NaN          7          0.000000
	307        NaN          8          0.000000
	308        NaN          9          0.061414
	309        NaN         10          0.316439
	310        NaN         11          0.904773
	311        NaN         12          0.884122
	312        NaN         13          0.000000
	313        NaN         14          0.000000
	314        NaN         15          0.000000
	315        NaN         16          0.000000
	316        NaN         17          0.013495
	317        NaN         18          0.882519
	318        NaN         19          0.000000
	319        NaN         20          0.986830
	320        NaN         21          0.000000
	321        NaN         22          0.000000
	322        NaN         23          0.000000
	323        NaN         24          0.000000
	324        NaN         25          0.000000
	325        NaN         26          0.000000
	326        NaN         27          1.702720
	327        NaN         28          0.169556
	328        NaN         29          0.949750
	329        NaN         30          0.240084
	330        NaN         31          0.925913
	331        NaN         32          0.000000
	332        NaN         33          0.693356
	333        NaN         34          0.000000
	334        NaN         35          0.310170
	335        NaN         36          0.000000
	336        NaN         37          0.000000
	337        NaN         38          0.000000
	338        NaN         39          0.000000
	339        NaN         40          0.000000
	340        NaN         41          0.000000
	341        NaN         42          0.000000
	342        NaN         43          0.000000
	343        NaN         44          0.000000
	344        NaN         45          0.391061
	345        NaN         46          0.001669
	346        NaN         47          0.000000
	347        NaN         48          0.444463
	348        NaN         49          0.383512
	349        NaN         50          0.511329
	
DataFrame methods automatically ignore NA/NaN values.

	print "Mean virulence across all treatments:", experimentDF["Virulence"].mean()
	
	Mean virulence across all treatments: 0.75

However, not all methods in Python are guaranteed to handle NA/NaN values properly.

	from scipy import stats

	print "Mean virulence across all treatments:", stats.sem(experimentDF["Virulence"])
	
	Mean virulence across all treatments: nan

Thus, it behooves you to take care of the NA/NaN values before performing your analysis.
You can either:

**(1) filter out all of the entries with NA/NaN**

	# NOTE: this drops the entire row if any of its entries are NA/NaN!
	print experimentDF.dropna()
	
	<class 'pandas.core.frame.DataFrame'>
	Int64Index: 300 entries, 0 to 299
	Data columns:
	Virulence           300  non-null values
	Replicate           300  non-null values
	ShannonDiversity    300  non-null values
	dtypes: float64(2), int64(1)
	
If you only care about NA/NaN values in a specific column, you can specify the
column name first.

	print experimentDF["Virulence"].dropna()
	
	0     0.5
	1     0.5
	2     0.5
	3     0.5
	4     0.5
	5     0.5
	6     0.5
	7     0.5
	8     0.5
	9     0.5
	10    0.5
	11    0.5
	12    0.5
	13    0.5
	14    0.5
	...
	285    1
	286    1
	287    1
	288    1
	289    1
	290    1
	291    1
	292    1
	293    1
	294    1
	295    1
	296    1
	297    1
	298    1
	299    1
	Name: Virulence, Length: 300
	
**(2) replace all of the NA/NaN entries with a valid value**

	print experimentDF.fillna(0.0)["Virulence"]
	
	0     0.5
	1     0.5
	2     0.5
	3     0.5
	4     0.5
	5     0.5
	6     0.5
	7     0.5
	8     0.5
	9     0.5
	10    0.5
	11    0.5
	12    0.5
	13    0.5
	14    0.5
	...
	335    0
	336    0
	337    0
	338    0
	339    0
	340    0
	341    0
	342    0
	343    0
	344    0
	345    0
	346    0
	347    0
	348    0
	349    0
	Name: Virulence, Length: 350
	
Take care when deciding what to do with NA/NaN entries. It can have a significant
impact on your results!

	print "Mean virulence across all treatments w/ dropped NaN:", experimentDF["Virulence"].dropna().mean()
	
	print "Mean virulence across all treatments w/ filled NaN:", experimentDF.fillna(0.0)["Virulence"].mean()
	
	Mean virulence across all treatments w/ dropped NaN: 0.75
	Mean virulence across all treatments w/ filled NaN: 0.642857142857
	
### Mean

The mean performance of an experiment gives a good idea of how the experiment will
turn out *on average* under a given treatment.

Conveniently, DataFrames have all kinds of built-in functions to perform standard
operations on them en masse: `add()`, `sub()`, `mul()`, `div()`, `mean()`, `std()`, etc.
The full list is located at: http://pandas.sourceforge.net/generated/pandas.DataFrame.html

Thus, computing the mean of a DataFrame only takes one line of code:

	from pandas import *
	
	print "Mean Shannon Diversity w/ 0.8 Parasite Virulence =", experimentDF[experimentDF["Virulence"] == 0.8]["ShannonDiversity"].mean()
	
	Mean Shannon Diversity w/ 0.8 Parasite Virulence = 1.2691338188
	
### Variance

The variance in the performance provides a measurement of how consistent the results
of an experiment are. The lower the variance, the more consistent the results are, and
vice versa.

Computing the variance is also built in to pandas DataFrames:

	from pandas import *
	
	print "Variance in Shannon Diversity w/ 0.8 Parasite Virulence =", experimentDF[experimentDF["Virulence"] == 0.8]["ShannonDiversity"].var()
	
	Variance in Shannon Diversity w/ 0.8 Parasite Virulence = 0.611038433313
	
### Standard Error of the Mean (SEM)

Combined with the mean, the SEM enables you to establish a range around a mean that
the majority of any future replicate experiments will most likely fall within.

pandas DataFrames don't have methods like SEM built in, but since DataFrame
rows/columns are treated as lists, you can use any NumPy/SciPy method you like on them.

	from pandas import *
	from scipy import stats
	
	print "SEM of Shannon Diversity w/ 0.8 Parasite Virulence =", stats.sem(experimentDF[experimentDF["Virulence"] == 0.8]["ShannonDiversity"])
	
	SEM of Shannon Diversity w/ 0.8 Parasite Virulence = 0.110547585529
	
A single SEM will usually envelop 68% of the possible replicate means
and two SEMs envelop 95% of the possible replicate means. Two
SEMs are called the "estimated 95% confidence interval." The confidence
interval is estimated because the exact width depend on how many replicates
you have; this approximation is good when you have more than 20 replicates.

### Mann-Whitney-Wilcoxon (MWW) RankSum test

The MWW RankSum test is a useful test to determine if two distributions are significantly
different or not. Unlike the t-test, the RankSum test does not assume that the data
are normally distributed, potentially providing a more accurate assessment of the data sets.

As an example, let's say we want to determine if the results of the two following
treatments significantly differ or not:

	# select two treatment data sets from the parasite data
	treatment1 = experimentDF[experimentDF["Virulence"] == 0.5]["ShannonDiversity"]
	treatment2 = experimentDF[experimentDF["Virulence"] == 0.8]["ShannonDiversity"]
	
	print "Data set 1:\n", treatment1
	print "Data set 2:\n", treatment2
	
	Data set 1:
	0     0.059262
	1     1.093600
	2     1.139390
	3     0.547651
	4     0.065928
	5     1.344330
	6     1.680480
	7     0.000000
	8     2.047680
	9     0.000000
	10    1.507140
	11    0.000000
	12    1.589810
	13    1.144800
	14    1.011190
	15    0.000000
	16    0.776665
	17    0.001749
	18    1.761200
	19    0.021091
	20    0.790915
	21    0.000000
	22    0.018867
	23    0.994268
	24    1.729620
	25    0.967537
	26    0.457318
	27    0.992525
	28    1.506640
	29    0.697241
	30    1.790580
	31    1.787710
	32    0.857742
	33    0.000000
	34    0.445267
	35    0.045471
	36    0.003490
	37    0.000000
	38    0.115830
	39    0.980076
	40    0.000000
	41    0.820405
	42    0.124755
	43    0.719755
	44    0.584252
	45    1.937930
	46    1.284150
	47    1.651680
	48    0.000000
	49    0.000000
	Name: ShannonDiversity
	Data set 2:
	150    1.433800
	151    2.079700
	152    0.892139
	153    2.384740
	154    0.006980
	155    1.971760
	156    0.000000
	157    1.428470
	158    1.715950
	159    0.000000
	160    0.421927
	161    1.179920
	162    0.932470
	163    2.032520
	164    0.960912
	165    2.384150
	166    1.879130
	167    1.238890
	168    1.584300
	169    1.118490
	170    2.022970
	171    0.000000
	172    2.138820
	173    2.533390
	174    1.212340
	175    0.059135
	176    1.578260
	177    1.725210
	178    0.293153
	179    0.000000
	180    0.000000
	181    1.699600
	182    2.178650
	183    1.792580
	184    1.920800
	185    0.000000
	186    1.583250
	187    0.343235
	188    1.980010
	189    0.980876
	190    1.089380
	191    0.979254
	192    1.190450
	193    1.738880
	194    1.154100
	195    1.981610
	196    2.077180
	197    1.566410
	198    0.000000
	199    1.990900
	Name: ShannonDiversity
	
A RankSum test will provide a P value indicating whether or not the two
distributions are the same.

	from scipy import stats
	
	z_stat, p_val = stats.ranksums(treatment1, treatment2)
	
	print "MWW RankSum P for treatments 1 and 2 =", p_val
	
	MWW RankSum P for treatments 1 and 2 = 0.000983355902735
	
If P <= 0.05, we are highly confident that the distributions significantly differ, and
can claim that the treatments had a significant impact on the measured value.

If the treatments do *not* significantly differ, we could expect a result such as
the following:

	treatment3 = experimentDF[experimentDF["Virulence"] == 0.8]["ShannonDiversity"]
	treatment4 = experimentDF[experimentDF["Virulence"] == 0.9]["ShannonDiversity"]
	
	print "Data set 3:\n", treatment3
	print "Data set 4:\n", treatment4
	
	Data set 3:
	150    1.433800
	151    2.079700
	152    0.892139
	153    2.384740
	154    0.006980
	155    1.971760
	156    0.000000
	157    1.428470
	158    1.715950
	159    0.000000
	160    0.421927
	161    1.179920
	162    0.932470
	163    2.032520
	164    0.960912
	165    2.384150
	166    1.879130
	167    1.238890
	168    1.584300
	169    1.118490
	170    2.022970
	171    0.000000
	172    2.138820
	173    2.533390
	174    1.212340
	175    0.059135
	176    1.578260
	177    1.725210
	178    0.293153
	179    0.000000
	180    0.000000
	181    1.699600
	182    2.178650
	183    1.792580
	184    1.920800
	185    0.000000
	186    1.583250
	187    0.343235
	188    1.980010
	189    0.980876
	190    1.089380
	191    0.979254
	192    1.190450
	193    1.738880
	194    1.154100
	195    1.981610
	196    2.077180
	197    1.566410
	198    0.000000
	199    1.990900
	Name: ShannonDiversity
	Data set 4:
	200    1.036930
	201    0.938018
	202    0.995956
	203    1.006970
	204    0.968258
	205    0.000000
	206    0.416046
	207    1.570310
	208    2.122400
	209    2.461440
	210    0.969003
	211    0.000000
	212    2.204760
	213    0.999556
	214    1.820140
	215    1.581250
	216    1.950260
	217    1.633000
	218    1.854850
	219    0.159017
	220    0.997556
	221    1.935620
	222    1.814500
	223    0.999802
	224    0.000000
	225    0.186966
	226    1.569840
	227    1.660550
	228    0.998564
	229    2.280260
	230    1.560220
	231    0.992335
	232    1.557250
	233    1.536150
	234    1.584580
	235    2.195650
	236    1.327320
	237    2.165350
	238    1.711200
	239    1.885540
	240    0.960891
	241    0.958280
	242    0.990460
	243    2.175780
	244    0.890169
	245    1.922790
	246    1.564330
	247    1.870380
	248    1.262280
	249    0.000000
	Name: ShannonDiversity
	
	# compute RankSum P value
	z_stat, p_val = stats.ranksums(treatment3, treatment4)

	print "MWW RankSum P for treatments 3 and 4 =", p_val
	
	MWW RankSum P for treatments 3 and 4 = 0.994499571124
	
With P > 0.05, we must say that the distributions do not significantly differ.
Thus changing the parasite virulence between 0.8 and 0.9 does not result in a
significant change in Shannon Diversity.

### One-way analysis of variance (ANOVA)

If you need to compare more than two data sets at a time, an ANOVA is your best bet. For
example, we have the results from three experiments with overlapping 95% confidence
intervals, and we want to confirm that the results for all three experiments are not
significantly different.

	treatment1 = experimentDF[experimentDF["Virulence"] == 0.7]["ShannonDiversity"]
	treatment2 = experimentDF[experimentDF["Virulence"] == 0.8]["ShannonDiversity"]
	treatment3 = experimentDF[experimentDF["Virulence"] == 0.9]["ShannonDiversity"]
	
	print "Data set 1:\n", treatment1
	print "Data set 2:\n", treatment2
	print "Data set 3:\n", treatment3
	
	Data set 1:
	100    1.595440
	101    1.419730
	102    0.000000
	103    0.000000
	104    0.787591
	105    2.234270
	106    1.700440
	107    0.954747
	108    1.127320
	109    1.761330
	110    0.000000
	111    0.374074
	112    1.836250
	113    1.583900
	114    0.998377
	115    0.341714
	116    0.892717
	117    2.142960
	118    1.824870
	119    0.999703
	120    0.957757
	121    1.152910
	122    0.597295
	123    1.959020
	124    0.764003
	125    0.614147
	126    0.617618
	127    2.235990
	128    0.000000
	129    2.484220
	130    0.008294
	131    1.003480
	132    1.292820
	133    2.185060
	134    2.421770
	135    0.713224
	136    0.551367
	137    0.006377
	138    0.948393
	139    2.257370
	140    1.394850
	141    0.547157
	142    2.072580
	143    1.323440
	144    1.001340
	145    1.042600
	146    0.000000
	147    1.139100
	148    2.383260
	149    0.056819
	Name: ShannonDiversity
	Data set 2:
	150    1.433800
	151    2.079700
	152    0.892139
	153    2.384740
	154    0.006980
	155    1.971760
	156    0.000000
	157    1.428470
	158    1.715950
	159    0.000000
	160    0.421927
	161    1.179920
	162    0.932470
	163    2.032520
	164    0.960912
	165    2.384150
	166    1.879130
	167    1.238890
	168    1.584300
	169    1.118490
	170    2.022970
	171    0.000000
	172    2.138820
	173    2.533390
	174    1.212340
	175    0.059135
	176    1.578260
	177    1.725210
	178    0.293153
	179    0.000000
	180    0.000000
	181    1.699600
	182    2.178650
	183    1.792580
	184    1.920800
	185    0.000000
	186    1.583250
	187    0.343235
	188    1.980010
	189    0.980876
	190    1.089380
	191    0.979254
	192    1.190450
	193    1.738880
	194    1.154100
	195    1.981610
	196    2.077180
	197    1.566410
	198    0.000000
	199    1.990900
	Name: ShannonDiversity
	Data set 3:
	200    1.036930
	201    0.938018
	202    0.995956
	203    1.006970
	204    0.968258
	205    0.000000
	206    0.416046
	207    1.570310
	208    2.122400
	209    2.461440
	210    0.969003
	211    0.000000
	212    2.204760
	213    0.999556
	214    1.820140
	215    1.581250
	216    1.950260
	217    1.633000
	218    1.854850
	219    0.159017
	220    0.997556
	221    1.935620
	222    1.814500
	223    0.999802
	224    0.000000
	225    0.186966
	226    1.569840
	227    1.660550
	228    0.998564
	229    2.280260
	230    1.560220
	231    0.992335
	232    1.557250
	233    1.536150
	234    1.584580
	235    2.195650
	236    1.327320
	237    2.165350
	238    1.711200
	239    1.885540
	240    0.960891
	241    0.958280
	242    0.990460
	243    2.175780
	244    0.890169
	245    1.922790
	246    1.564330
	247    1.870380
	248    1.262280
	249    0.000000
	Name: ShannonDiversity

	# compute one-way ANOVA P value	
	from scipy import stats
		
	f_val, p_val = stats.f_oneway(treatment1, treatment2, treatment3)
	
	print "One-way ANOVA P =", p_val
	
	One-way ANOVA P = 0.381509481874
	
If P > 0.05, we can claim with high confidence that the means of the results of all three
experiments are not significantly different.

### Bootstrapped 95% confidence intervals

Oftentimes in wet lab research, it's difficult to perform the 20 replicate runs
recommended for computing reliable confidence intervals with SEM.

In this case, bootstrapping the confidence intervals is a much more accurate method of
determining the 95% confidence interval around your experiment's mean performance.

Unfortunately, SciPy doesn't have bootstrapping built into its standard library yet.
However, we have a pre-built bootstrapping function below:

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

	treatment1 = experimentDF[experimentDF["Virulence"] == 0.8]["ShannonDiversity"][:10]
	
	print "Small data set:\n", treatment1
	
	Small data set:
	150    1.433800
	151    2.079700
	152    0.892139
	153    2.384740
	154    0.006980
	155    1.971760
	156    0.000000
	157    1.428470
	158    1.715950
	159    0.000000
	Name: ShannonDiversity
	
	# compute 95% confidence intervals around the mean
	CIs = ci(data=treatment1, statfun=scipy.mean)

	print "Bootstrapped 95% confidence intervals\nLow:", CIs[0], "\nHigh:", CIs[1]
	
	Bootstrapped 95% confidence intervals
	Low: 0.659028048 
	High: 1.722468024
	
Note that you can change the range of the confidence interval by setting the alpha:

	# 80% confidence interval
	CIs = ci(treatment1, scipy.mean, alpha=0.2)
	print "Bootstrapped 80% confidence interval\nLow:", CIs[0], "\nHigh:", CIs[1]
	
	Bootstrapped 80% confidence interval
	Low: 0.827291024 
	High: 1.5420059

And also modify the size of the bootstrapped sample pool that the confidence intervals
are taken from:

	# bootstrap 20,000 samples instead of only 10,000
	CIs = ci(treatment1, scipy.mean, n_samples=20000)
	print "Bootstrapped 95% confidence interval w/ 20,000 samples\nLow:", CIs[0], "\nHigh:", CIs[1]
	
	Bootstrapped 95% confidence interval w/ 20,000 samples
	Low: 0.644756972 
	High: 1.7071459
	
Generally, bootstrapped 95% confidence intervals provide more accurate confidence
intervals than 95% confidence intervals estimated from the SEM.