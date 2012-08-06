# BEACONToolkit Chapter 2: Analysis
# By: Luis Zaman 
# 8/6/12 

######## Fake fish data for what p-values aren't ########
cold_fish = rnorm(5000, mean=20.5, sd=5)
hot_fish = rnorm(5000, mean=20, sd=5)
data_frame <- data.frame(weight=c(hot_fish,cold_fish), environment=c(rep("hot", 5000), rep("cold", 5000)))
boxplot(weight ~ environment, data=data_frame, xlab="Environment", ylab="Weight (kg)", main="Fake Fish Data")
t.test(cold_fish,hot_fish)


######## Fake data for what p-values are ########
cold_effect = rnorm(50, mean=1.0, sd=5)
hist(cold_effect, main="Histogram of our data", xlab="Data")


######## Monte Carlo for P-Value ########
#now instead of just looking at them, lets see how many of them have means below 0
num_samples <- 100000


monte_carlo_samples <- replicate(num_samples, mean(rnorm(length(cold_effect), mean=0, sd=sd(cold_effect))))
hist(monte_carlo_samples, main="Monte Carlo Simulated Means")

p_val <- length(monte_carlo_samples[monte_carlo_samples>= mean(cold_effect)])/length(monte_carlo_samples)
print(paste("p-value = ", p_val))

#this performs a one tail t-test, assuming we expect the effect to be above 0 (our null hypothesis)
t.test(cold_effect, alternative="greater")



######## Bootstrap for 95% confidence intervals ########

#first get the sampling distribution of means
sample_means <- replicate(num_samples, mean(sample(cold_effect, size=length(cold_effect), replace=T)))
hist(sample_means, xlab="Means of Samples", main="Histogram of Resampled Means")


#sample with replacement the same number of times as the length of our dataset
#plot a few of these to show that you get variation based on the empirical distribution
boxplot(sample(cold_effect, size=length(cold_effect), replace=T),sample(cold_effect, size=length(cold_effect), replace=T),sample(cold_effect, size=length(cold_effect), replace=T),sample(cold_effect, size=length(cold_effect), replace=T),sample(cold_effect, size=length(cold_effect), replace=T),sample(cold_effect, size=length(cold_effect), replace=T),sample(cold_effect, size=length(cold_effect), replace=T),sample(cold_effect, size=length(cold_effect), replace=T), xlab="Resamples", main="Multipe Resampling")

#use sd of sample mean distribution to calculate 95% confidence intervals
c(mean(cold_effect) - 2 * sd(sample_means), mean(cold_effect) + 2 * sd(sample_means))

#compare this to the t-test confidence intervals
t.test(cold_effect)



######## Other Analysis in R ########
setwd("~/BEACONToolkit/analysis/data")
parasite_data <- read.csv("parasite_data.csv")

plot(ShannonDiversity ~ as.factor(Virulence), data=parasite_data)

no_parasites <- parasite_data[is.na(parasite_data$Virulence), ]
normal_parasites <-  parasite_data[na.omit(parasite_data$Virulence == 0.8), ]

boxplot(no_parasites$ShannonDiversity, normal_parasites$ShannonDiversity, ylab="Shannon Diversity", xlab="W and W.O. Parasites", main="Normal Parasite Runs (0.8 Virulence)")

mean(no_parasites$ShannonDiversity)
mean(normal_parasites$ShannonDiversity)

sem <- function(values) {sd(values)/sqrt(length(values))}
sem(normal_parasites$ShannonDiversity)

qt(c(0.025, 0.975), df=length(normal_parasites$ShannonDiversity))

c( mean(normal_parasites$ShannonDiversity) -2.008559*sem(normal_parasites$ShannonDiversity),  
   mean(normal_parasites$ShannonDiversity) + 2.008559*sem(normal_parasites$ShannonDiversity))

t.test(no_parasites$ShannonDiversity, normal_parasites$ShannonDiversity, conf.int=T)


wilcox.test(no_parasites$ShannonDiversity, normal_parasites$ShannonDiversity, conf.int=T)



