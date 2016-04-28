#! /bin/bash


while read line
do

output=`echo "$line" | /home/vmsanchez/hybridmt/tools/local/bin/apertium -u  $1`
echo "$output"

done


