#! /bin/bash

# Script to create a NetApp Cloud Volume
# Written by Graham Smith, NetApp Jan 2018
# requires bash, jq (optional) and curl
# Version 0.2

#set -x

usage() { echo "Usage: $0 [-n <name> ] [-m <mountpoint> ] [-r <region> ] [-l <standard|premium|extreme> ] [ -a allocated_size_in_GB (100 to 100000) ] [-e <export> ] [-w <ro|rw> ] [-p <nfs3|smb|nfs3smb> ] [ -s <snapshotId> (optional) ] [-t <tag> (optional) ][-c <config-file>]" 1>&2; exit 1; }

while getopts ":n:m:r:l:a:e:w:p:s:t:c:" o; do
    case "${o}" in
        n)
		    n=${OPTARG}
            ;;
        m)
            m=${OPTARG}
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
        s)
            t=${OPTARG}
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

#if [ $r != "us-east" ] && [ $r != "us-west" ]; then
#    usage
#fi

if [ $l != "standard" ] && [ $l != "premium" ] && [ $l != "extreme" ]; then
    usage
fi

if [ $l = "standard" ]; then
    l=basic
fi

if [ $l = "premium" ]; then
    l=standard
fi

#if [[ $a != ?(-)+([0-9]) ]]; then
#    usage
#fi

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

source $c

# Create volume
volume=$(curl -s -H accept:application/json -H "Content-type: application/json" -H api-key:$apikey -H secret-key:$secretkey -X POST $url/FileSystems -d '
{"name": "'$n'",
"creationToken": "'$m'",
"region": "'$r'",
"serviceLevel": "'$l'",
"quotaInBytes": '$a',
"exportPolicy": {"rules": [{"ruleIndex": 1,"allowedClients":"'$e'","unixReadOnly": '$ro',"unixReadWrite": '$rw',"cifs": '$cifs',"nfsv3": '$nfs3',"nfsv4": false}]},
"snapshotId": "'$s'",
"labels": ["'$t'"]}'
)

# Show info

if [ $(command -v jq) ]; then
	echo $volume |jq -r ''
else
	echo $volume
fi

