#!/usr/bin/python
# coding=utf-8
# -*- encoding: utf-8 -*-

import re, sys, string, apertium, getopt;
from expandPTLib import *

t=u"à la fin de .  [debug-postgen à la fin ~de ~. debug-postgen] [debug-postchunk {norule-chunk ^à la fin de<pr>$ norule-chunk}{postchunk-rule ^punt<sent>{^.<sent>$}$ -- ^0-.<sent>$ postchunk-rule} debug-postchunk][debug-interchunk  {isolated-word ^à la fin de<PREP>{^à la fin de<pr>$}$ isolated-word} {interchunk-rule punt --^punt<sent>{^.<sent>$}$ -- ^0-punt<sent>{^.<sent>$}$ interchunk-rule} debug-interchunk][debug-transfer {transfer-rule prep --^e dibenn<pr>$ -- {start-chunk ^0-à la fin de<pr>$ end-chunk} transfer-rule}{transfer-rule sent --^.<sent>$ -- {start-chunk ^0-.<sent>$ end-chunk} transfer-rule} debug-transfer]"
mwlf=MultiwordLexicalForms()
print >>sys.stderr, "Loading target language multiword lexical forms"
mwlf.load("/work2/vmsanchez/wmt/synthetic/br-fr-tyers/lemmas-target/multiwords")
debugInfo = DebugInfo(t,"",mwlf)
debugInfo.extractModuleOutputs(True,False, True, True)

print debugInfo.debugTransfer.encode('utf-8')
print debugInfo.debugInterchunk.encode('utf-8')
print debugInfo.debugPostchunk.encode('utf-8')
print debugInfo.debugPostGen.encode('utf-8')

debugInfo.extractTransferAndGenerationAlignments2level()
#debugInfo.extractTransferAndGenerationAlignments()
debugInfo.extractPostGenerationAlignments()

print debugInfo.translation.encode('utf-8')+" ||| "+debugInfo.alignmentsTransfer.toString().encode('utf-8')+" ||| "+debugInfo.alignmentsInterchunk.toString().encode('utf-8')+" ||| "+debugInfo.alignmentsPostchunk.toString().encode('utf-8')+" ||| "+debugInfo.alignmentsGeneration.toString().encode('utf-8')+" ||| "+debugInfo.alignmentsPostGeneration.toString().encode('utf-8')

