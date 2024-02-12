#! /bin/bash

# script to create a snapshot of a NetApp Cloud Volume by mountpoint
# Written by Graham Smith, NetApp Feb 2019
# requires bash, jq and curl
# Version 0.3

#set -x

usage() { echo "Usage: $0 [-m <mountpoint>,<mountpoint>] [-c <config-file>]" 1>&2; exit 1; }

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

# Create snapshot(s)
function snap () {
	region=$(echo $filesystems |jq -r '' | grep -i -A 10 $f |grep region |cut -d '"' -f 4)
	time=$(date +%Y%m%d%H%M%S%N)
	snap=$(curl -s -H accept:application/json -H "Content-type: application/json" -H api-key:$apikey -H secret-key:$secretkey -X POST $url/FileSystems/$f/Snapshots -d '{"name": "snap_'$time'","region": "'$region'"}' )
}

vols=$(echo $m |grep -o , | wc -l)
let "vols=vols+1"

if [  $vols -ge 11 ]; then
	echo "Too many volumes, please select up to 10 volumes"
	exit 1
fi

fsids=()

# get filesystem info
filesystems=$(curl -s -H accept:application/json -H "Content-type: application/json" -H api-key:$apikey -H secret-key:$secretkey -X GET $url/FileSystems)

# get filesystemIds
ids=$(echo $filesystems |jq -r ''|grep fileSystemId |cut -d '"' -f 4)

if [ "${#ids}" == "0" ]; then
	echo "Please check that the apikey and secretkey are valid"
	exit 1
fi

while [ $vols -ge 1 ]
do 
	v=$(echo $m | cut -d ',' -f $vols)
	fileSystemId=$(echo $filesystems |jq -r ''| grep -i -B 10 '"'$v'"' |grep fileSystemId | cut -d '"' -f 4)
	if [ "${#fileSystemId}" == "0" ]; then
		echo "Please check the mountpoint" '"'$v'"' "is correct"
		exit 1
	fi
	fsids+=($fileSystemId)
	let "vols=vols-1"
done

for f in "${fsids[@]}"
do
	snap $f
	if [ $(echo $snap | grep Error) ]; then
		echo 'Error, retrying..'
		sleep 5
		snap $f
	fi 	
	echo $snap | jq -r ''
done
