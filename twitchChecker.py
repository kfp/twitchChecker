#!/usr/bin/env python

import urllib2, json, sys, getopt, subprocess, os, time
from termcolor import colored
from prettytable import PrettyTable

#TwitchChannels = ['yourchannel']
## newline seperated channels
TwitchChannels = [line.rstrip('\n') for line in open('channels.txt')]

DEVNULL = open(os.devnull, 'wb')
TWITCHCHECKER_CLIENT_ID = 'ae5gdyajcqmlrcafcwjqzlfbs1botlr'
LIVESTREAMER_CLIENT_ID = 'ewvlchtxgqq88ru9gmfp1gmyt6h2b93'
QUALITY_PRIORITIES = ['1080p60', '1080p', '720p60', 'source', 'best']

def getTwitchData(channels):
	url = 'https://api.twitch.tv/kraken/streams?channel='+channels
	viewers = -1
	data = None
	try:
                req = urllib2.Request(url)
                req.add_header('Client-ID',TWITCHCHECKER_CLIENT_ID)
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
	twitchData = getTwitchData(channels = ','.join([str(x) for x in TwitchChannels]))
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
	channel = TwitchChannels[channelNumber]
	#channelData = getChannelData(getTwitchData(channel), channel)

	for quality in QUALITY_PRIORITIES:
		popen = doLoadStream(channel, quality)
		time.sleep(3)
		if(popen.poll() != None):
			print quality +" stream not available. Falling back..."
		else:
                        popen.poll() #fixes some race condition somehow
			return

def doLoadStream(channel, quality="best"):
	execList = ["livestreamer",'--http-header', 'Client-ID='+LIVESTREAMER_CLIENT_ID,'twitch.tv/'+channel, quality]
	print 'Loading stream... '+ ' '.join(execList)
	logfile = open("streamOut.log", 'w');
	return subprocess.Popen(execList, stdout=logfile, stderr=logfile)

def doLoadChat(channelNumber):
	execList = ["Chatty", '-connect', '-channel', ''+TwitchChannels[channelNumber]]
	print 'Loading chat... '+ ' '.join(execList)
	logfile = open("chatOut.log", 'w');
	return subprocess.Popen(execList, stdout=DEVNULL, stderr=logfile)

def usage():
		print '''
Usage: '''+ sys.argv[0] + '''
	[-l list available channels]
	[-o <id> load specified video channel ID]
	[-c <id> list specified chat channel ID]
	Channels are loaded one per line from channels.txt
	livestreamer required for video, chatty required for chat
				'''

def main(argv):
	try:
		opts, args = getopt.getopt(argv,"hlo:c:")
	except getopt.GetoptError as err:
		print(err)
		usage()
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-l':
			listStreams()
		elif opt == '-o':
			loadStream(int(arg))
		elif opt == '-c':
			doLoadChat(int(arg))
		elif opt == '-h':
			usage()

if __name__ == "__main__":
	main(sys.argv[1:])
