import twitter
import time
import argparse
from os import listdir
from rpy import *
import csv
r("""source('k-means.R')""")

api = twitter.Api(consumer_key = 'cHLHog4YUgR9dfYp34HGQ',
			consumer_secret   = 'Jh0ASrw6tX1SowwfGTyAuKj1VJsj5ZGQ59es2U57TL4',
			access_token_key  = '1439653741-rp07suWh4Le6OOgHwFy4bcdkG2c8LVsBy4FzhpQ',
		  access_token_secret = 'OFV1at1ZFXe2LWIHb2DZsFRFzbJ2mwxcXC58Gikw')

"""Each of these users will be contained in a large data frame.
   Frame structure: Each column is a user, each row is a user statistic:
   Ordering: 1. ID number
   			 2. numStatuses
   			 3. numFollowers
   			 4. numFriends
   			 5. numListed
   			 6. numFavorites"""

class user:
	"""Represents a twitter user with some relevant statistics.
	   For now, contains:
		self.name: string screen name of user
		self.id: unique user ID number
		self.numStatuses: total number of statuses posted
		self.numFollowers: total number of followers
		self.numFriends: total number of friends
		self.numListed: the total number of lists this user is on
		self.avgRetweet: the average number of retweets for each of the user's last ~18 tweets
		self.numFavorites: number of favorites the user has

	The only argument is the (str) name of the user. The rest of the statistics
	will be collected via twitter API."""

	def __init__(self, name):
		self.user             = api.GetUser(name)
		self.name             = name
		self.id               = self.user.id
		self.numStatuses      = float(self.user.statuses_count)
		self.numFollowers     = float(self.user.followers_count)
		self.numFriends       = float(self.user.friends_count)
		self.numListed        = float(self.user.listed_count)
		self.numFavorites     = float(self.user.favourites_count)
		#calculates average retweet rate
		retweet_count = []
		for tweet in api.GetUserTimeline(name):
			retweet_count.append(tweet.retweet_count)
		try:
			self.avgRetweet       = float(sum(retweet_count))/len(retweet_count)
		except:
			self.avgRetweet       = 0


		#Stores a list version of the class as well.
		#This will be coerced into a dictionary for easper processing in R.
		self.list             = [self.id, self.numStatuses, self.numFollowers,
					             self.numFriends, self.numListed, self.numFavorites]

def _readUsers(directory):
	"""Function outside the class for processing files. Helper to makeDataFrame().
	Output: the list of screen names of the users who made the tweets, duplicates removed."""
	files = os.listdir(directory)
	these_users = []
	for text_file in files:
		current_file = directory + '/' + text_file
		f = open(current_file, 'r')
		tweet_list = f.readlines()
		splitted = [string.replace('"', '').strip().split(',') for string in tweet_list]
		for user in splitted:
			if user[1] not in these_users:
				these_users.append(user[1])
			else:
				continue
	return these_users

def _makeDataFrame(directory):
	"""Input: a (str) directory containing collected tweets. 
	   Output: an rpy r-object data.frame in preparation for clustering"""
	these_users = _readUsers(directory)
	masterDict = {}
	for name in these_users:
		current_user = user(name)
		masterDict[current_user.name] = current_user.list
	r.assign('df', masterDict)
	r('df = data.frame(df)')
	r.assign('transpose', r('t(df)'))
	return r('transpose')


def kMeans(df, k, threshold = 0.05, index_list = []):
	"""Wrapper for the k-means.R functions. Indices can be a list of any length
	   representing which statistics you would like to cluster on. The indices
	   correspond to the description of the ordering above. You can try anything,
	   but I don't suggest you try clustering on user ID. You'll probably get some weird junk."""
	r.assign('df', df)
	r('df_transpose = t(df)')
	if len(index_list) == 0:
	   		index_list = [2, 3, 4, 5, 6]
	r.assign('index_list', index_list)
	r('testframe = df_transpose[index_list,]')
	r.assign('k', k)
	r.assign('threshold', threshold)
	results = r('kMeans(testframe, k, threshold)')
	r.assign('results', results)
	return r('results')

