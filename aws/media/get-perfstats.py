#!/usr/bin/env python3
import requests
import json
import sys
from datetime import datetime, timedelta
import argparse
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

parser = argparse.ArgumentParser()
parser.add_argument("-c","--config", nargs='+', help="config file")
parser.add_argument("-m","--mountpoint", nargs='+', help="mountpoint")
parser.add_argument("-ld","--last_N_days", nargs='+', help="get stats for the last N days")
parser.add_argument("-lh","--last_N_hours", nargs='+', help="get stats for the last N hours")
parser.add_argument("-lm","--last_N_mins", nargs='+', help="get stats for the last N minutes")
parser.add_argument("-r","--timerange", nargs='+', help="start and end time in YYYY-MM-DDTHH:MM format")
parser.add_argument("-s","--stats", nargs='+', help="optionally select latency, iops or throughput")

args = parser.parse_args()

format = "%Y-%m-%dT%H:%M"
stats = "TOTAL_IOPS,TOTAL_THROUGHPUT,AVERAGE_READ_LATENCY,AVERAGE_WRITE_LATENCY"

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

if args.timerange:
	starttime = args.timerange[0]
	endtime = args.timerange[1]

if args.last_N_days:
	if int(args.last_N_days[0]) > 31:
		print('Maximum date range is 31 days')
		sys.exit(1)
	else:
		endtime = (datetime.utcnow().strftime(format))
		past = int(args.last_N_days[0])
		starttime = ((datetime.utcnow() - timedelta(days=past)).strftime(format))

if args.last_N_hours:
	endtime = (datetime.utcnow().strftime(format))
	past = int(args.last_N_hours[0])
	starttime = ((datetime.utcnow() - timedelta(hours=past)).strftime(format))

if args.last_N_mins:
	if int(args.last_N_mins[0]) < 5:
		print('Minimum update period in 5 minutes')
		sys.exit(1)
	else:
		endtime = (datetime.utcnow().strftime(format))
		past = int(args.last_N_mins[0])
		starttime = ((datetime.utcnow() - timedelta(minutes=past)).strftime(format))
	
if args.stats:
	if args.stats[0] == 'latency':
		stats = "AVERAGE_READ_LATENCY,AVERAGE_WRITE_LATENCY"
	elif args.stats[0] == 'iops':
		stats = "READ_IOPS,WRITE_IOPS,TOTAL_IOPS"	
	elif args.stats[0] == 'throughput':
		stats = "READ_THROUGHPUT,WRITE_THROUGHPUT,TOTAL_THROUGHPUT"	
	else:
		print('Argument for -s should be latency, iops or throughput')
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
timerange = 'startDate='+starttime+'&endDate='+endtime

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
	url = url+'/'+volid+'/PerformanceMetrics?'+timerange+'&type='+stats
	req = requests.get(url, headers = head)
	details = json.dumps(req.json(), indent=4)
	print('Performance stats '+args.mountpoint[0])
	print(highlight(details, JsonLexer(), TerminalFormatter()))


getsnaps(volid, url, head)


