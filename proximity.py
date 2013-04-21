#!/usr/bin/env python

import daemon, os, time, imaplib, sys, urllib2, json
from datetime import datetime
from xml.dom import minidom

devices = {
	'90:21:55:AE:E4:0B': {'name':'Cristian Grigoriu', 'email':'grig@sinc.ro', 'emailpw':'secret', 'twitter':'digitalGrig'}, 
	'CC:78:5F:2D:76:8D': 'George Dragusin',
	}
thrsh = 200

def pngrender(baddr):
	t = gettime()
	w = getweather()
	cmd = "convert -size 600x800 xc:white -draw \"\
			font Roboto-Black font-size 48 text 230,780 '{0}' \
			font Roboto-Black font-size 72 text 40, 180 '{1}' \
			font Roboto-Medium font-size 48 text 40, 230 '{2}' \
			font Roboto-Black font-size 64 text 40, 293 '{3} {4}' \
			font Roboto-Medium font-size 48 text 40, 345 '{5}' \
			font Roboto-Medium font-size 64 text 40, 500 'Emailuri:' \
			font Roboto-Black font-size 64 text 300, 500 '{6}' \
			font Roboto-Medium font-size 64 text 40, 580 'Twittere:' \
			font Roboto-Black font-size 64 text 300, 580 '{7}' \
			font Roboto-Black font-size 64 text 350, 180 '{8} C' \
			font Roboto-Black font-size 64 text 350, 250 '{9}% ' \
			font Roboto-Black font-size 64 text 350, 320 '{10}/{11}' \
			\" -depth 8 -type GrayScale /tmp/kindle.png".format(devices[baddr]['name'], t[0], t[1], t[2], t[3], t[4], getemails(baddr), gettwitter(baddr), w[0], w[1], w[2], w[3])
	f = os.popen(cmd)
	cmd = "scp -i /home/pi/.ssh/id_rsa /tmp/kindle.png root@192.168.2.2:/tmp/;ssh -i /home/pi/.ssh/id_rsa root@192.168.2.2 \"/usr/sbin/eips -c;/usr/sbin/eips -c;/usr/sbin/eips -g /tmp/kindle.png\""
	f = os.popen(cmd)

def blank_render():
	t = gettime()
	w = getweather()
	cmd = "convert -size 600x800 xc:white -draw \"\
			font Roboto-Black font-size 72 text 40, 180 '{1}' \
			font Roboto-Medium font-size 48 text 40, 230 '{2}' \
			font Roboto-Black font-size 64 text 40, 293 '{3} {4}' \
			font Roboto-Medium font-size 48 text 40, 345 '{5}' \
			font Roboto-Black font-size 64 text 350, 180 '{8} C' \
			font Roboto-Black font-size 64 text 350, 250 '{9}% ' \
			font Roboto-Black font-size 64 text 350, 320 '{10}/{11}' \
			\" -depth 8 -type GrayScale /tmp/kindle.png".format('', t[0], t[1], t[2], t[3], t[4], 0, 0, w[0], w[1], w[2], w[3])
	f = os.popen(cmd)
	cmd = "scp -i /home/pi/.ssh/id_rsa /tmp/kindle.png root@192.168.2.2:/tmp/;ssh -i /home/pi/.ssh/id_rsa root@192.168.2.2 \"/usr/sbin/eips -c;/usr/sbin/eips -c;/usr/sbin/eips -g /tmp/kindle.png\""
	f = os.popen(cmd)

def getemails(baddr):
	obj = imaplib.IMAP4_SSL('in.sinc.ro','993')
	obj.login(devices[baddr]['email'], devices[baddr]['emailpw'])
	obj.select()
	obj.search(None,'UnSeen')
	return len(obj.search(None, 'UnSeen')[1][0].split())

def gettwitter(baddr):
	req = urllib2.Request('https://api.twitter.com/1/users/show.json?screen_name={0}&include_entities=true'.format(devices[baddr]['twitter']))
	response = urllib2.urlopen(req)
	the_page = response.read()
	data = json.loads(the_page)
	return data['listed_count'] 

def gettime():
	weekdays = ['Luni', 'Marti', 'Miercuri', 'Joi', 'Vineri', 'Sambata', 'Duminica']
	months = ['Ianuarie', 'Februarie', 'Martie', 'Aprilie', 'Mai', 'Iunie', 'Iulie', 'August', 'Septembrie', 'Octombrie', 'Noiembrie', 'Decembrie']
	now = time.localtime()
	return [time.strftime("%H:%M", now), weekdays[int(time.strftime("%u", now)) -1], time.strftime("%d", now), months[int(time.strftime("%m", now))], time.strftime("%Y", now)]

def getweather():
	url = "http://rp5.ru/xml/8927/00000/ro"
	response = urllib2.urlopen(url)
	xml = response.read()
	xmldoc = minidom.parseString(xml)
	weather = xmldoc.getElementsByTagName('timestep')[0]
	t = weather.getElementsByTagName('temperature')
	h = weather.getElementsByTagName('humidity')
	v = weather.getElementsByTagName('wind_velocity')
	d = weather.getElementsByTagName('wind_direction')
	return [t[0].firstChild.nodeValue, h[0].firstChild.nodeValue, v[0].firstChild.nodeValue, d[0].firstChild.nodeValue]

def proximity():
	while True:
		time.sleep(5)
		for baddr in devices:
			cmd = "hcitool cc {0} 2>/dev/null;hcitool lq {0} 2>/dev/null".format(baddr)
			f = os.popen(cmd)
			lines = f.readlines()
			for line in lines:
				if (line.startswith('Link')):
					link = int(int(line.rpartition(':')[2].strip()))
					if (link > thrsh):
						#pngrender(baddr)
						print "in zona"
					else:
						#blank_render()
						print "departe"
				else:
					#blank_render()
					print "departe"


def run():
	with daemon.DaemonContext():
		proximity()

if __name__ == "__main__":
	#run()
	proximity()

