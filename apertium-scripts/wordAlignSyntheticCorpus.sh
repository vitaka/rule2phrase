#! /bin/bash

SDIR=$1
SL=$2
TL=$3

SYNTHNAME=syntheticCorpus2levelplusdetdict
MOSESDIR=/home/vmsanchez/hybrid-thesis/tools/mosesdecoder

mkdir -p $SDIR/mosesalign/corpus
cp $SDIR/$SYNTHNAME.$SL $SDIR/mosesalign/corpus/corpus.$SL
cp $SDIR/$SYNTHNAME.$TL $SDIR/mosesalign/corpus/corpus.$TL

$MOSESDIR/scripts/training/train-model.perl --last-step 3 --root-dir $SDIR/mosesalign --corpus $SDIR/mosesalign/corpus/corpus   --f $SL --e $TL  --parallel  --alignment grow-diag-final-and  --reordering msd-bidirectional-fe  --external-bin-dir $MOSESDIR/../tools --mgiza --mgiza-cpus 4

cp $SDIR/mosesalign/model/aligned.grow-diag-final-and $SDIR/$SYNTHNAME.als.giza


mkdir -p $SDIR/mosesalign-dict/corpus
cp $SDIR/dictionary/dictcorpus.$SL $SDIR/mosesalign-dict/corpus/corpus.$SL
cp $SDIR/dictionary/dictcorpus.$TL $SDIR/mosesalign-dict/corpus/corpus.$TL

$MOSESDIR/scripts/training/train-model.perl --last-step 3 --root-dir $SDIR/mosesalign-dict --corpus $SDIR/mosesalign-dict/corpus/corpus   --f $SL --e $TL  --parallel  --alignment grow-diag-final-and  --reordering msd-bidirectional-fe  --external-bin-dir $MOSESDIR/../tools --mgiza --mgiza-cpus 4

cp $SDIR/mosesalign-dict/model/aligned.grow-diag-final-and $SDIR/dictionary/dictcorpus.als.giza

