#!/usr/bin/env python3
import sys
import boto3
import argparse
import ipaddress

''' 
Written by Graham Smith, NetApp June 2019
Checks if a CIDR is private and if it overlaps an existing CIDR in an AWS account
Version 0.4
''' 

parser = argparse.ArgumentParser()
required = parser.add_argument_group('Required')
optional = parser.add_argument_group('Optional')
required.add_argument("-c","--cidr", nargs='+', help="a private (RFC1918) /28 CIDR is required")
optional.add_argument("-k","--keys", nargs=2, help="Access key, then Secret key. Optional, will use credentials file if not specified here")
args = parser.parse_args()

if args.cidr:
	if len(args.cidr)!=1:
		print('an CIDR is required')
		parser.print_help()
		sys.exit(1)
else:
	print('an CIDR is required')
	parser.print_help()
	sys.exit(1)

cidr = ipaddress.ip_network(args.cidr[0])
if cidr.is_private == False or str(cidr) == '0.0.0.0/0':
	print('Please enter a private (RFC1918) CIDR')
	print()
	print('The IP spaces for private internets are, 10.0.0.0-10.255.255.255, 172.16.0.0-172.31.255.255 and 192.168.0.0-192.168.255.255')
	print()
	print('Please see https://tools.ietf.org/html/rfc1918')
	sys.exit(1)

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

clashes = 0

# Find CIDRs in AWS VPCs and check for clashes
print('Checking in each region if ' +str(cidr) + ' overlaps existing CIDRs')
regions = [region['RegionName'] for region in ec2.describe_regions()['Regions']]
for region in regions:
	print(region + '                 ', end="\r")
	ec2 = boto3.client('ec2',region_name=region)
	response = ec2.describe_vpcs()
	resp = response['Vpcs']
	for v in range(0, len(resp)):
		p = (str(resp[v]))
		p = p.split(':')[1]
		p = p.split("'")[1]
		n1 = ipaddress.ip_network(p)
		try:
			n2 = ipaddress.ip_network(cidr)
		except ValueError:
			print('CIDR ' + str(cidr) + ' is not valid')
			sys.exit(1)
		if n1.overlaps(n2):
			print(str(cidr)+' overlaps with ' + (str(p)) + ' in region ' + (str(region)))
			clashes += 1

# Report clashes
if clashes == 0:
	print(str(cidr) + ' does not overlap existing CIDRs in your account')
else:
	print(str(cidr) + ' overlaps in ' + str(clashes) + ' existing VPCs')						
