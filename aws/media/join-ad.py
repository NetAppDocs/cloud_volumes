#!/usr/bin/env python3
import requests
import urllib.request
import json
import sys
import re
import argparse
import datetime
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

parser = argparse.ArgumentParser()
required = parser.add_argument_group('Required')
optional = parser.add_argument_group('Optional')
required.add_argument("-c","--config", nargs='+', help="config file")
required.add_argument("-D","--DNS", nargs='+', help="IP for AD DNS")
required.add_argument("-d","--domain", nargs='+', help="domain for AD") 
required.add_argument("-n","--netbios", nargs='+', help="netBIOS name for the CVS SMB server")
optional.add_argument("-ou","--organizationalUnit", nargs='+', help="OU required, defaults to CN=Computers")
required.add_argument("-p","--password", nargs='+', help="password for an AD admininstrator")
required.add_argument("-r","--region", nargs='+', help="AWS region for Cloud Volumes to join AD")
required.add_argument("-u","--username", nargs='+', help="username of AD admininstrator")

args = parser.parse_args()

if args.config:
	if len(args.config)!=1:
		print('a config file is required')
		sys.exit(1)
else:
	print('a config file is required')
	sys.exit(1)

if args.DNS:
	if len(args.DNS)!=1:
		print('a IP address for DNS is required')
		sys.exit(1)
else:
	print('a IP address for DNS is required')
	sys.exit(1)

if args.domain:
	if len(args.domain)!=1:
		print('a domain is required')
		sys.exit(1)
else:
	print('a domain is required')
	sys.exit(1)

if args.netbios:
	if len(args.netbios)!=1:
		print('a netbios name is required')
		sys.exit(1)
else:
	print('a netbios name is required')
	sys.exit(1)

if args.organizationalUnit:
	if len(args.organizationalUnit)!=1:
		print('an OU is required such as OU=ManagedAD')
		sys.exit(1)
else:
	args.organizationalUnit = ['CN=Computers']

if args.password:
	if len(args.password)!=1:
		print('a password for an AD admininstrator is required')
		sys.exit(1)
else:
	print('a password for an AD admininstrator is required')
	sys.exit(1)

if args.region:
	if (args.region)[0] != 'us-east-1' and (args.region)[0] != 'us-west-1' and (args.region)[0] != 'us-west-2' and (args.region)[0] != 'eu-central-1' and (args.region)[0] != 'eu-west-1' and (args.region)[0] != 'eu-west-2' and (args.region)[0] != 'ap-northeast-1' and (args.region)[0] != 'ap-southeast-2':
		print('Please select an available region')
		sys.exit(1)	
else:
	print('Please select an available region')
	sys.exit(1)

if args.username:
	if len(args.username)!=1:
		print('a username is required')
		sys.exit(1)
else:
	print('a username is required')
	sys.exit(1)

conf=args.config[0]
file = open(conf, 'r')

# read config file for keys and api endpoint
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

command = 'Storage/ActiveDirectory'
url = url+command

# Join AD 
def join(url, data, head):
	url = url
	data_json = json.dumps(data)
	req = requests.post(url, headers = head, data = data_json)
	details = json.dumps(req.json(), indent=4)
#	print('Joined AD in region ' + region [0])
	print(highlight(details, JsonLexer(), TerminalFormatter()))

data = {
	"DNS": args.DNS[0],
	"domain": args.domain[0],
	"netBIOS": args.netbios[0],
	"organizationalUnit": args.organizationalUnit[0],
	"password": args.password[0],
	"region": args.region[0],
	"username": args.username[0]
		}

join(url, data, head)
