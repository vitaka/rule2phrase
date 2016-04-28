#! /bin/bash


while read line
do

output=`echo "$line" | /home/vmsanchez/hybridmt/tools/local/bin/apertium   $1`
echo "$output"

done


