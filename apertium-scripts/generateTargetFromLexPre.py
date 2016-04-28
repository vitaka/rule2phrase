#!/usr/bin/python
# coding=utf-8
# -*- encoding: utf-8 -*-

import re, sys, string, apertium, getopt;
from expandPTLib import *

DEBUG=True

debuggerInput=["^habitante<n><mf><pl>$","^ya<adv>$ ^se<prn><pro><ref><p3><mf><sp>$ ^haber<vbhaver><pri><p3><sg>$ ^suscitar<vblex><pp><m><sg>$","^solicitante<n><mf><pl>$"]

#splitter = re.compile("\.sep_sentence_vmsanchez\n?")
splitter = re.compile("sep_sentence_vmsanchez\n?")

srclang="es"
targetlang="pt"
debugOn=False
mwFile="error_mw_file_not_selected"
duplicateToBeDetemrined=False
duplicatedLinesFile=""
writeDebugInfo=False
outputTransfer1level=False
outputTransfer1levelFile=""
inputt1x=False
postTransfer=False

try:
	opts, args = getopt.getopt(sys.argv[1:], "ib:ds:t:m:o:hwp", ["inputt1x","duplicateToBeDetemrined:","debug","sourcelang=","targetlang=","mwlexicalforms=","outputt1x=","help","writeDebugInfo", "postTransfer" ])
except getopt.GetoptError, err:
	# print help information and exit:
	print str(err) # will print something like "option -a not recognized"
	usage()
	sys.exit(2)

for o, a in opts:
	if o in ("-h", "--help"):
		usage()
		sys.exit()
	elif o in ("-d", "--writeDebugInfo"):
		writeDebugInfo=True
	elif o in ("-i", "--inputt1x"):
		inputt1x=True
	elif o in ("-w", "--debug"):
		debugOn=True
	elif o in ("-s", "--sourcelang"):
		srclang=a
	elif o in ("-t", "--targetlang"):
		targetlang=a
	elif o in ("-m", "--mwlexicalforms"):
		mwFile=a
	elif o in ("-o", "--outputt1x"):
		outputTransfer1level=True
		outputTransfer1levelFile=a
	elif o in ("-b", "--duplicateToBeDetemrined"):
		duplicateToBeDetemrined=True
		duplicatedLinesFile=a
	elif o in ("-p","--postTransfer"):
		postTransfer=True
	else:
		assert False, "unhandled option"

print >>sys.stderr, "srclang="+srclang+" targetlang="+targetlang+" debug:"+str(debugOn)

debugFragments=list()

lexforms=list()
#for line in debuggerInput:
for line in sys.stdin:
	line=line.decode('utf-8').strip()
	if debugOn and inputt1x:
		pieces=line.split(u"|||")
		lexforms.append(pieces[0].strip())
		debugFragments.append(pieces[1].strip())
	else:
		lexforms.append(line)

src=(u"^.<sent>$[sep_sentence_vmsanchez\n]").join(lexforms)+u"^.<sent>$[]"

if not duplicateToBeDetemrined and not inputt1x:
	mode=srclang+"_lex_pre-"+targetlang
	if debugOn:
		mode+="_debug"

	if DEBUG:
		fsource=open("/tmp/finputd","w")
		fsource.write(src.encode('utf-8'))
		fsource.close()
	localTranslation=apertium.translateAndReformat(src,mode)

	#print localTranslation.encode('utf-8')

	#translations=splitter.split(localTranslation[:-1])
	translations=splitter.split(localTranslation)

	if DEBUG:
		ftarget=open("/tmp/ftarget","w")
		ftarget.write(localTranslation.encode('utf-8'))
		ftarget.close()

	if not len(translations) == len(lexforms):
		print >> sys.stderr, "Error: length mismatch between lex phrases and translations "+str(len(translations))+" != "+str(len(lexforms))
		exit(1)

	if debugOn:
		mwlf=MultiwordLexicalForms()
		print >>sys.stderr, "Loading target language multiword lexical forms"
		mwlf.load(mwFile)

		for t in translations:
			debugInfo = DebugInfo(t,"",mwlf)
			debugInfo.extractModuleOutputs(True,False)
			debugInfo.extractTransferAndGenerationAlignments(postTransfer)
			debugInfo.extractPostGenerationAlignments()
			print debugInfo.translation.encode('utf-8')+" ||| "+debugInfo.alignmentsTransfer.toString().encode('utf-8')+" ||| "+debugInfo.alignmentsGeneration.toString().encode('utf-8')+" ||| "+debugInfo.alignmentsPostGeneration.toString().encode('utf-8')
	else:
		for t in translations:
			print t[:-1].encode('utf-8')
