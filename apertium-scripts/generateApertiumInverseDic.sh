#! /bin/bash

DEFSOURCE=es
DEFTARGET=pt

SOURCE=${1:-$DEFSOURCE}
TARGET=${2:-$DEFTARGET}
DIXFILE=$3
APERTIUM_SOURCE_DIR=$4
APERTIUM_INSTALL_DIR=$5

#IMPORTANTEEEEEEEEEEEEEEE!!!!!!!!!!!!                                      Esto debería ser LR!!!! -----> <----
#cat $DIXFILE | sed -r 's_r=\"RL\"_r=\"NLR\"_g'| sed -r 's_r=\"LR\"_r=\"RL\"_g' | sed -r 's_r=\"NLR\"_r=\"RL\"_g' > $APERTIUM_SOURCE_DIR/apertium-$MODE.${SOURCE}inv.dix
cat $DIXFILE | sed -r 's_r=\"RL\"_r=\"NLR\"_g'| sed -r 's_r=\"LR\"_r=\"RL\"_g' | sed -r 's_r=\"NLR\"_r=\"LR\"_g' > $APERTIUM_SOURCE_DIR/apertium.${SOURCE}inv.dix

lt-comp rl $APERTIUM_SOURCE_DIR/apertium.${SOURCE}inv.dix  $APERTIUM_INSTALL_DIR/$SOURCE-$TARGET.automorfinv.bin

