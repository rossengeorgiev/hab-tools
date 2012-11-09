#!/usr/bin/env python
import sys
import urllib
import urllib2
import re
import json
from getpass import getpass
from time import sleep
from datetime import datetime
import time

#---------------------------------
# CONFIG
#---------------------------------
apikey 		= "" # (optional) API for your aprs.fi account

#---------------------------------
# Program Code
#---------------------------------
if(len(sys.argv) < 2):
	print "Usage: python %s <callsign>" % sys.argv[0]
	print "\nUploads latest APRS cordinates and altitude to spacenear.us"
	sys.exit()

callsign 	= sys.argv[1];

class aprs:
	def __init__(self, callsign, apikey = ''):
		self.csign = callsign
		self.apikey = apikey
		self.password = getpass("spacenear.us password: ")

	def openurl(self, url, post = []):
		if(len(post) > 0):
			data = urllib.urlencode(post)
			request = urllib2.Request(url, data)
		else:
			request = urllib2.Request(url)

		return urllib2.urlopen(request).read()

	def check(self):
		url = "http://api.aprs.fi/api/get?name=%s&what=loc&apikey=%s&format=json" % (self.csign, self.apikey)
		data = json.loads(self.openurl(url))

		if data['result'] == "fail":
			print "[Error] %s" % data['description']
			return 0
		elif int(data['found']) < 1:
			print "[Error] no position data for %s" % self.csign
			return 0

		data = data['entries'][-1]

		self.pos = {
									"vechicle": "%s (APRS)" % self.csign,
									"time"		: data['time'],
									"lat"			: data['lat'],
									"lon"			: data['lng'],
									"alt"			: data['altitude'] if data.has_key('altitude') else 0,
#									"comment"	: data['comment'],
									"pass"		: self.password 
								}

		return 1

	def submitPosition(self):
		url = "http://spacenear.us/tracker/track.php"
		temp = self.openurl(url, self.pos).split("\n")[1:]
		print '[Submited] %s' % ' '.join(temp)


payload = aprs(callsign, apikey)

while 1:
	try:
		if payload.check():
			payload.submitPosition()
		
		sleep(1)
	except KeyboardInterrupt:
		print "Exiting..."
		sys.exit()
	
	
