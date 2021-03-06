#!/bin/bash

# bash script to test if an ASN matches existing VPG or DXG gateway in an AWS account
# Requires that aws cli installed and 'aws configure' has been completed
# Written by Graham Smith of NetApp, April 2019

if [ $# -lt 2 ] || [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    echo "Usage: test-asn.sh ASN region"
    echo
    exit 0
fi

asn=$1
region=$2

vpg=$(aws ec2 describe-vpn-gateways --region $region --filter  Name=amazon-side-asn,Values=$asn --output=json |grep VpnGatewayId |cut -d ":" -f 2)
dcx=$(aws directconnect --region $region describe-direct-connect-gateways --output=json |grep -B4 $1 |grep directConnectGatewayId |cut -d ":" -f 2)
account=$(aws sts get-caller-identity --output text --query 'Account' --output=json)

echo
echo "For account:" $account
echo -n $(echo $vpg | wc -w) "Matching Virtual Private Gateway(s) with ASN" $1 ": "
echo $vpg

echo -n $(echo $dcx | wc -w) "Matching Direct Connect Gateway(s) with ASN" $1 ": "
echo $dcx
