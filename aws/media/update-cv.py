#!/usr/bin/env python3
import requests
import json
import sys
import argparse
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

parser = argparse.ArgumentParser()
parser.add_argument("-a","--allocation", type=int, help="allocated_size_in_GB (100 to 100000") 
parser.add_argument("-c","--config", nargs='+', help="config file")
parser.add_argument("-e","--export", action='append', nargs='+', help="protocol <nfs3|nfs41|nfs3+41|smb|nfs3+smb|nfs41+smb|nfs3+41+smb> and for nfs3|41 a valid CIDR, rw|ro and optionally 'squash'")
parser.add_argument("-hs","--hide_snapshot", action='store_true', help="hide the snapshot directory")
parser.add_argument("-l","--service_level", nargs='+', help="service level <standard|premium|extreme>")
parser.add_argument("-m","--mountpoint", nargs='+', help="mountpoint")
parser.add_argument("-p","--protocol", nargs='+', help="Change NFS protocol <nfs3|nfs41|nfs3+41>")
parser.add_argument("-t","--tag", nargs='+', help="tag (optional)")
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

data = { "creationToken": args.mountpoint[0], "region": region}

# update volume 
def update(volid, url, data, head):
	url = url+'/'+volid
	data_json = json.dumps(data)
	req = requests.put(url, headers = head, data = data_json)
	details = json.dumps(req.json(), indent=4)
	print('Updated volume '+args.mountpoint[0])
	print(highlight(details, JsonLexer(), TerminalFormatter()))

if args.allocation:
	if (args.allocation)<100 or (args.allocation)>100000:
		print('Allocation size must be between 100 to 100000 GB')
		sys.exit(1)
	else:
		args.allocation = args.allocation * 1000000000
	data.update({"quotaInBytes": args.allocation})

if args.service_level:
	if (args.service_level)[0] != 'standard' and (args.service_level)[0] != 'premium' and (args.service_level)[0] != 'extreme':
		print('Service level must be standard, premium or extreme')
		sys.exit(1)
	data.update({"serviceLevel": args.service_level[0]})

if args.hide_snapshot:
	snapshot_directory = False
else:
	snapshot_directory = True
data.update({"snapshotDirectory": snapshot_directory})

if args.tag:
	tag = args.tag[0]
	data.update({"labels": [tag]})

if args.protocol:
	if (args.protocol[0]) == 'nfs3':
		protocols = [ 'NFSv3' ]
	elif (args.protocol[0]) =='nfs41':
		protocols = [ 'NFSv4' ]
	elif (args.protocol[0]) =='nfs3+41':
		protocols = [ 'NFSv3', 'NFSv4' ]
	elif (args.protocol[0]) =='nfs3+smb':
		protocols = [ 'NFSv3', 'CIFS' ]
	elif (args.protocol[0]) =='nfs41+smb':
		protocols = [ 'NFSv4', 'CIFS' ]
	elif (args.protocol[0]) =='nfs3+41+smb':
		protocols = [ 'NFSv3', 'NFSv4', 'CIFS' ]
	else:
		print('Argument for -p should be nfs3, nfs41, nfs3+41, nfs3+smb, nfs41+smb or nfs3+41+smb' )
		sys.exit(1)

	data.update({"protocolTypes": protocols})

else:
	print('Protocol argument is required' )
	sys.exit(1)

if args.export:
	rule=[]

	for r in range (0, len(args.export)):
		if (args.export[r][0]) == 'smb' :
			print('Can not update exports on an SMB volume')
			sys.exit(1)

	for r in range (0, len(args.export)):
		if (args.export[r][0]) != 'nfs3' and (args.export[r][0]) !='nfs41' and (args.export[r][0]) !='nfs3+41' and (args.export[r][0]) !='smb' and (args.export[r][0]) != 'nfs3+smb' and (args.export[r][0]) != 'nfs41+smb' and (args.export[r][0]) != 'nfs3+41+smb':
			print('First -e argument should be nfs3, nfs41, nfs3+41, smb, nfs3+smb, nfs41+smb or nfs3+41+smb')
			sys.exit(1)

		if (len(args.export[r])) < 3:
			print('For nfs please provide a CIDR and rw|ro')
			sys,exit(1)
		if (args.export[r][0]) == 'nfs3':
			nfs3, nfs41, cifs = True, False, False
		elif (args.export[r][0]) == 'nfs41':
			nfs3, nfs41, cifs = False, True, False
		elif (args.export[r][0]) == 'nfs3+41':
			nfs3, nfs41, cifs = True, True, False
		elif (args.export[r][0]) == 'nfs3+smb':
			nfs3, nfs41, cifs = True, False, True
		elif (args.export[r][0]) == 'nfs41+smb':
			nfs3, nfs41, cifs = False, True, True
		else :
			nfs3, nfs41, cifs = True, True, True
		export = (args.export[r][1])
		if (args.export[r][2]) != 'ro' and (args.export[r][2]) != 'rw':
			print('ro (read only) or rw (read write) must be provided')
			sys.exit(1)
		elif (args.export[r][2]) == 'ro':
			rw, ro = False, True
		else: 
			rw, ro = True, False
		if (len(args.export[r])) == 4:		
			if (args.export[r][3]) == 'squash':
				superuser = False
		else:
			superuser = True

		rule_index=r+1
		index = {"ruleIndex": rule_index,"allowedClients": export,"unixReadOnly": ro,"unixReadWrite": rw,"cifs": cifs,"nfsv3": nfs3,"nfsv4": nfs41, "superuser": superuser}
		rule.append(index)
		rules = {"rules": rule}
		data.update({"exportPolicy": rules})

update(volid, url, data, head)
