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
bootstrapping and sometimes more generally resampling. 

![New Fake Distribution](https://github.com/briandconnelly/BEACONToolkit/raw/master/analysis/doc/figures/fake_hist.png)

	cold_effects = rnorm(50, mean=1.0, sd=5)
	
Let's say this is the measured effect of cold temperature on body weight in some 
other species of fish. We want to know if there is really a trend of colder
temperatures and heavier fish. We can think about testing this by asking how
often we would see as extreme a mean if the true mean was zero. This would
require us to specify the distribution, and would be called a parametric 
Monte Carlo test. In this case we know this data came from a normal distribution, so we could perform this test by looking at means from a set of random numbers drawn from this null distribution (with mean=0) and estimate the probability of observing a mean as extreme as the one we actually observed in `cold_effects`. 
	
	#first define how many samples we'll be doing -- the more the better
	num_samples <- 100000

	#generate a sample mean distribution under the null hypothesis
	monte_carlo_samples <- replicate(num_samples, mean(rnorm(length(cold_effect), mean=0, sd=sd(cold_effect))))
	
	#we can look at it
	hist(monte_carlo_samples, main="Monte Carlo Simulated Means")

	p_val <- length(monte_carlo_samples[monte_carlo_samples>= mean(cold_effect)])/length(monte_carlo_samples)
	print(paste("p-value = ", p_val))
	
	#output
	[1] "p-value =  0.00105"
	
![Monte Carlo](https://github.com/briandconnelly/BEACONToolkit/raw/master/analysis/doc/figures/monte_carlo.png)
	
We can compare our simulated p-value to the t-test closed form solution and see they are quite similar. 

	#compare this to the t-test p-value
	t.test(cold_effect, alternative="greater")
	
	#output
	t = 3.0718, df = 49, p-value = 0.001734


### What 95% confidence intervals are

There is a lot of confusion about what 95% confidence intervals are. The most common interpretation is that they are where you expect the true mean to fall 95% of the time. Unfortunately, this is not exactly what they are. Instead, they tell you where your estimated mean will fall 95% of the time, if you were to replicate your experiment over and over again. Here we will quickly show you what this means, and how to bootstrap 95% confidence intervals for yourself. 

Lets say we have a distribution, here `cold_effects` will serve as our data. The 95% confidence interval tells us if we were to go back out to the ocean and sample fish again thousands and thousands of times, where the mass of our estimated means would fall. We can think about this process as sampling from the underlying distribution over and over again, and while we don't have the underlying distribution, we do have an empirical one. With bootstrapping and resampling techniques in general, we treat our empirical distribution as the underlying distribution and sample repeatedly from it. 

Just to illustrate a bit of the variation we get when resampling from our data
over and over again, here are a few box plots of individual resamplings. We can
perform a single resampling event by calling the `sample` function, specifying
we want to sample with replacement by setting `replace=T`:

	sample(cold_effects, size=length(a), replace=T)

![Resampled Distributions](https://github.com/briandconnelly/BEACONToolkit/raw/master/analysis/doc/figures/resamples.png)

And if we calculate the mean of these resampled distributions many many times, 
we get what is known as the sampling distribution of means. We can repeat this 
sampling process using the `replicate` function, here replicating it 100,000
times.

	sample_means <- replicate(100000, mean(sample(cold_effects, size=length(cold_effects), replace=T)))
	
![Sample Mean Distribution](https://github.com/briandconnelly/BEACONToolkit/raw/master/analysis/doc/figures/sampling_means.png)

We know that if we sample over and over again and calculate the mean, it will approximate a normal distribution given enough samples. We also know that +/- 2 standard deviations of a normal distribution contain about 96% of the mass. So, using these two facts, we can estimate our confidence intervals as +/- 2 standard deviations of the sampling distribution. This is where, having resampled over and over again, the mean will end up about 95% of the time.

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

We can make a box plot of just these two distributions to get a sense of how parasites affect host diversity with parasites at 0.8 virulence.

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

Now, if you remember back to the box plot of diversities from runs without parasites, it didn't look very normally distributed. The median and lower quartile were squashed together close to zero. The t-test is parametric and makes the assumption that our data is normally distributed. While it is fairly robust to violations of that assumption, there are non-parametric tests designed to deal with data like these. In particular, the Wilcox Rank-Sum test, also known as the Mann-Whitney U Test, is a general non-parametric statistic. 

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
between multiple distributions, and how to compute bootstrapped 95% confidence intervals for
non-normally distributed data.

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
	
	print dataset_list
	
> [ 29.31616689  17.84990351  18.29067038  22.88000839  11.40115392
>   16.25772419  15.06432056   9.95443695  14.96259294  20.85094509
>   13.48477627  20.03862034  22.71966826  26.49146294  26.41032275
>   16.87420833  26.74874152  15.24608994  20.19901887  25.9643908
>   13.06743069  22.83800346  30.86368     17.37685739  16.56721256
>   22.23323283  26.31665391  23.87633505  19.18316128  28.03331025]

### Mean

The mean performance of an experiment gives a good idea of how the experiment will
turn out *on average* under a given treatment.

	import scipy

	dataset_mean = scipy.mean(dataset_list)
	
	print "Dataset mean:", dataset_mean
	
> Dataset mean: 20.378703342

### Variance

The variance in the performance provides a measurement of how consistent the results
of an experiment are. The lower the variance, the more consistent the results are, and
vice versa.

	import scipy
	
	dataset_variance = scipy.var(dataset_list)
	
	print "Variance around the mean:", dataset_variance
	
> Variance around the mean: 30.0722365196

### Standard Error of the Mean (S.E.M.)

Combined with the mean, the S.E.M. enables you to establish a range around a mean that
the majority of any future replicate experiments will most likely fall within.

	from scipy import stats

	dataset_stderr = 1.96 * stats.sem(dataset_list)
	
	print "Standard error of the mean:", dataset_stderr
	
> Standard error of the mean: 1.99590532404

A single S.E.M. will usually envelop 68% of the possible replicate means
and two S.E.M.s envelop 95% of the possible replicate means. Two
S.E.M.s are called the "estimated 95% confidence interval." The confidence
interval is estimated because the exact width depend on how many replicates
you have; this approximation is good when you have more than 20 replicates.

### Mann-Whitney-Wilcoxon (MWW) RankSum test

The MWW RankSum test is a useful test to determine if two distributions are significantly
different or not. Unlike the t-test, the RankSum test does not assume that the data
are normally distributed, potentially providing a more accurate assessment of the datasets.

As an example, let's say we want to determine if the results of the two following
experiments significantly differ or not:

	import numpy as np
	
	# create random set of numbers between 0 and 10
	experiment1 = np.random.rand(1, 50) * 10
	experiment2 = np.random.rand(1, 50) * 10
	
	print experiment1
	print experiment2
	
> [[ 0.60703811  2.02903267  7.77922897  0.72135786  7.60735994  2.55005731
>    3.75147232  9.92628774  5.84305081  8.70985479  6.24811885  1.90969196
>    9.10927591  3.01245551  9.06592429  9.56689585  4.48222746  7.44179666
>    6.24691287  2.23830165  4.35116166  2.84018573  0.08320698  4.36125059
>    1.4610135   5.86651043  1.89150441  6.24918774  6.57098487  4.29357824
>    1.5557837   9.63006435  0.71365672  7.11599719  4.02809286  7.65547018
>    8.82567936  0.54906886  8.55374451  2.57840604  3.20837339  5.73256059
>    5.7241952   9.35435413  9.35996839  7.01528296  4.66974079  6.09729923
>    4.84421278  9.62590103]]
   
> [[ 5.94954301  4.02512252  5.10857072  0.20204057  8.57127551  7.51061019
>    7.39677011  9.39687917  9.11026608  9.4898699   9.00727209  8.47904713
>    1.56610254  0.71595907  8.30823977  5.63675437  3.82638994  3.26857413
>    4.81009474  5.15329638  0.78554851  8.05647441  4.42453386  7.16148733
>    5.37506635  6.07097425  1.18304531  4.24637205  0.98300946  3.32876637
>    2.28266522  4.95443069  5.48805806  5.20826745  1.528031    8.50207874
>    9.69815007  7.36248269  2.17102453  7.15547992  8.51739963  0.85976576
>    7.43011228  8.14334652  1.03625833  5.92170905  8.47008621  8.40191409
>    2.95670326  1.66834695]]

A quick RankSum test will provide a P value indicating whether or not the two
distributions are the same.

	from scipy import stats
	
	z_stat, p_val = stats.ranksums(experiment1, experiment2)
	
	print "MWW RankSum P for experiments 1 and 2 =", p_val
	
> MWW RankSum P for experiments 1 and 2 = 5.73303143758e-07
	
If P <= 0.05, we are highly confident that the distributions significantly differ, and
can claim that the treatment has a significant impact on the measured value.

If the treatments do *not* significantly differ, we could expect a result such as the following:

	# create a set of normally-distributed numbers centered around the same mean
	experiment3 = np.random.normal(40, 8, 30)
	experiment4 = np.random.normal(40, 8, 30)
	
	print experiment3
	print experiment4
	
> [ 57.9564105   37.97638507  40.65139054  55.43770779  49.52670648
>   39.17122622  48.87309287  31.08453766  47.93442482  48.22312111
>   51.93581354  58.72188138  39.82392081  37.0940381   37.61361859
>   50.62734137  44.41113408  10.27225975  43.62763019  29.33972703
>   44.71846967  38.80722083  44.86990128  36.50444083  41.35612323
>   48.47557548  46.86753584  34.36680173  41.29560205  42.72153454]

> [ 37.79410956  30.15902312  45.38095056  48.54958363  47.86142528
>   40.29446501  33.87154296  47.93095233  47.49276641  46.16960774
>   39.2747562   23.60764727  36.1324458   30.60504485  43.65414926
>   34.49818113  54.88851323  49.05865549  42.83492157  40.09497425
>   27.24463829  46.34087852  34.35112739  46.51584338  52.38865353
>   40.67349906  45.40321415  36.09856076  52.37654715  30.63914578]
	
	z_stat, p_val = stats.ranksums(experiment3, experiment4)
	
	print "MWW RankSum P for experiments 3 and 4 =", p_val
	
> MWW RankSum P for experiments 3 and 4 = 0.383055045846

With P > 0.05, we must say that the distributions do not significantly differ. Thus the
treatments in experiments 3 and 4 do not have a significant impact on the measured value.

### One-way analysis of variance (ANOVA)

If you need to compare more than two datasets at a time, an ANOVA is your best bet. For
example, we have the results from three experiments with overlapping 95% confidence
intervals, and we want to confirm that the results for all three experiments are not
significantly different.

	import numpy as np
	
	# generate 3 sets of normally distributed numbers
	experiment1 = np.random.normal(20, 3, 30)
	experiment2 = np.random.normal(18, 5, 30)
	experiment3 = np.random.normal(19, 7, 30)
	
	print experiment1
	print experiment2
	print experiment3

> [ 19.04378835  22.50421579  24.34944666  22.51816612  20.58749006
>   12.8445342   18.30013223  27.3257252   17.94535996  18.91757146
>   18.37062731  18.65238219  18.38667562  22.60495363  24.76745954
>   23.04309348  18.85710967  18.21680551  27.35845316  19.88643909
>   20.99802896  20.66157181  21.80630328  23.24209409  16.03063632
>   22.34485767  20.92888144  19.68930839  16.73974945  18.07995139]
> [ 27.81170323  10.94953741  16.9971959   15.61408967  15.45994329
>   18.65727731  21.58641937  15.52435895  11.2323641   20.92883425
>   23.79364776  15.72508182  25.26726475  21.97336108  14.85964094
>   16.72098642  13.01312028  16.41548278  16.46276207  20.45849468
>   15.48204606  21.02902367  23.97056686  24.01698211  16.95786928
>   21.32214887  15.14553344  16.77880364  19.99548804  18.45136648]
> [ 13.43821528  14.53030599  21.96858873  14.87958515   6.77025586
>   33.31744607   6.96561297  33.32049064  21.16775149  19.06799499
>   29.8830259    8.11961867  30.82037979  16.36569719  13.32181128
>   30.09211718  19.61686393  24.02101628  16.29424766  23.98372488
>   22.32620927   8.50589624  30.20030432  24.58815171  12.49966463
>   30.50019967  17.89961298  23.10544466  13.70368434  14.70896301]

	from scipy import stats
	
	f_val, p_val = stats.f_oneway(experiment1, experiment2, experiment3)
	
	print "One-way ANOVA P =", p_val
	
> One-way ANOVA P = 0.333441170471
	
If P > 0.05, we can claim with high confidence that the means of the results of all three
experiments are not significantly different.

### Bootstrapped 95% confidence intervals

Oftentimes in wet lab research, it's difficult to perform the 20 replicate runs
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
	
	experiment1 = np.random.normal(15, 3, 10)
	
	print experiment1

> [ 15.85892027  19.46669957  16.94655472  15.23605432  14.42308533
>   11.26638304  20.18231971  21.21970167  11.40363899  16.38765404]

	CIs = ci(data=experiment1, statfun=scipy.mean)
	
	print "Bootstrapped 95% confidence interval low:", CIs[0], ", high:", CIs[1]
	
> Bootstrapped 95% confidence interval low: 14.2865506829 , high: 18.2302554524
	
Note that you can change the range of the confidence interval by setting the alpha:

	# 80% confidence interval
	CIs = ci(experiment1, scipy.mean, alpha=0.2)
	print "Bootstrapped 80% confidence interval low:", CIs[0], ", high:", CIs[1]

> Bootstrapped 80% confidence interval low: 14.9653005047 , high: 17.5814853635

And also modify the size of the bootstrapped sample pool that the confidence intervals
are taken from:

	# bootstrap 20,000 samples instead of only 10,000
	CIs = ci(experiment1, scipy.mean, n_samples=20000)
	"Bootstrapped 95% confidence interval low:", CIs[0], ", high:", CIs[1]
	
> Bootstrapped 95% confidence interval low: 14.2447813408 , high: 18.2276982261
	
Generally, bootstrapped 95% confidence intervals provide more accurate confidence
intervals than 95% confidence intervals estimated from the S.E.M.

## Python's pandas Module

The pandas module provides powerful, efficient, R-like DataFrame objects capable of
calculating statistics en masse on the entire DataFrame. DataFrames are very useful
for when you need to compute statistics over multiple replicate runs.

For the purposes of this tutorial, `experimentList` and `experimentDF` shall be assigned
by the following Python code:

	import pandas
	import numpy as np
	
	experimentList = []
	
	for replicate in range(30):
		
		experimentList.append(pandas.DataFrame(np.random.rand(600, 10),
						columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']))
	
	experimentDF = (pandas.concat(experimentList, axis=1, keys=range(len(experimentList)))
			 .swaplevel(0, 1, axis=1)
			 .sortlevel(axis=1)
			 .groupby(level=0, axis=1))

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

### Accessing specific data columns

Data from specific columns of the DataFrame can be accessed by indexing the DataFrame
with the column name.

	print confidenceIntervalDF["C"]
	
> 0     0.114974
> 1     0.096842
> 2     0.107527
> 3     0.095829
> 4     0.103239
> 5     0.102268
> 6     0.098333
> 7     0.102555
> 8     0.104940
> 9     0.127890
> 10    0.119824
> 11    0.110450
> 12    0.108072
> 13    0.099324
> 14    0.102238
> ...
> 585    0.122916
> 586    0.105350
> 587    0.102912
> 588    0.089611
> 589    0.107591
> 590    0.089419
> 591    0.101189
> 592    0.108616
> 593    0.086157
> 594    0.096727
> 595    0.111009
> 596    0.109768
> 597    0.087983
> 598    0.101010
> 599    0.087999
> Name: C, Length: 600

### NumPy/SciPy methods on pandas DataFrames

Finally, NumPy and SciPy methods can be applied directly to pandas DataFrames with the
`aggregate()` function.

	import numpy as np
	from scipy import stats as st
	
	# mean
	meanDF = experimentDF.aggregate((lambda x: np.mean(x, axis=1)))
	
	# geometric mean
	geomeanDF = experimentDF.aggregate((lambda x: st.gmean(x, axis=1)))
	
	# standard error of the mean
	semDF = experimentDF.aggregate((lambda x: st.sem(x, axis=1)))
	
	# etc.