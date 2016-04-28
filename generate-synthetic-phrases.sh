#! /bin/bash

MYFULLPATH=`readlink -f $0`
CURDIR=`dirname "$MYFULLPATH"`
SCRIPTSDIR="$CURDIR/apertium-scripts"
source $CURDIR/shflags

function identify_apertium_monolingual_dict {
local SL="$1"
local APERTIUMPAIR="$2"
local APERTIUM_PAIR_DATA="$3"

local APERTIUMSLDICT=""
if [ -f "$APERTIUM_PAIR_DATA/.deps/$SL.dix" ]; then
	APERTIUMSLDICT="$APERTIUM_PAIR_DATA/.deps/$SL.dix"
elif [ -f "$APERTIUM_PAIR_DATA/apertium-$APERTIUMPAIR.$SL.dix"  ]; then
	APERTIUMSLDICT="$APERTIUM_PAIR_DATA/apertium-$APERTIUMPAIR.$SL.dix"
elif [ -f "$APERTIUM_PAIR_DATA/../apertium-$SL/.deps/$SL.dix"  ]; then
	APERTIUMSLDICT="$APERTIUM_PAIR_DATA/../apertium-$SL/.deps/$SL.dix"
elif [ -f "$APERTIUM_PAIR_DATA/../apertium-$SL/apertium-$SL.$SL.dix" ]; then
	APERTIUMSLDICT="$APERTIUM_PAIR_DATA/../apertium-$SL/apertium-$SL.$SL.dix"
fi
if [ "$APERTIUMSLDICT" == "" ]; then
	echo "Error. Apertium $SL dictionary could not be identified" >&2
	exit 1
fi

echo "$APERTIUMSLDICT"

}

################# This program generates a set of synthetic phrases from Apertium and an SL text ###############################
################# They can afterwards be integrated in a phrase table ##########################################################
DEFINE_string 'sl' '' 'Source language' 's'
DEFINE_string 'tl' '' 'Target language' 't'
DEFINE_string 'apertium_prefix' '~/local' 'Apertium installation prefix' 'p'
DEFINE_string 'moses_dir' '~/mosesdecoder' 'Moses installation directory' 'm'
DEFINE_string 'apertium_data' '' 'Directory with the source code of the language pair' 'u'
DEFINE_string 'input' '' 'Input text in the SL' 'i'
DEFINE_string 'output_dir' '' 'Output directory' 'o'
DEFINE_boolean 'generate_corpus_independent_data' 'false' 'Generate corpus-independent data in output_dir. Note that this is prerrequisite for the generation of synthetc phrase pairs' 'n'
DEFINE_string 'corpus_independent_dir' '' 'Directory with corpus-independent data' 'd'
DEFINE_string 'fast_align_dir' '' 'Directory where fast_align executable files can be found' 'a'
DEFINE_string 'truecaser_sl' '' 'Truecaser model for the SL' 'c'
DEFINE_string 'truecaser_tl' '' 'Truecaser model for the TL' 'C'
DEFINE_boolean 'factored' false 'Generate TL additional factor with morphological information' 'F'

FLAGS "$@" || exit $?
eval set -- "${FLAGS_ARGV}"

SL=${FLAGS_sl}
TL=${FLAGS_tl}
APERTIUM_PREFIX=${FLAGS_apertium_prefix}
MOSES_DIR=${FLAGS_moses_dir}
APERTIUM_PAIR_DATA=${FLAGS_apertium_data}
INPUTFILES=${FLAGS_input}
OUTPUTDIR=${FLAGS_output_dir}
FASTALIGNDIR="${FLAGS_fast_align_dir}"

GENCORPUSIND=${FLAGS_generate_corpus_independent_data}
CORPUSINDDIR=${FLAGS_corpus_independent_dir}

if [ "$SL" == "" -o "$TL" == "" -o "$APERTIUM_PREFIX" == ""  -o "$MOSES_DIR" == "" -o "$APERTIUM_PAIR_DATA" == "" -o "$INPUTFILES" == "" -o "$OUTPUTDIR" == "" -o "$FASTALIGNDIR" == "" ]; then
	echo "Error. Input parameters cannot be empty. Use --help for the list of parameters. All of them are mandatory" >&2
	exit 1
fi

