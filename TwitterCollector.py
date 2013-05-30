import twitter
import time
import argparse
from pretty_time import prettyITime


"""Data collected: self.search_string, str(user.screen_name), str(created_at), str(text), id, created_at_in_seconds"""

class TweetCollector:
	"""Class for downloading recent tweets. Search input for this use
	case will be a 4-letter string stock ticker. Will download all tweets
	that show up for the given search term and write them, as well as
	associated metadate, to a file for further analysis.

	"search_string" (str) : The string to search for.
	"int rate" (int seconds): The interval (in seconds) between search queries.
	"freshness (int seconds): Makes sure every tweet collected is at MOST this many seconds old."""

	def __init__(self, search_string, rate = 300, freshness = 100000, verbose = False, last_search_time = 0):
		self.api              = twitter.Api(consumer_key = '4u0qnjcETVeM8vuFbM63A',
			consumer_secret   = 'DGvkyymB4WpUwIeCNbMyO3OTjRSDKiso85JpJsIcnb4',
			access_token_key  = '1439653741-hnQCfbMB8K8LzaaNV99sUmldBGngeRGMEbna6ma',
		  access_token_secret = 'WxKqa2huSiMe6v00ORpwupfXcb9q2PfV89Ko4Z33MGE')
		self.search_string    = search_string
		self.rate             = rate
		self.last_search_time = 0
		self.verbose          = verbose
		self.last_id          = None
		self.cache            = []
		self.freshness        = freshness
		self.filename         = "%s %s-%s-%s %s %is" % (self.search_string,
										time.localtime().tm_mon, time.localtime().tm_mday,
										time.localtime().tm_year, prettyITime(int(time.time())),
										self.rate)

	def _search(self):
		"""Perfoms a simple search for a string in twitter. Returns a list
		of twitter.Status objects."""
		results = self.api.GetSearch(self.search_string, since_id = self.last_id)
		if len(results) == 0:
			return results
		self.last_id = max(tweet.id for tweet in results)
		results.sort(key = lambda x: x.created_at_in_seconds)
		return results

	def _WriteTweetData(self):
		f = open(self.filename, 'a')
		if self.verbose:
			print "Opening File ", self.filename
			print "Writing to File..."
		for tweet in self.cache:
			screen_name = str(tweet.user.screen_name)
			created_at = str(''.join(letter for letter in tweet.created_at if letter.isalnum() or letter == ' '))
			text = "".join(letter for letter in tweet.text if letter.isalnum() or letter == ' ')
			id = tweet.id
			created_at_in_seconds = int(tweet.created_at_in_seconds)
			try:
				f.write("\"%s\",\"%s\",\"%s\",\"%s\",%i,%s" % (self.search_string,
															screen_name, created_at,
															text, id, prettyITime(created_at_in_seconds)))
			except:
				continue
			f.write('\n')
			if self.verbose: print screen_name, created_at
		f.close()
		if self.verbose: print "Done. Local Cache Emptied."
		self.cache = []

	def GetTweets(self):
		start_time = int(time.time())
		
		if self.verbose:
			print prettyITime(start_time), "called GetTweets"
		if start_time > (self.last_search_time + self.rate):
			if self.verbose: print "Searching for ", self.search_string
			results = self._search()
			if self.verbose: print "Pulled down %i new tweets." % len(results)
			self.last_search_time = start_time
			if len(results) == 0:
				if self.verbose: print "No new results."
				return
			self.cache += results
			if self.verbose: print "Holding %i tweets in cache." % len(self.cache)
			cutoff = start_time - self.freshness
			print "Cutoff time:", prettyITime(cutoff)
			print "Got ", len(self.cache), " tweets before time-filter."
			filtered_cache = []
			for tweet in self.cache:
				if tweet.created_at_in_seconds > cutoff:
					filtered_cache.append(tweet)
				elif self.verbose:
					print "Removed ", tweet.text, " created at ", prettyITime(tweet.created_at_in_seconds)
			self.cache = filtered_cache
			if self.verbose:
				print "Got ", len(self.cache), " tweets after time-filter."
				for tweet in self.cache:
					print tweet.text
			self._WriteTweetData()

def main():
	parser = argparse.ArgumentParser('TwitterCollector')
	parser.add_argument("-v", "--verbose", dest="v", help="Prints out real-time info.", action = "store_true")
	parser.add_argument("ticker", help = "the ticker to search for, prepended with a $ sign")
	args = parser.parse_args()

	ticker = args.ticker
	ticker_collector = TweetCollector(ticker, verbose = args.v)

	while True:
		print "~~~~~~~~~", prettyITime(time.time())
		ticker_collector.GetTweets()
		time.sleep(60)

if __name__ == '__main__':
	main()
