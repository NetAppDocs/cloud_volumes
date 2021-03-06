#! /bin/bash

# Script to clone a NetApp Cloud Volume
# Written by Graham Smith, NetApp July 2018
# requires bash, jq and curl
# Version 0.2

#set -x

usage() { echo "Usage: $0 [-n <name> ] [-m <mountpoint> ] [-N <new-mountpoint> ] [-r <region> ] [-l <standard|premium|extreme> ] [ -a allocated_size_in_GB (100 to 100000) ] [-e <export> ] [-w <ro|rw> ] [-p <nfs3|smb|nfs3smb> ] [-t <tag> (optional) ][-c <config-file>]" 1>&2; exit 1; }

while getopts ":n:m:N:r:l:a:e:w:p:s:t:c:" o; do
    case "${o}" in
        n)
		    n=${OPTARG}
            ;;
        m)
            m=${OPTARG}
            ;;
        N)
            N=${OPTARG}
            ;;
		r)
		    r=${OPTARG}
            ;;
		l)
		    l=${OPTARG}
            ;;
		a)
		    a=${OPTARG}
            ;;
        e)
		    e=${OPTARG}
            ;;
        w)
		    w=${OPTARG}
            ;;
        p)
		    p=${OPTARG}
            ;;
        t)
            t=${OPTARG}
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

if [ -z "${n}" ] || [ -z "${m}" ] || [ -z "${r}" ] || [ -z "${l}" ] || [ -z "${a}" ] || [ -z "${w}" ] || [ -z "${p}" ] || [ -z "${c}" ]; then
    usage
fi

source $c

time=$(date +%Y%m%d%H%M%S)

#if [ $r != "us-east" ] && [ $r != "us-west" ]; then
#    usage
#fi

# get filesystem info
filesystems=$(curl -s -H accept:application/json -H "Content-type: application/json" -H api-key:$apikey -H secret-key:$secretkey -X GET $url/FileSystems)

# get filesystemIds
ids=$(echo $filesystems |jq -r ''|grep fileSystemId |cut -d '"' -f 4)

if [ "${#ids}" == "0" ]; then
	echo "Please check that the apikey and secretkey are valid"
	exit 0
fi

# Find matching filesystemId
fileSystemId=$(echo $filesystems |jq -r ''| grep -i -B 10 '"creationToken": "'$m'"''' |grep fileSystemId | cut -d '"' -f 4)
echo $fileSystemId

if [ "${#fileSystemId}" == "0" ]; then
	echo "Please check the mountpoint is correct"
	exit
fi

if [ $l != "standard" ] && [ $l != "premium" ] && [ $l != "extreme" ]; then
    usage
fi

if [ $l = "standard" ]; then
    l=basic
fi

if [ $l = "premium" ]; then
    l=standard
fi

if [[ $a != ?(-)+([0-9]) ]]; then
    usage
fi

if (( $a < 100 || $a > 1000000 )); then
    usage
fi

a=$((a*1000000000))

if [ -z "$e" ];then
    e="0.0.0.0/0"
#add check for valid CIDR
fi

if [ $w != "ro" ] && [ $w != "rw" ]; then
    usage
elif [ $w == "ro" ];then
    ro=true;rw=false
else  ro=false;rw=true
fi

if [ $p == "nfs3" ];then
    nfs3=true;cifs=false
elif [ $p == "smb" ];then
    nfs3=false;cifs=true
elif [ $p == "nfs3smb" ];then
    nfs3=true;cifs=true
else usage
fi

# Create snapshot
s=$(curl -s -H accept:application/json -H "Content-type: application/json" -H api-key:$apikey -H secret-key:$secretkey -X POST $url/FileSystems/$fileSystemId/Snapshots -d '{"name": "snap_'$time'","region": "'$r'"}' |jq -r '' |grep snapshotId | cut -d '"' -f 4)
echo "Created snapshot" $s

sleep 60

# Create volume
volume=$(curl -s -H accept:application/json -H "Content-type: application/json" -H api-key:$apikey -H secret-key:$secretkey -X POST $url/FileSystems -d '
{"name": "'$n'",
"creationToken": "'$N'",
"region": "'$r'",
"serviceLevel": "'$l'",
"quotaInBytes": '$a',
"exportPolicy": {"rules": [{"ruleIndex": 1,"allowedClients":"'$e'","unixReadOnly": '$ro',"unixReadWrite": '$rw',"cifs": '$cifs',"nfsv3": '$nfs3',"nfsv4": false}]},
"snapshotId": "'$s'",
"labels": ["'$t'"]}'
)

echo $volume | jq 

# the wait should not be needed when we use unsplit flexclone
echo 
echo "waiting 60 seconds"
sleep 60

# Delete snapshot
curl -s -H accept:application/json -H "Content-type: application/json" -H api-key:$apikey -H secret-key:$secretkey -X DELETE $url/v1/FileSystems/$fileSystemId/Snapshots/$s > /dev/null 2>&1
echo "Deleted snapshot" $s

exit

