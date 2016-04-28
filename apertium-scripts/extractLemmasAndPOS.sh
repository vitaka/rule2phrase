# !/bin/bash

# Extracts lemmas and part-of-speech tags from an Apertium monolingual dictionary
# Creates a file for each PoS with all its lemmas
#Creates another file with the lexical forms which generate/come from multiword surface forms

# $1 : Apertium bin directory
# $2 : Dictionary file
# $3 : Directory where the extracted lemmas will be stored
# $4 : Apertium scripts directory
# $5 : "analysis" for analysis multiwords; "generation" for generation multiwords. Default is analysis

DEFAULTMW="analysis"

MW=${5:-$DEFAULTMW}

mkdir -p $3

#this command writes lemmas and multi-word units in corresponding files. Afterwards, we will need to adapt the format
$1/lt-expand "$2" |  LC_ALL=C sort -u  | python $4/extractLemmasAndPOSv2.py "$3" "$MW"

#adapt the format of lemmas file
zcat $3/lemmas-pre.gz | LC_ALL=C sort -k1,1 -t '	' | python -c '
import sys
prevGroup=""
for line in sys.stdin:
	line=line.rstrip("\n")
	parts=line.split("\t")
	mygroup=parts[0]
	if mygroup != prevGroup:
		print mygroup
	print parts[1]
	prevGroup=mygroup
' | gzip> $3/lemmas.gz

#adapt the format of multi-word file
zcat $3/multiwords-pre.gz | LC_ALL=C sort -k1,1 -t '	' | python -c '
import sys
prevGroup=""
for line in sys.stdin:
	line=line.rstrip("\n")
	parts=line.split("\t")
	mygroup=parts[0]
	if mygroup != prevGroup:
		print mygroup
	print parts[1]
	prevGroup=mygroup
' > $3/multiword
