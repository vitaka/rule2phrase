#!/usr/bin/python
# coding=utf-8
# -*- encoding: utf-8 -*-

import re, sys, string, apertium, getopt;
from expandPTLib import *

splitter = re.compile(r'\[sep_sentence\][\n]?')
patternForLex=re.compile(r"\^(([^$]*)\$)")

srclang="es"
targetlang="pt"
debugOn=False
mwFile="error_mw_file_not_selected"

try:
	opts, args = getopt.getopt(sys.argv[1:], "ds:t:m:h", ["debug","sourcelang=","targetlang=","mwlexicalforms=","help" ])
except getopt.GetoptError, err:
	# print help information and exit:
	print str(err) # will print something like "option -a not recognized"
	usage()
	sys.exit(2)

for o, a in opts:
	if o in ("-h", "--help"):
		usage()
		sys.exit()
	elif o in ("-d", "--debug"):
		debugOn=True
	elif o in ("-s", "--sourcelang"):
		srclang=a
	elif o in ("-t", "--targetlang"):
		targetlang=a
	elif o in ("-m", "--mwlexicalforms"):
		mwFile=a
	else:
		assert False, "unhandled option"

print >>sys.stderr, "srclang="+srclang+" targetlang="+targetlang+" debug:"+str(debugOn)

lexforms=list()
prevAlignments=list()
for line in sys.stdin:
	line=line.decode('utf-8').strip()
	if debugOn:
		parts=line.split(u"|||")
		if len(parts) >= 2:
			lexforms.append(parts[0].strip())
			#sa = SentenceAlignments()
			#sa.parse(parts[1].strip())
			sa=u"|||".join(parts[1:])
			prevAlignments.append(sa)
	else:
		lexforms.append(line)

if targetlang == "pt":
	mode=srclang+"_lex_analyzed-"+srclang
else:
	mode=srclang+"_lex_analyzed_with_"+targetlang+"-"+srclang
	
supForm=apertium.translate(u"[sep_sentence]\n".join(lexforms).replace(u"^",u"[sep_word_vmsanchez_e][sep_word_vmsanchez_s]^"),"none",mode)
supForms=splitter.split(supForm)

if not len(supForms) == len(lexforms):
	print >> sys.stderr, "Error: length mismatch between surface form phrases ("+str(len(supForms))+") and lexical forms ("+str(len(lexforms))+")"
	print >> sys.stderr, supForm
	exit(1)

if debugOn:
	mwlf=MultiwordLexicalForms()
	#print >>sys.stderr, "Loading target language multiword lexical forms"
	mwlf.load(mwFile)

	for i in range(len(supForms)):
		sup=supForms[i]
		lex=lexforms[i]
		prevSa=prevAlignments[i]
		sa=SentenceAlignments()	
		iterator=patternForLex.finditer(lex)
		word=0
		offset=0
		#print >>sys.stderr, "Lex: "+lex.encode('utf-8')
		for m in iterator:
			word+=1
			lexform=m.group()[1:-1]
			numSfWords=mwlf.getNumWords(lexform)
			#print >>sys.stderr, "Match: "+m.group().encode('utf-8')+" "+str(numSfWords)
			for j in range(numSfWords):
				sa.alignments.append((word+offset+j,word))
			offset+=(numSfWords-1)
		
		print sup.encode('utf-8')+" ||| "+sa.toString().encode('utf-8')+" ||| "+prevSa.encode('utf-8')
		
else:
	for i in range(len(supForms)):
		sup=supForms[i]
		print sup.encode('utf-8')
