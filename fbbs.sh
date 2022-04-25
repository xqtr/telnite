#!/bin/bash

if [[ ! -f "/tmp/bbslist.csv" ]]
then
    wget https://www.telnetbbsguide.com/bbslist/bbslist.csv -O /tmp/bbslist.csv
fi

bbs="$(cat /tmp/bbslist.csv | fzf -e -i)"

if [[ ! -z "${bbs// }" ]]
then
    address=$(echo $bbs | cut -d"," -f4)
    port=$(echo $bbs | cut -d"," -f5)
    if [[ -z "${port// }" ]]
    then
       port=23
    fi
    echo "Connecting to: $address:$port..."
    ./telnite.py $address:$port
fi