if [ "$CORPUSINDDIR" == "" -a "$GENCORPUSIND" != "${FLAGS_TRUE}"  ]; then
	echo "Error. You must provide a corpus-independent data dir with --corpus_independent_dir if you are not generating it with this command"
	exit
fi



echo "Welcome to the synthetic phrase pair generator from Apertium data"
echo "-----------------------------------------------------------------"


if [  "$GENCORPUSIND" == "${FLAGS_TRUE}" ]; then
	MYMAKEFILE="$CURDIR/Makefile-synthetic-corpus-independent"
	echo "Generating CORPUS-INDEPENDENT DATA"
else
	MYMAKEFILE="$CURDIR/Makefile-synthetic-corpus-dependent"
	echo "Generating CORPUS-DEPENDENT DATA using corpus-independent data from $CORPUSINDDIR"
fi

echo "1.1 Make sure the Apertium installed in $APERTIUM_PREFIX has been patched with patch provided in this package"
echo "1.2 Checking TMPDIR:"
if [ "$TMPDIR" != "" ]; then
	echo "You are using $TMPDIR for temporary file storage. Make sure you have at least 100 free GiB"
else
	echo "You are using the default sytem location (usually /tmp) for temporary file storage. Make sure you have at least 100 free GiB"
fi

MODESDIR=$APERTIUM_PREFIX/share/apertium/modes
echo "2.1 Creating new modes needed for the synthetic phrase generation in $MODESDIR"
bash $SCRIPTSDIR/generateApertiumSpecialModes.sh $SL $TL "$MODESDIR"


echo "3. Compiling required Java packages"
pushd $SCRIPTSDIR/ApertiumPhraseGenerator
mvn compile assembly:single
popd

echo "4. Detecting Apertium information: pair and files"

#pair
APERTIUMSOURCEBASENAME=`basename $APERTIUM_PAIR_DATA`
APERTIUMPAIR=""
if [[ $APERTIUMSOURCEBASENAME == *"$SL-$TL"* ]]; then
  APERTIUMPAIR="$SL-$TL"
elif [[ $APERTIUMSOURCEBASENAME == *"$TL-$SL"* ]]; then
  APERTIUMPAIR="$TL-$SL"
fi
if [ "$APERTIUMPAIR" == "" ]; then
	echo "Error. Apertium pair could not be identified" >&2
	exit 1
fi
echo "Apertium pair: $APERTIUMPAIR found!"

#SL dictionary
APERTIUMSLDICT=`identify_apertium_monolingual_dict $SL $APERTIUMPAIR "$APERTIUM_PAIR_DATA"`
echo "Apertium $SL monolingual dictionry: $APERTIUMSLDICT found!"

#TL dictionary
APERTIUMTLDICT=`identify_apertium_monolingual_dict $TL $APERTIUMPAIR "$APERTIUM_PAIR_DATA"`
echo "Apertium $TL monolingual dictionry: $APERTIUMTLDICT found!"


echo "5. Generating reversed SL monolingual dictionary"
bash $SCRIPTSDIR/generateApertiumInverseDic.sh $SL $TL $APERTIUMSLDICT $APERTIUM_PAIR_DATA $APERTIUM_PREFIX/share/apertium/apertium-$APERTIUMPAIR


echo "6. Running phrase generation"
PMORPHVALUE=""
if [ "${FLAGS_factored}" == "${FLAGS_TRUE}" ]; then
	PMORPHVALUE="printmorph"
fi

PATH="$APERTIUM_PREFIX/bin:$PATH" time  make -f $MYMAKEFILE SL=$SL TL=$TL DIRSYNTH=$OUTPUTDIR APERTIUMPAIR=$APERTIUMPAIR FILTERFILES="$INPUTFILES" MOSESDIR=$MOSES_DIR PREFIX=$APERTIUM_PREFIX LANGUAGEPAIRSOURCEDIR="$APERTIUM_PAIR_DATA" SOURCEDICT_FILE="$APERTIUMSLDICT" TARGETDICT_FILE="$APERTIUMTLDICT" CORPUSINDEPENDENTDATADIR="$CORPUSINDDIR" FASTALIGNDIR="$FASTALIGNDIR" PAR_TRUECASER_MODEL_SL="${FLAGS_truecaser_sl}" PAR_TRUECASER_MODEL_TL="${FLAGS_truecaser_tl}" PRINTTLMORPH="$PMORPHVALUE"
