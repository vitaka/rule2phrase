#! /bin/bash

SL=$1
TL=$2
MODES_DIR=$3

HASLTPROCB=false
if [ "`cat $MODES_DIR/${SL}-${TL}.mode | grep 'lt-proc -b' | wc -l`" == "1" ]; then
	HASLTPROCB=true
fi

#sl_lex_pre-tl_debug.mode
APERTIUMPATH=`cat $MODES_DIR/${SL}-${TL}.mode | perl -ne 'print  if s/.*[| ](\/[^ ]+\/)apertium-tagger.*/\1/' | tr -d '\n'`
if [ $HASLTPROCB ]; then
	FROMTRANSFERINC=`cat $MODES_DIR/${SL}-${TL}.mode | awk -F"lt-proc -b" '{ print $2 }' | tr -d '\n'`
	FROMTRANSFER=`echo "${APERTIUMPATH}lt-proc -b $FROMTRANSFERINC" | sed 's:/b:-b:'`
else
	FROMTRANSFERINC=`cat $MODES_DIR/${SL}-${TL}.mode | awk -F"apertium-transfer[ ]*[-/]" '{ print $2 }' | tr -d '\n'`
	FROMTRANSFER=`echo "${APERTIUMPATH}apertium-transfer /$FROMTRANSFERINC" | sed 's:/b:-b:'`
fi

FROMTRANSFERINCSPLITPOSTGENP1=`echo "$FROMTRANSFERINC" | awk -F"${APERTIUMPATH}lt-proc -p" '{ print $1 }'`
FROMTRANSFERINCSPLITPOSTGENP2=`echo "$FROMTRANSFERINC" | awk -F"${APERTIUMPATH}lt-proc -p" '{ print $2 }'`


#echo "apertium-transfer -d /$FROMTRANSFERINC"   > $MODES_DIR/${SL}_lex_pre-${TL}_debug.mode

echo "apertium-transfer -d /$FROMTRANSFERINCSPLITPOSTGENP1 "'sed  -r "s:^([]]?)([^[]+)(\\[\\\\\\[debug-transfer):\1\2 [ \\\\[debug-postgen \2 debug-postgen\\\\] ] \3:g" | '"${APERTIUMPATH}lt-proc -p$FROMTRANSFERINCSPLITPOSTGENP2" | sed 's:/b:-b:'  > $MODES_DIR/${SL}_lex_pre-${TL}_debug.mode

if [ $HASLTPROCB ]; then
	echo "$FROMTRANSFERINC"  > $MODES_DIR/${SL}_lex_pre-${TL}.mode
	echo "apertium-pretransfer | lt proc -b $FROMTRANSFERINC" | sed 's:/b:-b:'  > $MODES_DIR/${SL}_lex-${TL}.mode
else
	echo "apertium-transfer /$FROMTRANSFERINC"  | sed 's:/b:-b:'  > $MODES_DIR/${SL}_lex_pre-${TL}.mode
	echo "apertium-pretransfer | apertium-transfer /$FROMTRANSFERINC" | sed 's:/b:-b:'  > $MODES_DIR/${SL}_lex-${TL}.mode
fi

FROMTRANSFERSTEP1INC=`echo "$FROMTRANSFER" | awk -F"apertium-interchunk" '{ print $1 }'`
FROMTRANSFERSTEP2INC=`echo "$FROMTRANSFER" | awk -F"apertium-interchunk" '{ print $2 }'`

FROMTRANSFERSTEP1=`echo "$FROMTRANSFERSTEP1INC" | sed -r 's/\|[^|]*$//'`
FROMTRANSFERSTEP2=`echo "${APERTIUMPATH}apertium-interchunk$FROMTRANSFERSTEP2INC"`

echo "$FROMTRANSFERSTEP1" | sed -r 's/(apertium-transfer)/\1 -d/' > $MODES_DIR/${SL}_lex_pre-${TL}_step1_debug.mode
echo "$FROMTRANSFERSTEP1" > $MODES_DIR/${SL}_lex_pre-${TL}_step1.mode

FROMTRANSFERSTEP2DEBUGINC=`echo "$FROMTRANSFERSTEP2" | sed -r 's/(apertium-interchunk)/\1 -d/' | sed -r 's/(apertium-postchunk)/\1 -d/'`

FROMTRANSFERSTEP2DEBUGINCPART1=`echo "$FROMTRANSFERSTEP2DEBUGINC" | awk -F"${APERTIUMPATH}lt-proc -p" '{ print $1 }'`
FROMTRANSFERSTEP2DEBUGINCPART2=`echo "$FROMTRANSFERSTEP2DEBUGINC" | awk -F"${APERTIUMPATH}lt-proc -p" '{ print $2 }'`

#if FROMTRANSFERSTEP2DEBUGINCPART2 is empty, it means that lt-proc -p didn't exist (it may happen in Finnish), and
#we sould not include it
if [ "`echo "$FROMTRANSFERSTEP2DEBUGINCPART2" | tr -d ' ' | tr -d '\t'`" == "" ]; then
	echo "$FROMTRANSFERSTEP2DEBUGINCPART1"' | sed  -r "s:(^|\]?transfer\\\\\\]\\])(([^[]|\\[[^\\\\])+)(\\[\\\\\\[debug-postchunk):\1\2 [ \\\\[debug-postgen \2 debug-postgen\\]] \4:g"'  > $MODES_DIR/${SL}_lex_pre-${TL}_step2_debug.mode
