#! /bin/bash

# script to find NetApp Cloud Volumes Service fileSystemId by mountpoint
# Written by Graham Smith, NetApp July 2018
# requires bash, jq and curl
# Version 0.0.1

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

# get filesystem info
filesystems=$(curl -s -H accept:application/json -H "Content-type: application/json" -H api-key:$apikey -H secret-key:$secretkey -X GET $url/FileSystems)

# get filesystemIds
ids=$(echo $filesystems |jq -r ''|grep fileSystemId |cut -d '"' -f 4)

if [ "${#ids}" == "0" ]; then
	echo "Please check that the apikey and secretkey are valid"
	exit
fi

# Find matching filesystemId
fileSystemId=$(echo $filesystems |jq -r ''| grep -i -B 10 $m |grep fileSystemId | cut -d '"' -f 4)

if [ "${#fileSystemId}" == "0" ]; then
	echo "Please check the mountpoint is correct"
	exit
fi

echo -n "The fileSystemId for "$m" is :" 
echo $fileSystemId


