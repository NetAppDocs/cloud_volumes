#!/usr/bin/env python3
import requests
import json
import argparse
import sys
import os
import csv
import datetime
#from pygments import highlight
#from pygments.lexers import JsonLexer
#from pygments.formatters import TerminalFormatter

parser = argparse.ArgumentParser()
parser.add_argument("-c","--config", nargs='+', help="path to .conf config files")
parser.add_argument("-o","--output", nargs='+', help="name of output file for summary")
args = parser.parse_args()

if args.config:
	if len(args.config)!=1:
		print('a path to the config file(s) is required')
		sys.exit(1)
else:
	parser.print_help()	
	sys.exit(1)

if args.output:
	if len(args.output)!=1:
		print('the name of output file is required')
		sys.exit(1)
	else:
		output = args.output[0]
else:
	parser.print_help()
	sys.exit(1)

standard={}
premium={}
extreme={}
used_standard={}
used_premium={}
used_extreme={}
volumes={}

time=(datetime.datetime.now())

price_standard=0.10
price_premium=0.20
price_extreme=0.30

# read config files for keys and api endpoint
def config(file):
	for line in file:
		if 'apikey' in line:
			apikey=(line.split("=")[1].rstrip('\n'))
		if 'secretkey' in line:
			secretkey=(line.split("=")[1].rstrip('\n'))
		if 'url' in line:
			url=str(line.split("=")[1].rstrip('\n'))
	# create header
	headers = {}
	headers['api-key'] = apikey
	headers['secret-key'] = secretkey
	headers['content-type'] = 'application/json'
	command = 'FileSystems'
	url = url+command
	# get filesystems
	req = requests.get(url, headers = headers)
	if req.status_code != 200:
		print("Please check the config file")
		print(req)
		sys.exit(1)
	vols=(len(req.json()))
	for vol in range(0, vols):
		mountpoint=((req.json()[vol])['creationToken'])
		allocated=(((req.json()[vol])['quotaInBytes'])/1000000000)
		used=(((req.json()[vol])['usedBytes'])/1000000000)
		if used > allocated:
			print("Suggest increasing allocation on volume: " + (str(mountpoint)))
		service_level=((req.json()[vol])['serviceLevel'])
		if ((req.json()[vol])['serviceLevel']) == 'extreme':
			extreme.update({mountpoint:allocated})
			used_extreme.update({mountpoint:used})
		if ((req.json()[vol])['serviceLevel']) == 'premium':
			premium.update({mountpoint:allocated})
			used_premium.update({mountpoint:used})
			service_level='premium'
		if ((req.json()[vol])['serviceLevel']) == 'standard':
			standard.update({mountpoint:allocated})
			used_standard.update({mountpoint:used})
			service_level='standard'
		print("mountpoint: " + (str(mountpoint)) + ", GB allocated: " + (str(round(allocated))) + ",level: " + service_level + ", GB used: " + (str(round(used,3))))

path = args.config[0]

for f in os.listdir(path):
	if f.endswith(".conf"):
		print()
		print(f)
		file = open(f, 'r')
		config(file)

total_volumes=(len(standard))+(len(premium))+(len(extreme))

standard_allocated=(round(sum(standard.values()),3))
standard_used=(round(sum(used_standard.values()),3))
if standard_allocated > standard_used:
	standard_cost = standard_allocated * price_standard
else:
	standard_cost = standard_used * price_standard

premium_allocated=(round(sum(premium.values()),3))
premium_used=(round(sum(used_premium.values()),3))
if premium_allocated > premium_used:
	premium_cost = premium_allocated * price_premium
else:
	premium_cost = premium_used * price_premium

extreme_allocated=(round(sum(extreme.values()),3))
extreme_used=(round(sum(used_extreme.values()),3))
if extreme_allocated > extreme_used:
	extreme_cost = extreme_allocated * price_extreme
else:
	extreme_cost = extreme_used * price_extreme

total_cost = (standard_cost + premium_cost + extreme_cost)

print()
print("Standard Service Level")
print("Volumes: " +(str(len(standard)))+ ", GB allocated: "+ (str(round(standard_allocated))) + ", GB used: " + (str(standard_used)))
print("Cost / Month: $" + (str(round(standard_cost,2))))
print()
print("Premium Service Level")
print("Volumes: " +(str(len(premium)))+ ", GB allocated: "+ (str(round(premium_allocated))) + ", GB used: " + (str(premium_used)))
print("Cost / Month: $" + (str(round(premium_cost,2))))
print()
print("Extreme Service Level")
print("Volumes: " +(str(len(extreme)))+ ", GB allocated: "+ (str(round(extreme_allocated))) + ", GB used: " + (str(extreme_used)))
print("Cost / Month: $" + (str(round(extreme_cost,2))))
total_volumes=(len(standard))+(len(premium))+(len(extreme))
print()
print("Combined Service Levels")
print("Volumes: "+(str(total_volumes))+", GB allocated: "+ (str(round(standard_allocated + premium_allocated + extreme_allocated))) + ", GB used: " + (str(round(standard_used + premium_used + extreme_used,3))))
print("Cost / Month: $" + (str(round(total_cost,2))))

if os.path.exists(output)==False:
	with open(output, 'a',newline='') as f:
		writer = csv.writer(f)
		writer.writerow(['timestamp','volumes','standard_allocated','standard_used','standard_cost','premium_allocated','premium_used','premium_cost','extreme_allocated','extreme_used','extreme_cost','total_cost'])


with open(output, 'a',newline='') as f:
    writer = csv.writer(f)
    writer.writerow([time,total_volumes,standard_allocated,standard_used,standard_cost,premium_allocated,premium_used,premium_cost,extreme_allocated,extreme_used,extreme_cost,total_cost])