else
	echo "$FROMTRANSFERSTEP2DEBUGINCPART1"'sed  -r "s:(^|\]?transfer\\\\\\]\\])(([^[]|\\[[^\\\\])+)(\\[\\\\\\[debug-postchunk):\1\2 [ \\\\[debug-postgen \2 debug-postgen\\]] \4:g" | '"${APERTIUMPATH}lt-proc -p$FROMTRANSFERSTEP2DEBUGINCPART2" > $MODES_DIR/${SL}_lex_pre-${TL}_step2_debug.mode
fi

echo "$FROMTRANSFERSTEP2" > $MODES_DIR/${SL}_lex_pre-${TL}_step2.mode




#sl_lex-tl_debug.mode
FROMPRETRANSFERINC=`cat $MODES_DIR/${SL}-${TL}.mode | awk -F"apertium-pretransfer" '{ print $2 }' | tr -d '\n'`
FROMPRETRANSFER="${APERTIUMPATH}apertium-pretransfer$FROMPRETRANSFERINC"

FROMPRETRANSFERSTEP1INC=`echo "$FROMPRETRANSFER" | awk -F"apertium-interchunk" '{ print $1 }'`
FROMPRETRANSFERSTEP2INC=`echo "$FROMPRETRANSFER" | awk -F"apertium-interchunk" '{ print $2 }'`

FROMPRETRANSFERSTEP1=`echo "$FROMPRETRANSFERSTEP1INC" | sed -r 's/\|[^|]*$//'`
FROMPRETRANSFERSTEP2=`echo "${APERTIUMPATH}apertium-interchunk$FROMPRETRANSFERSTEP2INC"`

echo "$FROMPRETRANSFERSTEP1" | sed -r 's/(apertium-transfer)/\1 -d/g' | sed -r 's/(apertium-pretransfer)/\1 -d/' > $MODES_DIR/${SL}_lex-${TL}_step1_debug.mode
echo "$FROMPRETRANSFERSTEP1" > $MODES_DIR/${SL}_lex-${TL}_step1.mode

FROMPRETRANSFERSTEP2DEBUGINC=`echo "$FROMPRETRANSFERSTEP2" | sed -r 's/(apertium-interchunk)/\1 -d/' | sed -r 's/(apertium-postchunk)/\1 -d/'`

FROMPRETRANSFERSTEP2DEBUGINCPART1=`echo "$FROMPRETRANSFERSTEP2DEBUGINC" | awk -F"${APERTIUMPATH}lt-proc -p" '{ print $1 }'`
FROMPRETRANSFERSTEP2DEBUGINCPART2=`echo "$FROMPRETRANSFERSTEP2DEBUGINC" | awk -F"${APERTIUMPATH}lt-proc -p" '{ print $2 }'`

#if FROMPRETRANSFERSTEP2DEBUGINCPART2 is empty, it means that lt-proc -p didn't exist (it may happen in Finnish), and
#we sould not include it
if [ "`echo "$FROMPRETRANSFERSTEP2DEBUGINCPART2" | tr -d ' ' | tr -d '\t'`" == "" ]; then
	echo "$FROMPRETRANSFERSTEP2DEBUGINCPART1"'| sed  -r "s:(^|\]?pretransfer\\\\\\]\\])(([^[]|\\[[^\\\\])+)(\\[\\\\\\[debug-postchunk):\1\2 [ \\\\[debug-postgen \2 debug-postgen\\]] \4:g"' > $MODES_DIR/${SL}_lex-${TL}_step2_debug.mode
else
	echo "$FROMPRETRANSFERSTEP2DEBUGINCPART1"'sed  -r "s:(^|\]?pretransfer\\\\\\]\\])(([^[]|\\[[^\\\\])+)(\\[\\\\\\[debug-postchunk):\1\2 [ \\\\[debug-postgen \2 debug-postgen\\]] \4:g" | '"${APERTIUMPATH}lt-proc -p$FROMPRETRANSFERSTEP2DEBUGINCPART2" > $MODES_DIR/${SL}_lex-${TL}_step2_debug.mode
fi
echo "$FROMPRETRANSFERSTEP2" > $MODES_DIR/${SL}_lex-${TL}_step2.mode


#sl_lex_analyzed_with_tl-sl.mode

DICTDIR=` cat $MODES_DIR/${SL}-${TL}.mode | awk -F"${SL}-${TL}.automorf.bin" '{ print $1 }' | awk -F"lt-proc " '{ print $2 }' | tr -d '\n'`

echo "${APERTIUMPATH}lt-proc "'$1'" ${DICTDIR}${SL}-${TL}.automorfinv.bin" > $MODES_DIR/${SL}_lex_analyzed_with_${TL}-${SL}.mode

#sl-tl-pretransfer
TOTRANSFERINC=`cat $MODES_DIR/${SL}-${TL}.mode | awk -F"apertium-transfer[ ]*[-/]" '{ print $1 }' |  sed -r 's/\|[^|]*$//' | tr -d '\n'`
TOTRANSFER=`echo "$TOTRANSFERINC" | awk -F"apertium-pretransfer" '{ print $2 }' | tr -d '\n'`
echo "$APERTIUMPATH""apertium-pretransfer$TOTRANSFER" > $MODES_DIR/${SL}-${TL}-pretransfer.mode

#sl-sl_lex_pretransfer_to_tl
echo "$TOTRANSFERINC" | awk -F"lt-proc -b" '{ print $1 }' |  sed -r 's/\|[^|]*$//' | tr -d '\n' > $MODES_DIR/${SL}-${SL}_lex_pretransfer_to_${TL}.mode
