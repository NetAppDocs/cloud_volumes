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
parser.add_argument("-s","--snapshot", nargs='+', help="snapshotId or 'last'")
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

if args.snapshot:
	if len(args.mountpoint)!=1:
		print('please provide a snapshotId or enter "last"')
		sys.exit(1)
else:
	print('please provide a snapshotId or enter "last"')
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

# create header
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

# search for snapshot
if args.snapshot[0] == 'last':
	surl = url+'/'+volid+'/Snapshots'
	snap = requests.get(surl, headers = head)
	snaps=(len(snap.json())-1)
	snapshot = ((snap.json()[snaps])['snapshotId'])
else:
	snapshot = args.snapshot[0]

# revert volume to snapshot
def revert_snap(volid, url, data, head):
	url = url+'/'+volid+'/Revert'
	data_json = json.dumps(data)
	req = requests.post(url, headers = head, data = data_json)
	details = json.dumps(req.json(), indent=4)
	print('Reverted to snapshot '+snapshot)
	print(highlight(details, JsonLexer(), TerminalFormatter()))

data = {
	"snapshotId": snapshot,
	"volumeId": volid,
	"region": region
		}

revert_snap(volid, url, data, head)


