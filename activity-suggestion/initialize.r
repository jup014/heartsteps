rm(list = ls())
server = T
#' ---
#' title:  Initialize the bandit algorithm in HS 2.0
#' author: Peng Liao
#' date:   09.11, 2018
#' ---
#'  

library(rjson)


# ========  Recieve Input ========= ####

if(server){
  
  source("./banditcode/functions.R")
  args <- commandArgs(trailingOnly = TRUE)[1]
  input = fromJSON(args) # this is a list
  
}else{
  
  source("/Users/Peng/Dropbox/GitHubRepo/heartsteps/activity-suggestion/banditcode/functions.R")
  setwd("/Users/Peng/Dropbox/GitHubRepo/heartsteps/activity-suggestion/")
  input <- fromJSON(file = "./banditcode/start.json")
  
}


# convert NULL to NA and tranform into vector/matrix
names.array <- c("appClicksArray", "totalStepsArray")
names.matrix <- c("availMatrix", "preStepsMatrix", "postStepsMatrix")
for(name in names.array) input[[name]] <- proc.array(input[[name]])
for(name in names.matrix) input[[name]] <- proc.matrix(input[[name]])
  
# check if we have identical days' data for each variables
len.all <- NULL
for(name in names.array){
  
  len.all <- c(len.all, length(input[[name]]))
  
  
}
for(name in names.matrix){
  
  len.all <- c(len.all, nrow(input[[name]]))
  
  
}
stopifnot(all(diff(len.all) == 0))

# number of days before the study
ndays <- len.all[1]
stopifnot(ndays == 7)

# check if we have all five datas for the matrics
ncol.all <- NULL
for(name in names.matrix){
  
  ncol.all <- c(ncol.all, ncol(input[[name]]))
  
  
}
stopifnot(ncol.all == 5)

# ensure availability is logicial (no missing)
stopifnot(all(c(input$availMatrix) %in% c(0, 1)))

# need to ensure we have app clicks data 
stopifnot(all(is.na(input$appClicksArray)) == FALSE)

# need to ensure we have, for each dt, any pre/post steps data)
stopifnot(all(apply(input$preStepsMatrix, 2, function(x) sum(is.na(x))) < ndays))
stopifnot(all(apply(input$postStepsMatrix, 2, function(x) sum(is.na(x))) < ndays))



# ===  Initialize a Dataset for imputation and discretization === ####

## dataset used to handle future missing data and standarization
data.imputation <- list()
data.imputation$userID <- input$userID

# threshold to standarize the app click
data.imputation$thres.appclick <- mean(input$appClicksArray, na.rm=TRUE)

# applicks last 7 days (update daily)
data.imputation$appclicks <- tail(input$appClicksArray[is.na(input$appClicksArray)==FALSE], 7)

# total steps last 7 days (update daily)
data.imputation$totalsteps <- NA
if(all(is.na(input$totalStepsArray))==FALSE){
  
  data.imputation$totalsteps <- tail(input$totalStepsArray[is.na(input$totalStepsArray)==FALSE], 7)
  
}

# pre steps last 7 days per decision time (update daily)
data.imputation$presteps <- NULL
for(i in 1:5){
  
  temp <- input$preStepsMatrix[, i] 
  
  if(all(is.na(temp))){
    
    # checked already 
    data.imputation$presteps[[i]] <- NA
    
  }else{
    
    data.imputation$presteps[[i]] <- tail(temp[is.na(temp)==FALSE], 7)
    
  }
  
}

# post steps for last 7 days per decision time (update daily)
data.imputation$poststeps <- NULL
for(i in 1:5){
  
  temp <-input$postStepsMatrix[, i]
  
  if(all(is.na(temp))){
    
    # checked already
    data.imputation$poststeps[[i]] <- NA
    
  }else{
    
    data.imputation$poststeps[[i]] <- tail(temp[is.na(temp)==FALSE], 7)
    
  }
  
}

# ===== Initialize the Policy ====== ####
data.policy <- list()

# this will be used to select the action on the first day. 
# contains: posterior mean and variance, value function, pi_min and pi_max
# FORMAT:
# intercept
# (standarized) current.dosage,  
# engagement.indc, 
# work.loc, 
# other.loc, 
# variation.indc

data.policy$mu <- rep(0, 6)
data.policy$Sigma <- diag(1, 6)
data.policy$pi_max <- 0.8;
data.policy$pi_min <- 0.1;
data.policy$gamma.mdp <- 0.9;
data.policy$Q.mat <- matrix(0, 100, 2);