else:
	mode1=srclang+"_lex_pre-"+targetlang+"_step1"
	mode2=srclang+"_lex_pre-"+targetlang+"_step2"
	if debugOn:
		mode1+="_debug"
		mode2+="_debug"

	if inputt1x:
		src2list=list()
		for i in range(len(lexforms)):
			lf=lexforms[i]
			if debugOn:
				df=debugFragments[i]
				src2list.append(lf+u" ^punt<sent>{^.<sent>$}$ [\[debug-transfer "+df+u" debug-transfer\]]")
			else:
				src2list.append(lf+u" ^punt<sent>{^.<sent>$}$")
		#src2=u"[sep_sentence_vmsanchez]\n".join(src2list)+u"^punt<sent>{^.<sent>$}$[\[debug-transfer {transfer-rule sent --\^.<sent>\$ -- \^0-.<sent>\$ transfer-rule} debug-transfer\]][]"
		#src2=u"[sep_sentence_vmsanchez\n]".join(src2list)+u"[]"
		#replaced=lexforms
		#localTranslation=u""
		localTranslation=u"[sep_sentence_vmsanchez\n]".join(src2list)+u"[]"
	else:
		localTranslation=apertium.translate(src,'none',mode1)

	startDebugTransfer=u"[\[debug-transfer"
	endDebugTransfer=u"debug-transfer\]]"

	#replace lines with <ND> or <GD>
	patterns=[u"<ND>",u"<GD>",u"<PD>"]
	replacements=[[u"<sg>",u"<pl>"],[u"<m>",u"<f>"],[u"<p1>",u"<p2>",u"<p3>"]]
	curline=-1
	replaced=list()
	replacementsDone=list()

	chunkFound=False

	for line in localTranslation.split("\n"):
		curline+=1
		#saber si hay un solo chunk
		posStartSecondPart=line.find(startDebugTransfer)
		if posStartSecondPart > -1:
			firstPartLine=line[:posStartSecondPart]
		else:
			firstPartLine=line
		numChunks=-1
		mypos=0
		prevPos=0
		while mypos> -1:
			numChunks+=1
			mypos=firstPartLine.find(u"{",prevPos)
			if mypos >= 0:
				chunkFound=True
			prevPos=mypos+1

		#print >> sys.stderr, line.encode('utf-8')+" ||| num chunks="+str(numChunks)
		patternFound=False
		if numChunks==2:
			localReplaced=list()
			localReplaced.append(line)
			for numpat in range(len(patterns)):
				pattern=patterns[numpat]
				replacement=replacements[numpat]
				llReplaced=list()
				for lr in localReplaced:
					pos=lr.find(pattern)
					if pos > -1:
						patternFound=True
						for r in replacement:
							tline=lr[:pos]+r+lr[pos+len(pattern):]
							llReplaced.append(tline)
					else:
						llReplaced.append(lr)
				localReplaced=llReplaced
			if patternFound:
				replacementsDone.append((curline,len(localReplaced)))
				for lr in localReplaced:
					replaced.append(lr)

		if not patternFound:
			replaced.append(line)

	#we should remove entries with ^@: it means that they are not found in bilingual dictionary and it will cause
	#many problems
	for i in xrange(len(replaced)):
		if "^@" in replaced[i]:
			#May this cause problems when there is no interchunk module?
			if chunkFound:
				replaced[i]=(u"]" if i > 0 else u"")+u"^sent<SENT>{^.<sent>$}$[]"
			else:
				replaced[i]=(u"]" if i > 0 else u"")+u"^.<sent>$[]"

	icounter=len(replaced)-2
	while icounter>=0:
		if replaced[icounter].endswith(u"[]"):
			replaced[icounter]=replaced[icounter][:-1]+u"sep_sentence_vmsanchez"
		icounter-=1

	src2=u" \n".join(replaced)

	if outputTransfer1level:
		fsrca1=open(outputTransfer1levelFile,"w")
		if not debugOn:
			## remove entries with ^@
			for line in localTranslation.split("\n"):
				if not u"^@" in line:
					fsrca1.write(line.encode("utf-8")+"\n")
		else:
			for line in localTranslation.split("\n"):
				pos=line.find(startDebugTransfer)
				if pos>-1 and not u"^@" in line:
					chunk=line[:pos]
					pos2=line.find(endDebugTransfer,pos)
					if pos2>-1:
						transferdebug=line[pos+len(startDebugTransfer):pos2]
						fsrca1.write(chunk.encode('utf-8')+" ||| "+transferdebug.encode('utf-8')+"\n")
		fsrca1.close()

	#print >>sys.stderr , src2[:200].encode('utf-8')

	localTranslation2=apertium.translateAndReformat(src2,mode2)

	#print >>sys.stderr , localTranslation2[:200].encode('utf-8')

	translations=splitter.split(localTranslation2)

	#print >>sys.stderr , translations[0].encode('utf-8')

	#debug
	if DEBUG:
		fsrca1=open("/tmp/fsrc-1","w")
		fsrca1.write(localTranslation.encode('utf-8'))
		fsrca1.close()
		fsrc=open("/tmp/fsrc","w")
		fsrc.write(u"\n".join(replaced).encode('utf-8'))
		fsrc.close()
		ftarget=open("/tmp/ftarget","w")
		ftarget.write(localTranslation2.encode('utf-8'))
		ftarget.close()

	if not len(translations) == len(replaced):
		print >> sys.stderr, "Error: length mismatch between translations and lex phrases "+str(len(translations))+" != "+str(len(replaced))
		exit(1)

	#debug

	if debugOn:
		mwlf=MultiwordLexicalForms()
		print >>sys.stderr, "Loading target language multiword lexical forms"
		mwlf.load(mwFile)

		for t in translations:

			#debug
			#if t.startswith(u"It does not include"):
			#print >>sys.stderr, t.encode('utf-8')

			debugInfo = DebugInfo(t,"",mwlf)
			debugInfo.extractModuleOutputs(True,False, True, not inputt1x)
			debugInfo.extractTransferAndGenerationAlignments2level()
			#debugInfo.extractTransferAndGenerationAlignments()
			debugInfo.extractPostGenerationAlignments()

			#print debugInfo.translation.encode('utf-8')+" ||| "+debugInfo.alignmentsTransfer.toString().encode('utf-8')+" ||| "+debugInfo.alignmentsGeneration.toString().encode('utf-8')+" ||| "+debugInfo.alignmentsPostGeneration.toString().encode('utf-8')
			#print debugInfo.translation.encode('utf-8')+" ||| "+debugInfo.debugTransfer.encode('utf-8')+" ||| "+debugInfo.alignmentsTransfer.toString().encode('utf-8')+" ||| "+str(debugInfo.chunkAls)+" ||| "+debugInfo.debugInterchunk.encode('utf-8')+" ||| "+debugInfo.interAls.toString().encode('utf-8')+" ||| "+debugInfo.alignmentsInterchunk.toString().encode('utf-8')+" ||| "+debugInfo.debugPostchunk.encode('utf-8')+" ||| "+debugInfo.postAls.toString().encode('utf-8')+" ||| "+debugInfo.alignmentsGeneration.toString().encode('utf-8')
			print debugInfo.translation.encode('utf-8')+" ||| "+debugInfo.alignmentsTransfer.toString().encode('utf-8')+" ||| "+debugInfo.alignmentsInterchunk.toString().encode('utf-8')+" ||| "+debugInfo.alignmentsPostchunk.toString().encode('utf-8')+" ||| "+debugInfo.alignmentsGeneration.toString().encode('utf-8')+" ||| "+debugInfo.alignmentsPostGeneration.toString().encode('utf-8')

	else:
		for t in translations:
			tp=t
			if targetlang != "en":
				tp=t[:-1]
			tp=languageSpecificPostProcess(targetlang,tp)
			print tp.strip().encode('utf-8')

	if duplicatedLinesFile!="":
		f=open(duplicatedLinesFile,"w")
		for r in replacementsDone:
			f.write(str(r[0])+" "+str(r[1])+"\n")
		f.close()
