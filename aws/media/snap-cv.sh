#! /bin/bash

# script to create a snapshot of a NetApp Cloud Volume by mountpoint
# Written by Graham Smith, NetApp January 2019
# requires bash, jq and curl
# Version 0.2

#set -x

usage() { echo "Usage: $0 [-m <mountpoint> ] [-c <config-file>]" 1>&2; exit 1; }

while getopts ":m:c:" o; do
    case "${o}" in
        m)
            m=${OPTARG}
            ;;
        c)
            c=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

if [ -z "${m}" ] || [ -z "${c}" ]; then
    usage
fi

source $c

time=$(date +%Y%m%d%H%M%S)

# get filesystem info
filesystems=$(curl -s -H accept:application/json -H "Content-type: application/json" -H api-key:$apikey -H secret-key:$secretkey -X GET $url/FileSystems)

# get filesystemIds
ids=$(echo $filesystems |jq -r ''|grep fileSystemId |cut -d '"' -f 4)

if [ "${#ids}" == "0" ]; then
	echo "Please check that the apikey and secretkey are valid"
	exit 0
fi

# get region
region=$(echo $filesystems |jq -r '' | grep -i -A 10 $m |grep region |cut -d '"' -f 4)
echo $region

# Find matching filesystemId
fileSystemId=$(echo $filesystems |jq -r ''| grep -i -B 10 $m |grep fileSystemId | cut -d '"' -f 4)

if [ "${#fileSystemId}" == "0" ]; then
	echo "Please check the mountpoint is correct"
	exit
fi

# Create snapshot
curl -s -H accept:application/json -H "Content-type: application/json" -H api-key:$apikey -H secret-key:$secretkey -X POST $url/FileSystems/$fileSystemId/Snapshots -d '{"name": "snap_'$time'","region": "'$region'"}' |jq -r '' 
