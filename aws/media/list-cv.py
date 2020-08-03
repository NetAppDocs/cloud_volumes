#!/usr/bin/env python3
import requests
import json
import argparse
import sys
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

parser = argparse.ArgumentParser()
parser.add_argument("-c","--config", nargs='+', help="config file")
args = parser.parse_args()

if args.config:
	if len(args.config)!=1:
		print('a config file is required')
		sys.exit(1)
else:
	print('a config file is required')
	sys.exit(1)

conf=args.config[0]
file = open(conf, 'r')

# read config files for keys and api endpoint
for line in file:
	if 'apikey' in line:
		apikey=(line.split("=")[1].rstrip('\n'))
	if 'secretkey' in line:
		secretkey=(line.split("=")[1].rstrip('\n'))
	if 'url' in line:
		url=str(line.split("=")[1].rstrip('\n'))
		url=(url.replace("v1", "v2"))

# create header
headers = {}
headers['api-key'] = apikey
headers['secret-key'] = secretkey
headers['content-type'] = 'application/json'

command = 'Volumes'
url = url+command

# get volumes
req = requests.get(url, headers = headers)
volumes = json.dumps(req.json(), indent=4)

print(highlight(volumes, JsonLexer(), TerminalFormatter()))

vols=(len(req.json()))
print('There are '+str(vols)+' volumes')
