# /bin/bash

SRC_DEF=es
TARGET_DEF=pt
PAIR_DEF=es-pt

SRC=${1:-$SRC_DEF}
TARGET=${2:-$TARGET_DEF}
PAIR=${3:-$PAIR_DEF}
DIR=$4
SRCDICTIONARY=$5
APERTIUMBINDIR=$6
MYSCRIPTSDIR=$7
TOKENIZER=$8
TARGETMULTIWORDS=$9

LEARNEDFLAG="${12}"

TRUELOWERCASECMDSL="${13}"
TRUELOWERCASECMDTL="${14}"

WRITETLMORPH="${15}"

#if ${12} == "empty", use empty rules to generate corpus from dictionary

#DIR=/work2/vmsanchez/hybridmt/common/dictionary$4-$SRC-$TARGET

mkdir -p $DIR
$APERTIUMBINDIR/lt-expand $SRCDICTIONARY  | LC_ALL=C  sort | uniq  | split -l 10000 - $DIR/split_

rm -f $DIR/dictcorpus.all

echo "Generating dictionary corpus $SRC - $TARGET $9"

for file in `ls $DIR/split_*`; do

echo "Processing $file"
echo "Running: cat $file |  python $MYSCRIPTSDIR/generateCorpusFromDictionary.py  $file.$SRC.upperprev $file.$TARGET.upperprev $file.als.dprev  $SRC $TARGET $TARGETMULTIWORDS ${10} ${11}"

if [ "$LEARNEDFLAG" != ""  ] ; then
echo "WARNING!! using a different apertium path to generate dictionaries. This is because there are two patches: one for executing learned rules with backtracking and another for tracing back operations"
cat $file | PATH=/home/vmsanchez/hybrid-thesis/local2/bin:$PATH  python $MYSCRIPTSDIR/generateCorpusFromDictionary.py  $file.$SRC.upperprev $file.$TARGET.upperprev $file.als.dprev  $SRC $TARGET $TARGETMULTIWORDS "${10}" "${11}" "$LEARNEDFLAG" "$TRUELOWERCASECMDSL" "$TRUELOWERCASECMDTL"
else
cat $file |  python $MYSCRIPTSDIR/generateCorpusFromDictionary.py  $file.$SRC.upperprev $file.$TARGET.upperprev $file.als.dprev  $SRC $TARGET $TARGETMULTIWORDS "${10}" "${11}" "$LEARNEDFLAG" "$WRITETLMORPH"
fi

TOKENIZERSL=`echo "$TOKENIZER" | cut -f 1 -d ';'`
TOKENIZERTL=`echo "$TOKENIZER" | cut -f 2 -d ';'`

#most of this code is useless
#cat  $file.$SRC.upperprev | python $MYSCRIPTSDIR/tokenizeWithALignments.py -l $SRC -p "$TOKENIZER" > $file.$SRC.upperplusals
#cat  $file.$TARGET.upperprev | python $MYSCRIPTSDIR/tokenizeWithALignments.py -l $TARGET -p "$TOKENIZER" > $file.$TARGET.upperplusals
#cat $file.$SRC.upperplusals | python $MYSCRIPTSDIR/cutPhraseTable.py -f 1 > $file.$SRC.upper
#cat $file.$TARGET.upperplusals | python $MYSCRIPTSDIR/cutPhraseTable.py -f 1 | sed -r "s:^([^/]*)/.*:\1:" > $file.$TARGET.upper
#cat $file.$SRC.upperplusals | python $MYSCRIPTSDIR/cutPhraseTable.py -f 2 > $file.$SRC.upperonlyals
#cat $file.$TARGET.upperplusals | python $MYSCRIPTSDIR/cutPhraseTable.py -f 2  > $file.$TARGET.upperonlyals
#python $MYSCRIPTSDIR/pastePhraseTable.py $file.$SRC.upperonlyals $file.als.dprev $file.$TARGET.upperonlyals | python $MYSCRIPTSDIR/joinAlignments.py > $file.als.d

echo "Tokeninzing $file.$SRC.upperprev with $TOKENIZERSL"
echo "Tokeninzing $file.$TARGET.upperprev with $TOKENIZERTL"


CMD1="cat  $file.$SRC.upperprev  | $TOKENIZERSL > $file.$SRC.upper"
eval $CMD1

CMD2="cat  $file.$TARGET.upperprev  | $TOKENIZERTL | sed -r 's:^([^/]*)/.*:\1:' > $file.$TARGET.upper"
eval $CMD2

$TRUELOWERCASECMDSL <$file.$SRC.upper | sed -r "s/[ ]+/ /g" >$file.$SRC.d
$TRUELOWERCASECMDTL  <$file.$TARGET.upper| sed -r "s/[ ]+/ /g" >$file.$TARGET.d

#python $MYSCRIPTSDIR/pastePhraseTable.py  $file.$SRC.d $file.$TARGET.d $file.als.d >> $DIR/dictcorpus.all
python $MYSCRIPTSDIR/pastePhraseTable.py  $file.$SRC.d $file.$TARGET.d >> $DIR/dictcorpus.all

done

#cat $DIR/dictcorpus.all | LC_ALL=C sort | uniq | grep -E "^.*[^ ].* \|\|\| .*[^ ].* \|\|\|" | python $MYSCRIPTSDIR/filterEmptyPhrases.py -f 1,2 >$DIR/dictcorpus.nodup

#Remove errors from dictionary
cat $DIR/dictcorpus.all | LC_ALL=C sort -u |  grep -E "^.*[^ ].* \|\|\| .*[^ ].*" | python $MYSCRIPTSDIR/filterEmptyPhrases.py -f 1,2 | egrep -v '\|\|\| .*[#@].*' >$DIR/dictcorpus.nodup

python $MYSCRIPTSDIR/cutPhraseTable.py -f 1 <$DIR/dictcorpus.nodup > $DIR/dictcorpus.$SRC
python $MYSCRIPTSDIR/cutPhraseTable.py -f 2 <$DIR/dictcorpus.nodup > $DIR/dictcorpus.$TARGET
#python $MYSCRIPTSDIR/cutPhraseTable.py -f 3 <$DIR/dictcorpus.nodup > $DIR/dictcorpus.als

python $MYSCRIPTSDIR/cutPhraseTable.py -f 1,2 < $DIR/dictcorpus.nodup | sed -r 's/$/ |||/' | LC_ALL=C sort -u  | gzip > $DIR/dictcorpus.gz

#rm $DIR/split_*
#rm $DIR/dictsplit_*
