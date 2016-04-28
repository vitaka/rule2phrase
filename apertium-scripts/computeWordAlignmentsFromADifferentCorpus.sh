#! /bin/bash

SL=$1
TL=$2
WORKDIR=$3
TRAINCORPUS=$4
TESTCORPUS=$5
CLEANTESTCORPUS=$6

TOOLSDIR=/home/vmsanchez/wmt/tools
SCRIPTSDIR=/home/vmsanchez/wmt/tools/scripts


mkdir -p $WORKDIR/corpus

cat $TRAINCORPUS.$SL | $SCRIPTSDIR/tokenizer.perl -l $SL  | $SCRIPTSDIR/lowercase.perl  >  $WORKDIR/corpus/dirttrain.$SL
cat $TRAINCORPUS.$TL | $SCRIPTSDIR/tokenizer.perl -l $TL  | $SCRIPTSDIR/lowercase.perl  >  $WORKDIR/corpus/dirttrain.$TL

$TOOLSDIR/moses-scripts/training/clean-corpus-n.perl $WORKDIR/corpus/dirttrain $SL $TL $WORKDIR/corpus/cleantrain 1 40

cat $WORKDIR/corpus/cleantrain.$SL > $WORKDIR/corpus/$SL
cat $WORKDIR/corpus/cleantrain.$TL > $WORKDIR/corpus/$TL


cat $TESTCORPUS.$SL | $SCRIPTSDIR/tokenizer.perl -l $SL  | $SCRIPTSDIR/lowercase.perl > $WORKDIR/corpus/dirttest.$SL
cat $TESTCORPUS.$TL | $SCRIPTSDIR/tokenizer.perl -l $TL  | $SCRIPTSDIR/lowercase.perl > $WORKDIR/corpus/dirttest.$TL

if [ "l$CLEANTESTCORPUS" == "lno" ] ; then

cat $WORKDIR/corpus/dirttest.$SL  >  $WORKDIR/corpus/$SL-test
cat $WORKDIR/corpus/dirttest.$TL  > $WORKDIR/corpus/$TL-test

cat $WORKDIR/corpus/dirttest.$SL  >  $WORKDIR/corpus/test.$SL
cat $WORKDIR/corpus/dirttest.$TL  > $WORKDIR/corpus/test.$TL

else

$TOOLSDIR/moses-scripts/training/clean-corpus-n.perl $WORKDIR/corpus/dirttest $SL $TL $WORKDIR/corpus/test 1 40 

cat $WORKDIR/corpus/test.$SL  >  $WORKDIR/corpus/$SL-test
cat $WORKDIR/corpus/test.$TL  > $WORKDIR/corpus/$TL-test

fi


pushd $WORKDIR/corpus
$TOOLSDIR/plain2snt-miquel/plain2snt.out  $SL $TL $SL-test $TL-test

popd

$TOOLSDIR/bin/mkcls -c50 -n2 -p$WORKDIR/corpus/$SL -V$WORKDIR/corpus/$SL.vcb.classes opt
$TOOLSDIR/bin/mkcls -c50 -n2 -p$WORKDIR/corpus/$TL -V$WORKDIR/corpus/$TL.vcb.classes opt

mkdir -p $WORKDIR/giza.$SL-$TL
mkdir -p $WORKDIR/giza.$TL-$SL

$TOOLSDIR/bin/GIZA++ -c $WORKDIR/corpus/${SL}_${TL}.snt -m1 5 -m2 0 -m3 3 -m4 3 -model1dumpfrequency 1 -model4smoothfactor 0.4 -nodumps 1 -nsmooth 4 -o $WORKDIR/giza.$SL-$TL/$SL-$TL -onlyaldumps 1 -p0 0.999 -s $WORKDIR/corpus/$SL.vcb -t $WORKDIR/corpus/$TL.vcb -tc $WORKDIR/corpus/$SL-test_$TL-test.snt

$TOOLSDIR/bin/GIZA++ -c $WORKDIR/corpus/${TL}_${SL}.snt -m1 5 -m2 0 -m3 3 -m4 3 -model1dumpfrequency 1 -model4smoothfactor 0.4 -nodumps 1 -nsmooth 4 -o $WORKDIR/giza.$TL-$SL/$TL-$SL -onlyaldumps 1 -p0 0.999 -s $WORKDIR/corpus/$TL.vcb -t $WORKDIR/corpus/$SL.vcb -tc $WORKDIR/corpus/$TL-test_$SL-test.snt

rm -f  $WORKDIR/giza.$SL-$TL/$SL-$TL.A3.final.gz $WORKDIR/giza.$SL-$TL/$SL-$TL.tst.A3.final.gz $WORKDIR/giza.$TL-$SL/$TL-$SL.A3.final.gz $WORKDIR/giza.$TL-$SL/$TL-$SL.tst.A3.final.gz

gzip $WORKDIR/giza.$SL-$TL/$SL-$TL.A3.final 
gzip $WORKDIR/giza.$SL-$TL/$SL-$TL.tst.A3.final 
gzip $WORKDIR/giza.$TL-$SL/$TL-$SL.A3.final 
gzip $WORKDIR/giza.$TL-$SL/$TL-$SL.tst.A3.final

mkdir -p $WORKDIR/model
$TOOLSDIR/moses-scripts/training/symal/giza2bal.pl -d "gzip -cd $WORKDIR/giza.$SL-$TL/$SL-$TL.tst.A3.final.gz" -i "gzip -cd $WORKDIR/giza.$TL-$SL/$TL-$SL.tst.A3.final.gz" | $TOOLSDIR/moses-scripts/training/symal/symal -alignment="grow" -diagonal="yes" -final="yes" -both="yes" > $WORKDIR/model/aligned.grow-diag-final-and

$TOOLSDIR/moses-scripts/training/train-model.perl  --first-step 4 --last-step 6 --root-dir $WORKDIR --corpus $WORKDIR/corpus/test --f $SL --e $TL --alignment grow-diag-final-and  --reordering msd-bidirectional-fe 
