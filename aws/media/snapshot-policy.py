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
parser.add_argument("-hm","--hourly_minute", type=int, help="minute for hourly snapshot") 
parser.add_argument("-hr","--hourly_retention", type=int, help="number of hourly snapshots to keep")
parser.add_argument("-dm","--daily_minute", type=int, help="minute for daily snapshot")
parser.add_argument("-dh","--daily_hour", type=int, help="minute for daily snapshot")
parser.add_argument("-dr","--daily_retention", type=int, help="number of daily snapshots to keep")
parser.add_argument("-wd","--weekly_days", type=str, help="days of week 'Monday,Wednesday' etc.")
parser.add_argument("-wm","--weekly_minute", type=int, help="minute for weekly snapshot")
parser.add_argument("-wh","--weekly_hour", type=int, help="minute for weekly snapshot")
parser.add_argument("-wr","--weekly_retention", type=int, help="number of weekly snapshots to keep")
parser.add_argument("-md","--monthly_days", type=str, help="days of month '1, 15, 30' etc.")
parser.add_argument("-mm","--monthly_minute", type=int, help="minute for monthly snapshot")
parser.add_argument("-mh","--monthly_hour", type=int, help="minute for monthly snapshot")
parser.add_argument("-mr","--monthly_retention", type=int, help="number of monthly snapshots to keep")

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

# update volume 
def update(volid, url, data, head):
	url = url+'/'+volid
	data_json = json.dumps(data)
	req = requests.put(url, headers = head, data = data_json)
	details = json.dumps(req.json(), indent=4)
	print('Updated snapshot policy for volume '+args.mountpoint[0])
	print(highlight(details, JsonLexer(), TerminalFormatter()))

data = {
	"creationToken": args.mountpoint[0],
	"region": region,
	"snapshotPolicy": {
        "hourlySchedule": {
            "minute": args.hourly_minute,
            "snapshotsToKeep": args.hourly_retention
		        },
        "dailySchedule": {
            "hour": args.daily_hour,
            "minute": args.daily_minute,
            "snapshotsToKeep": args.daily_retention
		        },
        "enabled": True,
        "weeklySchedule": {
            "day": args.weekly_days,
            "hour": args.weekly_hour,
            "minute": args.weekly_minute,
            "snapshotsToKeep": args.weekly_retention
				},
        "monthlySchedule": {
            "daysOfMonth": args.monthly_days,
            "hour": args.monthly_hour,
            "minute": args.monthly_minute,
            "snapshotsToKeep": args.monthly_retention
		        }
			}
		}

update(volid, url, data, head)
