#!/usr/bin/env python3
import requests
import urllib.request
import json
import sys
import re
import argparse
import datetime
import time
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

parser = argparse.ArgumentParser()
parser.add_argument("-a","--allocation", type=int, help="allocated_size_in_GB (100 to 100000") 
parser.add_argument("-c","--config", nargs='+', help="config file")
parser.add_argument("-e","--export", action='append', nargs='+', help="protocol <nfs3|nfs41|nfs3+41|smb|nfs3+smb|nfs41+smb|nfs3+41+smb> and for nfs3|41 a valid CIDR and rw|ro")
parser.add_argument("-hs","--hide_snapshot", action='store_true', help="hide the snapshot directory")
parser.add_argument("-l","--service_level", nargs='+', help="service level <standard|premium|extreme>")
parser.add_argument("-m","--mountpoint", nargs='+', help="mountpoint")
parser.add_argument("-N","--new_mountpoint", nargs='+', help="new mountpoint for the copy")
parser.add_argument("-n","--name", nargs='+', help="name")
parser.add_argument("-r","--region", nargs='+', help="region")
parser.add_argument("-t","--tag", nargs='+', help="tag (optional)")
args = parser.parse_args()

if args.config:
	if len(args.config)!=1:
		print('a config file is required')
		sys.exit(1)
else:
	print('a config file is required')
	sys.exit(1)

if args.name:
	if len(args.name)!=1:
		print('a name is required')
		sys.exit(1)
else:
	print('a name is required')
	sys.exit(1)

if args.hide_snapshot:
	snapshot_directory = False
else:
	snapshot_directory = True

if args.service_level:
	if len(args.service_level)!=1:
		print('a service level is required')
		sys.exit(1)
else:
	print('a service level is required')
	sys.exit(1)

if args.mountpoint:
	if len(args.mountpoint)!=1:
		print('a parent mountpoint is required')
		sys.exit(1)
else:
	print('a parent mountpoint is required')
	sys.exit(1)

if args.new_mountpoint:
	if len(args.new_mountpoint)!=1:
		print('a mountpoint is required for the copy')
		sys.exit(1)
else:
	print('a mountpoint is required for the copy')
	sys.exit(1)

if args.allocation:
	if (args.allocation)<100 or (args.allocation)>100000:
		print('Allocation size must be between 100 to 100000 GB')
		sys.exit(1)
	else:
		args.allocation = args.allocation * 1000000000

# check service level and word swap to match UI
if args.service_level:
	if (args.service_level)[0] != 'standard' and (args.service_level)[0] != 'premium' and (args.service_level)[0] != 'extreme':
		print('Service level must be standard, premium or extreme')
		sys.exit(1)

if args.region:
	if (args.region)[0] != 'us-east-1' and (args.region)[0] != 'us-west-1' and (args.region)[0] != 'us-west-2' and (args.region)[0] != 'eu-central-1' and (args.region)[0] != 'eu-west-1' and (args.region)[0] != 'eu-west-2' and (args.region)[0] != 'ap-northeast-1' and (args.region)[0] != 'ap-southeast-2':
		print('Please select an available region')
		sys.exit(1)	
else:
	print('Please select an available region')
	sys.exit(1)

tag = ''
if args.tag:
	tag = args.tag[0]

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

