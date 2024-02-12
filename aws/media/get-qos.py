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

standard_qos = 16
premium_qos = 64
extreme_qos = 128

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

# get volume details
def getqos(volid, url, head):
	url = url+'/'+volid
	req = requests.get(url, headers = head)
	service_level=(req.json()['serviceLevel'])
	allocated=((req.json()['quotaInBytes'])/1000000000000)
	print('For mountpoint "' + args.mountpoint[0] + '" :') 
	print('Service Level = ' + service_level)
	print('Allocated Capacity = ' + str(round(allocated,4)) + ' TB')
	if (req.json()['serviceLevel']) == 'extreme':
		qos = (extreme_qos * allocated)
		print('QoS throughput policy = 0-' + str(round(qos,4)) + ' MB/s')
	if (req.json()['serviceLevel']) == 'premium':
		qos = (premium_qos * allocated)
		print('QoS throughput policy = 0-' + str(round(qos,4)) + ' MB/s')
	if (req.json()['serviceLevel']) == 'standard':
		qos = (standard_qos * allocated)
		print('QoS throughput policy = 0-' + str(round(qos,4)) + ' MB/s')

getqos(volid, url, head)
