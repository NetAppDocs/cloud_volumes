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
		print('a volume mountpoint is require')
		sys.exit(1)
else:
	print('a volume mountpoint is require')
	sys.exit(1)

conf=args.config[0]
file = open(conf, 'r')

for line in file:
	if 'apikey' in line:
		apikey=(line.split("=")[1].rstrip('\n'))
#		print(apikey)
	if 'secretkey' in line:
		secretkey=(line.split("=")[1].rstrip('\n'))
#		print(secretkey)
	if 'url' in line:
		url=str(line.split("=")[1].rstrip('\n'))
#		print(url)

head = {}
head['api-key'] = apikey
head['secret-key'] = secretkey
head['content-type'] = 'application/json'

command = 'FileSystems'
url = url+command

req = requests.get(url, headers = head)
vols=(len(req.json()))

for vol in range(0, vols):
#	if ((req.json()[vol])['creationToken']) == mount:
	if ((req.json()[vol])['creationToken']) == args.mountpoint[0]:
		print((req.json()[vol])['fileSystemId'])


