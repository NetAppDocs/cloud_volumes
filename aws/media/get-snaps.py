#!/usr/bin/env python3
import requests
import urllib.request
import json
import sys
import re
import argparse
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

parser = argparse.ArgumentParser()
parser.add_argument("-c","--config", nargs='+', help="config file")
parser.add_argument("-m","--mountpoint", nargs='+', help="mountpoint")
args = parser.parse_args()

if args.config:
	if len(args.config)!=1:
		print('a config file is required')
		sys.exit(1)
else:
	print('a config file is required')
	sys.exit(1)

if args.mountpoint:
	if len(args.mountpoint)!=1:
		print('a volume mountpoint is required')
		sys.exit(1)
else:
	print('a volume mountpoint is required')
	sys.exit(1)

conf=args.config[0]
file = open(conf, 'r')
volid = False

# read config files for keys and api endpoint
for line in file:
	if 'apikey' in line:
		apikey=(line.split("=")[1].rstrip('\n'))
	if 'secretkey' in line:
		secretkey=(line.split("=")[1].rstrip('\n'))
	if 'url' in line:
		url=str(line.split("=")[1].rstrip('\n'))
		url=(url.replace("v1", "v2"))

head = {}
head['api-key'] = apikey
head['secret-key'] = secretkey
head['content-type'] = 'application/json'

command = 'Volumes'
url = url+command

# get Volumes
req = requests.get(url, headers = head)
vols=(len(req.json()))

# search for VolumeId
for vol in range(0, vols):
	if ((req.json()[vol])['creationToken']) == args.mountpoint[0]:
		volid = ((req.json()[vol])['volumeId'])
		region = ((req.json()[vol])['region'])
if not volid :
	print('Mountpoint '+args.mountpoint[0] + ' does not exist')
	sys.exit(1)

# get snapshots
def getsnaps(volid, url, head):
	url = url+'/'+volid+'/Snapshots'
	req = requests.get(url, headers = head)
	details = json.dumps(req.json(), indent=4)
	print('Snapshots in volume '+args.mountpoint[0])
	print(highlight(details, JsonLexer(), TerminalFormatter()))


getsnaps(volid, url, head)


