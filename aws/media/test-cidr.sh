#!/bin/bash

# bash script to test if a CIDR range clashes with existing ranges in an AWS account
# Requires that aws cli and nmap are installed and 'aws configure' has been completed
# Written by Graham Smith of NetApp, April 2019

# version 2

run=true
messages=""
VALID='(((25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?))(\/([8-9]|[1-2][0-9]|3[0-2]))([^0-9.]|$)'

if [ $# -lt 1 ] || [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    messages+=" Usage: test-cidr.sh CIDR \n\b"
    run=false
fi

if ! [  -x "$(command -v nmap)" ]; then
	messages+=" Please install nmap \n\b"
	run=false
fi

if ! [  -x "$(command -v aws)" ]; then
	messages+=" Please install aws cli \n\b"
	run=false
fi

if ! echo $1 | grep -qP "$VALID"; then
	messages+="'$1' is not a valid CIDR \n\b"
	run=false
fi 

if [ $run == false ]; then
	echo -e $messages
	exit 0
fi

test=$(nmap -sL -n $1 | awk '/Nmap scan report/{print $NF}')
clash=0
account=$(aws sts get-caller-identity --output text --query 'Account' --output=json)

echo
echo "For account:" $account

for region in `aws ec2 --region us-east-1 describe-regions --output text | cut -f3`
do
	echo -ne "Checking region: $region\033[0K\r"

	cidrs=$(aws ec2 describe-subnets --region $region --query 'Subnets[].CidrBlock' --output text && aws ec2 describe-route-tables --region $region --query 'RouteTables[].Routes[].DestinationCidrBlock' --output text)
	for cidr in $cidrs
		do
			if [ "$cidr" != "0.0.0.0/0" ]; then
				compare=$(nmap -sL -n $cidr | awk '/Nmap scan report/{print $NF}')
				match=$(echo ${test[@]} ${compare[@]} | tr ' ' '\n' | sort | uniq -d)
				if [ "${#match}" -gt 0 ]; then 
					echo "Your CIDR" $1 "clashes with subnet" $cidr "in region" $region
					((clash+=1))
				fi
			fi
		done
done

echo -e "\033[2K"

if [ $clash -gt 0 ]; then
	echo "CIDR" $1 "clashes with" $clash "existing CIDRs in your AWS account"
else
	echo "CIDR" $1 "does not clash with existing CIDRs in your AWS account"
fi
