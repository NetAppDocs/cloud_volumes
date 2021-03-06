#! /bin/bash

# script to delete a snapshot of NetApp Cloud Volume by mountpoint and snapshotId
# Written by Graham Smith, NetApp July 2018
# requires bash, jq and curl
# Version 0.2

#set -x

usage() { echo "Usage: $0 [-m <mountpoint> ] [-s <snapshotId> ] [-c <config-file>]" 1>&2; exit 1; }

while getopts ":m:s:c:" o; do
    case "${o}" in
        m)
            m=${OPTARG}
            ;;
	s)
	    s=${OPTARG}
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

if [ -z "${m}" ] || [ -z "${s}" ] || [ -z "${c}" ]; then
    usage
fi

source $c

# get filesystem info
filesystems=$(curl -s -H accept:application/json -H "Content-type: application/json" -H api-key:$apikey -H secret-key:$secretkey -X GET $url/FileSystems)

# get filesystemIds
ids=$(echo $filesystems |jq -r ''|grep fileSystemId |cut -d '"' -f 4)

if [ "${#ids}" == "0" ]; then
	echo "Please check that the apikey and secretkey are valid"
	exit
fi

# Find matching filesystemId
fileSystemId=$(echo $filesystems |jq -r ''| grep -i -B 10 '"'$m'"' |grep fileSystemId | cut -d '"' -f 4)

if [ "${#fileSystemId}" == "0" ]; then
	echo "Please check the mountpoint is correct"
	exit
fi

# Delete snapshot
snapshot=$(curl -s -H accept:application/json -H "Content-type: application/json" -H api-key:$apikey -H secret-key:$secretkey -X DELETE $url/FileSystems/$fileSystemId/Snapshots/$s)

if [ "${#snapshot}" == "0" ]; then
	echo "Please check that the snapshot exists"
	exit
fi

echo $snapshot | jq 
