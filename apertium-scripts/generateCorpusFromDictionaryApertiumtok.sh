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
EXTRASCRIPTSDIR=$8
TARGETMULTIWORDS=$9

LEARNEDFLAG="${12}"

MYAPERTIUMPREFIX=/home/vmsanchez/hybrid-thesis/local


#if ${12} == "empty", use empty rules to generate corpus from dictionary

#DIR=/work2/vmsanchez/hybridmt/common/dictionary$4-$SRC-$TARGET

mkdir -p $DIR
$APERTIUMBINDIR/lt-expand $SRCDICTIONARY  | LC_ALL=C  sort | uniq  | split -l 10000 - $DIR/split_

rm -f $DIR/dictcorpus.all

echo "Generating dictionary corpus $SRC - $TARGET $9"

for file in `ls $DIR/split_*`; do

echo "Processing $file"
echo "Running: cat $file |  python $MYSCRIPTSDIR/generateCorpusFromDictionaryApertiumTok.py  $file.$SRC.upperprev $file.$TARGET.upperprev $file.als.dprev  $SRC $TARGET $TARGETMULTIWORDS ${10} ${11}"

if [ "$LEARNEDFLAG" != ""  ] ; then
cat $file | PATH=/home/vmsanchez/hybrid-thesis/local2/bin:$PATH  python $MYSCRIPTSDIR/generateCorpusFromDictionaryApertiumTok.py  $file.$SRC.upperprev $file.$TARGET.upperprev $file.als.dprev  $SRC $TARGET $TARGETMULTIWORDS "${10}" "${11}" "$LEARNEDFLAG"
else
cat $file |  python $MYSCRIPTSDIR/generateCorpusFromDictionaryApertiumTok.py  $file.$SRC.upperprev $file.$TARGET.upperprev $file.als.dprev  $SRC $TARGET $TARGETMULTIWORDS "${10}" "${11}" "$LEARNEDFLAG"
fi

#cat  $file.$SRC.upperprev | python $MYSCRIPTSDIR/tokenizeWithALignments.py -l $SRC > $file.$SRC.upperplusals
#cat  $file.$SRC.upperprev |  $MYAPERTIUMPREFIX/bin/apertium-destxt |  $MYAPERTIUMPREFIX/bin/lt-proc $MYAPERTIUMPREFIX/share/apertium/apertium-$PAIR/$SL-$TL.automorf.bin | $MYAPERTIUMPREFIX/bin/apertium-retxt  | sed '$ s:\^\./\.<sent>\$$::'    | paste - $file.$SRC.upperprev.additional  | python $MYSCRIPTSDIR/tokenizeWithApertiumAlignmentsSource.py  > $file.$SRC.upperplusals.preFranScript
#cat $file.$SRC.upperplusals.preFranScript | python $MYSCRIPTSDIR/cutPhraseTable.py -f 1 | python $MYSCRIPTSDIR/tagger-to-factored.py | sed -r 's:\|[^ |]+\|[^ |]+\|[^ |]+::g' >  $file.$SRC.upperplusals.postFranScript.onlysf
#cat $file.$SRC.upperplusals.preFranScript | python $MYSCRIPTSDIR/cutPhraseTable.py -f 2  >  $file.$SRC.upperplusals.preFranScript.onlyals
#python $MYSCRIPTSDIR/pastePhraseTable.py $file.$SRC.upperplusals.postFranScript.onlysf $file.$SRC.upperplusals.preFranScript.onlyals > $file.$SRC.upperplusals

cat $file.$SRC.upperprev | sed 's:^:^:' | sed 's:$:/dummy<dummy><dummy>$:' | python $MYSCRIPTSDIR/tagger-to-factored.py | sed -r 's:\|[^ |]+\|[^ |]+\|[^ |]+::g' | sed 's:$: ||| 1-1:' > $file.$SRC.upperplusals


#$file.$SRC.upperplusals

