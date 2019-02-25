#! /bin/bash

# script to list the NetApp Cloud Volumes in an account
# Written by Graham Smith, NetApp Jan 2019
# requires bash, jq (optional), and curl
# Version 0.2

#set -x

usage() { echo "Usage: $0 [-c <config-file>]" 1>&2; exit 1; }

while getopts ":m:c:" o; do
    case "${o}" in
        c)
            c=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

if [ -z "${c}" ]; then
    usage
fi

source $c

# get filesystem info
filesystems=$(curl -s -H accept:application/json -H "Content-type: application/json" -H api-key:$apikey -H secret-key:$secretkey -X GET $url/FileSystems)

# Show info

if [ $(command -v jq) ]; then
	echo $filesystems |jq -r ''
else
	echo $filesystems
fi