# ===== Create a holder to save the entire (imputated and unstandarized) history ====== ####

var.names <- c("day", "decision.time", 
           "availability", "probability", "action", "reward",
           "dosage", "engagement", "work.location", "other.location", "variation",
           "temperature", "logpresteps", "sqrt.totalsteps", "prepoststeps", "random.number")

data.history <- matrix(NA, nrow = 5*ndays, ncol = length(var.names))
colnames(data.history) <- var.names
data.history <- data.frame(data.history)

# just fill in the variables might be used later (avail, action, reward)
data.history$day <- -rep(ndays:1, each = 5) # negative represents before the study
data.history$decision.time <- rep(1:5, times = ndays)
data.history$availability <- c(t(input$availMatrix))
data.history$probability <- 0;
data.history$action <- 0;
data.history$dosage <- 1;
data.history$reward <- log(0.5 + c(t(input$postStepsMatrix)))

# the imputed pre and post steps using cumulative averages
# if the first one is missing, then use the total average

prestep.mat <- NULL # column: decision time
for(k in 1:5){
  
  temp <- input$preStepsMatrix[, k]
  
  if(is.na(temp[1])){
    
    temp[[1]] <- mean(temp, na.rm = TRUE)
    
  }
  
  for(i in 2:ndays){
    
    temp[i] <- mean(temp[1:i], na.rm = TRUE)
    
  }
  
  prestep.mat <- cbind(prestep.mat, temp)
  
  
}

poststep.mat <- NULL # column: decision time
for(k in 1:5){
  
  temp <- input$postStepsMatrix[, k]
  
  if(is.na(temp[1])){
    
    temp[[1]] <- mean(temp, na.rm = TRUE)
    
  }
  
  for(i in 2:ndays){
    
    temp[i] <- mean(temp[1:i], na.rm = TRUE)
    
  }
  
  poststep.mat <- cbind(poststep.mat, temp)
  
  
}
data.history$prepoststeps <- c(t(prestep.mat + poststep.mat))

# =====  Data Holder for the first day ==== ####
# study day / dosage on the first decision time / engagement indicator yesterday / 
# historical variation measure / sqrt of total steps yesterday 

data.day <- list()

# study day
data.day$study.day <- 1

# dosage related
data.day$yesterdayLast.dosage <-  1 # dosage at the fifth decision yesterday prior to treatment
data.day$fifthToEnd.anti <- FALSE # indicator of whether there is anti-sed msg sent between 5th to the end of yesterday
data.day$fifth.act <- FALSE # indicator of whether there is activity msg sent at fifth decision time yesterday

# sqrt steps (imputed if last day is missing)
data.day$sqrtsteps <- sqrt(input$totalStepsArray[ndays]) # not in action selection
if(is.na(data.day$sqrtsteps)){
 
  if(all(is.na(input$totalStepsArray))){
    
    # all previous days have missing total steps
    data.day$sqrtsteps <- NA
    
  }else{
    
    # impute by the average of the past (at most) 7 known days' value
    data.day$sqrtsteps <- sqrt(mean(data.imputation$totalsteps))
    
  }
  
}

# app engagement (imputed if last day is missing)
data.day$engagement <- (input$appClicksArray[ndays] >= data.imputation$thres.appclick)
if(is.na(data.day$engagement)){
  
  # use the known average, then we get true 
  data.day$engagement <- (mean(input$appClicksArray, na.rm=T) >= data.imputation$thres.appclick)
  
}

# use the history to define it based on the protocol 
data.day$variation <- rep(NA, 5)
for(k in 1:5){
  
  Y1 = sd(subset(data.history, decision.time == k)$prepoststeps)
  Y0 = sd(subset(data.history, decision.time == k & day < -1)$prepoststeps) # exclude the last day
  data.day$variation[k] <- (Y1 >= Y0)
  
}

# keep the names to ensure the format is same
data.day$var.names <- var.names



# ===== create the folder for the user and save the datasets ====== ####

if(dir.exists("./data") == FALSE){
  
  dir.create("./data")

}

paths <- paste("./data/", "user", input$userID, sep="")
dir.create(paths, showWarnings = FALSE)

save(data.day, file = paste(paths, "/daily.Rdata", sep=""))
save(data.policy, file = paste(paths, "/policy.Rdata", sep=""))
save(data.history, file = paste(paths, "/history.Rdata", sep=""))
save(data.imputation, file = paste(paths, "/imputation.Rdata", sep=""))

