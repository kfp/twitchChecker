import urllib2, json, sys, getopt, subprocess, os, time
from termcolor import colored
from prettytable import PrettyTable

#TwitchChannels = ['yourchannel']
#newline seperated channels
TwitchChannels = [line.rstrip('\n') for line in open('channels.txt')]
DEVNULL = open(os.devnull, 'wb')
CLIENT_ID = 'ae5gdyajcqmlrcafcwjqzlfbs1botlr'
LIVESTREAMER_CLIENT_ID = 'ewvlchtxgqq88ru9gmfp1gmyt6h2b93'

def getTwitchData(): 
	channels = ','.join([str(x) for x in TwitchChannels])
	url = 'https://api.twitch.tv/kraken/streams?channel='+channels
	viewers = -1
	data = None
	try:
                req = urllib2.Request(url)
                req.add_header('Client-ID',CLIENT_ID)
		respose = urllib2.urlopen(req)
	except:
		return None
	html = respose.read()
	data = json.loads(html)
	return data

def getChannelData(twitchData, channel):
	for channelData in twitchData['streams']:
		if channelData['channel']['name'].lower() == channel.lower():
			return channelData
	return None

def listStreams():
	print "Fetching info..."
	i = 0
	t = PrettyTable(['ID', 'Channel', 'Viewers', 'Title'])
	t.sortby = "Viewers"
	t.reversesort = True
	t.align['Title'] = "l"
	twitchData = getTwitchData()
	for channel in TwitchChannels:
		color = 'green'
		viewers = 0
		title = ''
		channelData = getChannelData(twitchData, channel)

		if channelData is None:
			color = 'yellow'
		else:
			viewers = channelData['viewers']
			title = channelData['channel']['status']
			title = title[:75] + (title[75:] and '..')
			t.add_row([i, colored(channel, color), viewers, colored(title, 'cyan')])
		i += 1
	print t

def loadStream(channelNumber):
	popen = doLoadStream(channelNumber)
	time.sleep(.5);
	if(popen.poll != None):
		print "best stream not available, falling back to 720p60"
		doLoadStream(channelNumber, "720p60")

def doLoadStream(channelNumber, quality="best"):
	execList = ["livestreamer",'--http-header', 'Client-ID='+LIVESTREAMER_CLIENT_ID,'twitch.tv/'+TwitchChannels[channelNumber], quality]
	print 'Loading stream... '+ ' '.join(execList)
	#subprocess.Popen(["livestreamer",'twitch.tv/'+TwitchChannels[channelNumber],"best"], stdout=DEVNULL, stderr=DEVNULL)
	logfile = open("out.log", 'w');
	return subprocess.Popen(execList, stdout=logfile, stderr=logfile)

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
