#!/usr/bin/env python3

import sys
import boto3
import argparse

''' 
Written by Graham Smith, NetApp June 2019
Checks if a ASN matches and gateway in an AWS account
Version 0.4
''' 

parser = argparse.ArgumentParser()
required = parser.add_argument_group('Required')
optional = parser.add_argument_group('Optional')
required.add_argument("-a","--asn", nargs='+', help="an ASN is required")
optional.add_argument("-d","--details", help="Optional, list gateway details",action="store_true")
optional.add_argument("-k","--keys", nargs=2, help="Access key, then Secret key. Optional, will use credentials file if not specified here")
args = parser.parse_args()

if args.asn:
	if len(args.asn)!=1:
		print('an ASN is required')
		parser.print_help()
		sys.exit(1)
else:
	print('an ASN is required')
	parser.print_help()
	sys.exit(1)

asn = args.asn[0]

if args.keys:
	access = args.keys[0]
	secret = args.keys[1]
	ec2 = boto3.client(
	'ec2',
    aws_access_key_id=access,
    aws_secret_access_key=secret
	)
else:
	ec2 = boto3.client('ec2')

# Get AWS account ID
iam = boto3.resource('iam')
print('For account: ' + str(iam.CurrentUser().arn.split(':')[4]))

regions = [region['RegionName'] for region in ec2.describe_regions()['Regions']]
match = []

print('Checking for gateways that match ASN ' + str(asn))
for region in regions:
	print(region + '                 ', end="\r")

	ec2 = boto3.client('ec2', region_name=region)
	response = ec2.describe_vpn_gateways(
	    Filters=[
	        {
	            'Name': 'amazon-side-asn',
	            'Values': [asn,]
	        },
	    ]
	)
	for keys,values in response.items():
		if keys == 'VpnGateways':
			if (len(values)) > 0:
				if args.details:
					print(region)
					print(values)
				match.append(region)

if (len(match)) > 0:
	print('Virtual private gateway(s) with ASN of ' +str(asn) + ' in region(s) ' + str(match))
else:
	print('No virtual private gateways found with ASN of ' +str(asn))

dx = boto3.client('directconnect')
response = dx.describe_direct_connect_gateways()
dxg = (response['directConnectGateways'])
if (asn) in str(dxg):
	print('Direct connect gateway found with ASN of ' +str(asn))
	if args.details:
		print(dxg)
else:
	print('No direct connect gateways found with ASN of ' +str(asn))