#cat  $file.$TARGET.upperprev | python $MYSCRIPTSDIR/tokenizeWithALignments.py -l $TARGET > $file.$TARGET.upperplusals
cat  $file.$TARGET.upperprev | sed 's:$: VMSANCHEZTHESISSEPARATOR:' |  $MYAPERTIUMPREFIX/bin/apertium-destxt |  $MYAPERTIUMPREFIX/bin/lt-proc $MYAPERTIUMPREFIX/share/apertium/apertium-$PAIR/$TL-$SL.automorf.bin | $MYAPERTIUMPREFIX/bin/apertium-retxt  | sed '$ s:\^\./\.<sent>\$$::'  | sed 's: \^VMSANCHEZTHESISSEPARATOR/\*VMSANCHEZTHESISSEPARATOR\$::' |  paste - $file.$TARGET.upperprev.additional | python $MYSCRIPTSDIR/tokenizeWithApertiumAlignmentsTarget.py  > $file.$TARGET.upperplusals.preFranScript

cat $file.$TARGET.upperplusals.preFranScript | python $MYSCRIPTSDIR/cutPhraseTable.py -f 1 | python $MYSCRIPTSDIR/tagger-to-factored.py | sed -r 's:\|[^ |]+\|[^ |]+\|[^ |]+::g' >  $file.$TARGET.upperplusals.postFranScript.onlysf
cat $file.$TARGET.upperplusals.preFranScript | python $MYSCRIPTSDIR/cutPhraseTable.py -f 2  >  $file.$TARGET.upperplusals.preFranScript.onlyals

python $MYSCRIPTSDIR/pastePhraseTable.py $file.$TARGET.upperplusals.postFranScript.onlysf $file.$TARGET.upperplusals.preFranScript.onlyals > $file.$TARGET.upperplusals


cat $file.$SRC.upperplusals | python $MYSCRIPTSDIR/cutPhraseTable.py -f 1 > $file.$SRC.upper
cat $file.$TARGET.upperplusals | python $MYSCRIPTSDIR/cutPhraseTable.py -f 1 | sed -r "s:^([^/]*)/.*:\1:" > $file.$TARGET.upper

cat $file.$SRC.upperplusals | python $MYSCRIPTSDIR/cutPhraseTable.py -f 2 > $file.$SRC.upperonlyals
cat $file.$TARGET.upperplusals | python $MYSCRIPTSDIR/cutPhraseTable.py -f 2  > $file.$TARGET.upperonlyals

#for some reaon, pretransfer alignments were ignored. this seems like a bug in the prev version. should I do the same
python $MYSCRIPTSDIR/pastePhraseTable.py $file.$SRC.upperonlyals $file.als.dprev $file.$TARGET.upperonlyals | python $MYSCRIPTSDIR/joinAlignmentsShort.py > $file.als.d

/home/vmsanchez/hybrid-thesis/tools/mosesdecoder/scripts/tokenizer/lowercase.perl   <$file.$SRC.upper | sed -r "s/[ ]+/ /g" >$file.$SRC.d
/home/vmsanchez/hybrid-thesis/tools/mosesdecoder/scripts/tokenizer/lowercase.perl  <$file.$TARGET.upper| sed -r "s/[ ]+/ /g" >$file.$TARGET.d

python $MYSCRIPTSDIR/pastePhraseTable.py  $file.$SRC.d $file.$TARGET.d $file.als.d >> $DIR/dictcorpus.all

done

cat $DIR/dictcorpus.all | LC_ALL=C sort | uniq | grep -v '[^|]|[^|]'  | grep -E "^.*[^ ].* \|\|\| .*[^ ].* \|\|\|" | python $MYSCRIPTSDIR/filterEmptyPhrases.py -f 1,2 >$DIR/dictcorpus.nodup

python $MYSCRIPTSDIR/cutPhraseTable.py -f 1 <$DIR/dictcorpus.nodup > $DIR/dictcorpus.$SRC
python $MYSCRIPTSDIR/cutPhraseTable.py -f 2 <$DIR/dictcorpus.nodup > $DIR/dictcorpus.$TARGET
python $MYSCRIPTSDIR/cutPhraseTable.py -f 3 <$DIR/dictcorpus.nodup > $DIR/dictcorpus.als

python $MYSCRIPTSDIR/cutPhraseTable.py -f 1,2 < $DIR/dictcorpus.nodup | sed -r 's/$/ |||/' | LC_ALL=C sort | uniq  |gzip > $DIR/dictcorpus.gz

#rm $DIR/split_*
#rm $DIR/dictsplit_*