now=(datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S"))
snapshot={}

# take a snapshot of the parent volume
def take_snap(volid, url, data, head):
	url = url+'/'+volid+'/Snapshots'
	data_json = json.dumps(data)
	req = requests.post(url, headers = head, data = data_json)
	details = json.dumps(req.json(), indent=4)
	print('Created snapshot in volume '+args.mountpoint[0])
	snap = [((req.json()['snapshotId']))]
	snapshot.update({'snapshot':snap})
#	print(highlight(details, JsonLexer(), TerminalFormatter()))

data = {
	"name": "snap-"+str(now),
	"fileSystemId": volid,
	"region": region
		}

take_snap(volid, url, data, head)

if args.export:
	rule=[]

	for r in range (0, len(args.export)):
		if (args.export[r][0]) == 'smb':
			rules = {"rules": []}
			protocols = [ 'CIFS' ]
			data = {
				"name": args.name[0],
				"creationToken": args.mountpoint[0],
				"region": args.region[0],
				"serviceLevel": args.service_level[0],
				"quotaInBytes": args.allocation,
				"exportPolicy": rules,
				"protocolTypes": protocols,
				"snapshotId": snapshot,
				"snapshotDirectory": snapshot_directory,
				"labels": [tag]
				}
			create(volid, url, data, head)
			sys.exit(1)
	
	for r in range (0, len(args.export)):
		if (args.export[r][0]) != 'nfs3' and (args.export[r][0]) !='nfs41' and (args.export[r][0]) !='nfs3+41' and (args.export[r][0]) !='smb' and (args.export[r][0]) != 'nfs3+smb' and (args.export[r][0]) != 'nfs41+smb' and (args.export[r][0]) != 'nfs3+41+smb':
			print('First argument should be nfs3, nfs41, nfs3+41, smb, nfs3+smb, nfs41+smb or nfs3+41+smb')
			sys.exit(1)

		if (len(args.export[r])) < 3:
			print('For nfs please provide a CIDR and rw|ro')
			sys,exit(1)
		if (args.export[r][0]) == 'nfs3':
			nfs3, nfs41, cifs = True, False, False
			protocols = [ 'NFSv3' ]
		elif (args.export[r][0]) == 'nfs41':
			nfs3, nfs41, cifs = False, True, False
			protocols = [ 'NFSv4' ]
		elif (args.export[r][0]) == 'nfs3+41':
			nfs3, nfs41, cifs = True, True, False
			protocols = [ 'NFSv3', 'NFSv4' ]
		elif (args.export[r][0]) == 'nfs3+smb':
			nfs3, nfs41, cifs = True, False, True
			protocols = [ 'NFSv3', 'CIFS' ]
		elif (args.export[r][0]) == 'nfs41+smb':
			nfs3, nfs41, cifs = False, True, True
			protocols = [ 'NFSv4', 'CIFS' ]
		else :
			nfs3, nfs41, cifs = True, True, True
			protocols = [ 'NFSv3', 'NFSv4', 'CIFS' ]
		export = (args.export[r][1])
		if (args.export[r][2]) != 'ro' and (args.export[r][2]) != 'rw':
			print('ro (read only) or rw (read write) must be provided')
			sys.exit(1)
		elif (args.export[r][2]) == 'ro':
			rw, ro = False, True
		else: 
			rw, ro = True, False
		rule_index=r+1
		index = {"ruleIndex": rule_index,"allowedClients": export,"unixReadOnly": ro,"unixReadWrite": rw,"cifs": cifs,"nfsv3": nfs3,"nfsv4": nfs41}
		rule.append(index)
		rules = {"rules": rule}

# create volume from snapshot
def create(volid, url, data, head):
	data_json = json.dumps(data)
	req = requests.post(url, headers = head, data = data_json)
	details = json.dumps(req.json(), indent=4)
	print('Created volume '+args.new_mountpoint[0])
	print(highlight(details, JsonLexer(), TerminalFormatter()))

data = {
	"name": args.name[0],
	"creationToken": args.new_mountpoint[0],
	"region": args.region[0],
	"serviceLevel": args.service_level[0],
	"quotaInBytes": args.allocation,
	"exportPolicy": rules,
	"protocolTypes": protocols,
	"snapshotId": snapshot['snapshot'][0],
	"snapshotDirectory": snapshot_directory,
	"labels": [tag]
	}

# test if snapshot is available
time.sleep(1)
surl = url+'/'+volid+'/Snapshots/'+snapshot['snapshot'][0]
req = requests.get(surl, headers = head)
status = json.dumps(req.json(), indent=4)
while ((req.json())['lifeCycleState']) != 'available':
	time.sleep(1)
	req = requests.get(surl, headers = head)

create(volid, url, data, head)
