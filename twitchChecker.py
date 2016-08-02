import urllib2, json, sys, getopt, subprocess, os, progressbar, time
from termcolor import colored
from prettytable import PrettyTable

TwitchChannels = ['lagtvmaximusblack', 'forcestrategygaming', 'jackfrags', 'yogscast', 'sips_', 'moonduckTV', 'dotastarladder_en', 'beyondTheSummit', 'admiralbulldog']
DEVNULL = open(os.devnull, 'wb')


def getTwitchData(TwitchChannel): # return the stream Id is streaming else returns -1
	url = str('https://api.twitch.tv/kraken/streams/'+TwitchChannel)
	viewers = -1
	data = None
	try:
		respose = urllib2.urlopen(url)
	except:
		return None
	html = respose.read()
	data = json.loads(html)
	return data
	try:
		viewers = data['stream']['viewers']
	except:
		viewers = -1
	return int(viewers)

def listStreams():
	print "Fetching info..."
	i = 0
	totalChannels = len(TwitchChannels)
	t = PrettyTable(['ID', 'Channel', 'Viewers', 'Title'])
	t.sortby = "Viewers"
	t.reversesort = True
	t.align['Title'] = "l"
	with progressbar.ProgressBar(maxval=totalChannels) as bar:
		for channel in TwitchChannels:
			twitchData = getTwitchData(channel)
			color = 'green'
			viewers = 0
			title = ''

			if twitchData is None:
				color = 'red'
			elif twitchData['stream'] is None:
				color = 'yellow'
			else:
				viewers = twitchData['stream']['viewers']
				title = twitchData['stream']['channel']['status']
				title = title[:75] + (title[75:] and '..')
			t.add_row([i, colored(channel, color), viewers, colored(title, 'cyan')])
			i += 1
			bar.update(i)
	print t

def loadStream(channelNumber):
	execStr = 'livestreamer twitch.tv/'+TwitchChannels[channelNumber]+' best'
	print 'Loading stream... '
	subprocess.Popen(["livestreamer",'twitch.tv/'+TwitchChannels[channelNumber],"best"], stdout=DEVNULL, stderr=DEVNULL)

def main(argv):
	try:
		opts, args = getopt.getopt(argv,"lo:")
	except getopt.GetoptError:
		print 'twitchChecker.py -l/ -o #'
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-l':
			listStreams()
		elif opt == '-o':
			loadStream(int(arg))

if __name__ == "__main__":
	main(sys.argv[1:])
