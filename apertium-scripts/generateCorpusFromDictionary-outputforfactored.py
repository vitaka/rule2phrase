#!/usr/bin/python
# coding=utf-8
# -*- encoding: utf-8 -*-

import sys,re,codecs,apertium;
from expandPTLib import *

DEBUG=False

if not sys.argv[2]:
	print >>sys.stderr, "Not enough parameters. Aborting"
	exit(1)

lexforms=list()
supforms=list()

sourceLang="es"
targetLang="pt"
usePreTransfer=False
duplicateToBeDetermined=False
alignments=True

emptymode=False
withLearnedRules=False

if len(sys.argv) >= 6:
	sourceLang=sys.argv[4]
	targetLang=sys.argv[5]
	if len(sys.argv) >= 8 and sys.argv[7]=="norule":
		usePreTransfer=True
	if len(sys.argv) >= 8 and sys.argv[7]=="dupdetermined":
		duplicateToBeDetermined=True
		duplicatedLinesFile= sys.argv[1]+".duplications"
	if len(sys.argv) >= 9 and sys.argv[8].startswith("empty"):
		emptymode=True
	if len(sys.argv) >= 10 and sys.argv[9].startswith("learned"):
		withLearnedRules=True

mwlfFile= sys.argv[6]
mwlf=MultiwordLexicalForms()
mwlf.load(mwlfFile)	

separator=u"sep_sentence_expandPTv2_vmsanchez"
splitter = re.compile(re.escape(separator)+r'\n?')

for lex in sys.stdin:
	lex=lex.decode('utf-8').strip()
	if lex.find(u"__REGEXP__") == -1:
		forms=lex.split(u":")
		supform=None
		lexform=None
		
		if len(forms) == 2:
			supform=forms[0]
			lexform=forms[1]
		elif len(forms) ==3:
			if forms[1]==u">":
				supform=forms[0]
				lexform=forms[2]
		
		if supform and lexform:
			lexforms.append(u"^"+lexform+u"$")
			supforms.append(supform)

#if DEBUG:	
#	print >>sys.stderr, str(lexforms)

if len(lexforms) == 0:
	exit(0)

src=(u"^.<sent>$["+separator+u"\n]").join(lexforms)+u"^.<sent>$[]"

if usePreTransfer:
	resultPreTransfer=apertium.preTransfer(src)
	srclist=list()
	ptlist=resultPreTransfer.split(u"\n")
	for line in ptlist:
		pos=0
		matches=-1
		while pos >= 0:
			matches+=1
			pos=line.find("^",pos)
		if matches <= 2:
			srclist.append(line)
	src=u"\n".join(srclist)

if duplicateToBeDetermined:
	mode1=sourceLang+"_lex-"+targetLang+"_step1"
	mode2=sourceLang+"_lex-"+targetLang+"_step2"
	
	if alignments:
		mode1+="_debug"
		mode2+="_debug"

	if emptymode:
		mode1+="_empty"
		mode2+="_empty"
	
	localTranslation=apertium.translate(src,'none',mode1)
	if DEBUG:
		print >> sys.stderr, "step1 translation: "
		print >> sys.stderr, localTranslation.encode("utf-8")

	startDebugTransfer=u"[\[debug-transfer"
	#replace lines with <ND> or <GD>
	patterns=[u"<ND>",u"<GD>",u"<PD>"]
	replacements=[[u"<sg>",u"<pl>"],[u"<m>",u"<f>"],[u"<p1>",u"<p2>",u"<p3>"]]
	curline=-1
	replaced=list()
	replacementsDone=list()
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
			prevPos=mypos+1

		patternFound=False
		if numChunks==2 or emptymode:
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

	#debug		
	#print >>sys.stderr, str(replaced)	

	icounter=len(replaced)-2
	endCondition=False
	while icounter>=0 and not endCondition:
		if replaced[icounter].endswith(u"[]"):
			replaced[icounter]=replaced[icounter][:-1]+separator
		else:
			endCondition=True
		icounter-=1	

	localTranslation2=apertium.translateAndReformat(u"\n".join(replaced),mode2)
	translations=splitter.split(localTranslation2)
	
	if DEBUG:		
		print >>sys.stderr, str(translations)
	
	if len(translations) != len(replaced):
		print >>sys.stderr, "Translations length ("+str(len(translations))+") does not match source length ("+str(len(replaced))+")"
		exit(1)
	
else:
	mode=sourceLang+"_lex-"+targetLang
	if alignments:
		mode+="_debug"
	localTranslation=apertium.translateAndReformat(src,mode)
	translations=splitter.split(localTranslation)
	
	if len(translations) != len(supforms):
		print >>sys.stderr, "Translations length ("+str(len(translations))+") does not match source length ("+str(len(supforms))+")"
		exit(1)

if DEBUG:
	fdsrc=fdtranslation=codecs.open(sys.argv[1]+".debug",encoding='utf-8',mode='w')
	fdsrc.write(src)
	fdsrc.close()

	fdtranslation=codecs.open(sys.argv[2]+".debug",encoding='utf-8',mode='w')
	fdtranslation.write(localTranslation)
	fdtranslation.close()

fsrc=codecs.open(sys.argv[1],encoding='utf-8',mode='w')
fsrclex=codecs.open(sys.argv[1]+".additional",encoding='utf-8',mode='w')
ftarget=codecs.open(sys.argv[2],encoding='utf-8',mode='w')
ftargetlex=codecs.open(sys.argv[2]+".additional",encoding='utf-8',mode='w')
fals=codecs.open(sys.argv[3],encoding='utf-8',mode='w')

if not duplicateToBeDetermined:
	dupsupforms=supforms
	duplexforms=lexforms
else:
	dictrep=dict()
	for r in replacementsDone:
		dictrep[r[0]]=r[1]
	dupsupforms=list()
	duplexforms=[]
	for i in range(len(supforms)):
		if i in dictrep:
			for j in range(dictrep[i]):
				dupsupforms.append(supforms[i])
				duplexforms.append(lexforms[i])
		else:
			dupsupforms.append(supforms[i])
			duplexforms.append(lexforms[i])
			

for i in range(len(dupsupforms)):
	sf=dupsupforms[i]
	fsrc.write(sf.strip()+u"\n")
	lf=duplexforms[i]
        fsrclex.write(lf.strip()+u"\n")


for i in range(len(translations)):
	tr=translations[i]
	if not alignments:
		ftarget.write(tr.strip()[:-1]+u"\n")
	else:
		sf=dupsupforms[i]
		if not duplicateToBeDetermined or withLearnedRules:
			debugInfo = DebugInfo(tr,"",mwlf)
			debugInfo.extractModuleOutputs(True,True)
			debugInfo.extractPreTransferAlignments()
			debugInfo.extractTransferAndGenerationAlignments(withLearnedRules)
			debugInfo.extractPostGenerationAlignments()				
			ftarget.write(debugInfo.translation.strip()+u"\n")
			ftargetlex.write(replaced[i]+u"\n")
			
			alignmentsAnalysis= SentenceAlignments()
			for n in range(len(sf.strip().split())):
				alignmentsAnalysis.alignments.append((n+1,1))
				
			#finalAlignments=SentenceAlignments()
			#finalAlignments.merge([alignmentsAnalysis,debugInfo.alignmentsPreTransfer,debugInfo.alignmentsTransfer,debugInfo.alignmentsGeneration,debugInfo.alignmentsPostGeneration])
			#fals.write(finalAlignments.toStringMinusOne()+u"\n")

			fals.write(u" ||| ".join([alignmentsAnalysis.toString(),debugInfo.alignmentsPreTransfer.toString(),debugInfo.alignmentsTransfer.toString(),debugInfo.alignmentsGeneration.toString(),debugInfo.alignmentsPostGeneration.toString()])+u"\n")						
		else:
			#debug
			#print >>sys.stderr, tr.encode('utf-8')
			debugInfo = DebugInfo(tr,"",mwlf)
			debugInfo.extractModuleOutputs(True,True, True)
			debugInfo.extractPreTransferAlignments()
			debugInfo.extractTransferAndGenerationAlignments2level()
			debugInfo.extractPostGenerationAlignments()
			ftarget.write(debugInfo.translation.strip()+u"\n")
			ftargetlex.write(replaced[i]+u"\n")
			
			alignmentsAnalysis= SentenceAlignments()
			for n in range(len(sf.strip().split())):
				alignmentsAnalysis.alignments.append((n+1,1))
			
			alsList=[alignmentsAnalysis,debugInfo.alignmentsPreTransfer,debugInfo.alignmentsTransfer,debugInfo.alignmentsInterchunk,debugInfo.alignmentsPostchunk,debugInfo.alignmentsGeneration,debugInfo.alignmentsPostGeneration]
			#debug
			#for a in alsList:
			#	print >>sys.stderr, a.toString()
			
			#finalAlignments=SentenceAlignments()
			#finalAlignments.merge(alsList)
			#fals.write(finalAlignments.toStringMinusOne()+u"\n")
			fals.write(u" ||| ".join([alignmentsAnalysis.toString(),debugInfo.alignmentsPreTransfer.toString(),debugInfo.alignmentsTransfer.toString(),debugInfo.alignmentsInterchunk.toString(),debugInfo.alignmentsPostchunk.toString(),debugInfo.alignmentsGeneration.toString(),debugInfo.alignmentsPostGeneration.toString()])+u"\n")

if False:
	for i in range(len(supforms)):
		sf=supforms[i]
		tr=translations[i]
		if not alignments:
			if not( len(sf.strip())==0 or len(tr.strip()[:-1])==0):
				fsrc.write(sf.strip()+u"\n")
				ftarget.write(tr.strip()[:-1]+u"\n")
		else:
			debugInfo = DebugInfo(tr,"",mwlf)
			debugInfo.extractModuleOutputs(True,True)
			debugInfo.extractPreTransferAlignments()
			debugInfo.extractTransferAndGenerationAlignments()
			debugInfo.extractPostGenerationAlignments()
			if not( len(sf.strip())==0 or len(debugInfo.translation.strip())==0):
				fsrc.write(sf.strip()+u"\n")
				ftarget.write(debugInfo.translation.strip()+u"\n")
				
				alignmentsAnalysis= SentenceAlignments()
				for n in range(len(sf.strip().split())):
					alignmentsAnalysis.alignments.append((n+1,1))
					
				finalAlignments=SentenceAlignments()
				finalAlignments.merge([alignmentsAnalysis,debugInfo.alignmentsPreTransfer,debugInfo.alignmentsTransfer,debugInfo.alignmentsGeneration,debugInfo.alignmentsPostGeneration])
				fals.write(finalAlignments.toStringMinusOne()+u"\n")
			
fsrc.close()
ftarget.close()
fals.close()

#if duplicateToBeDetermined:
#	f=open(duplicatedLinesFile,"w")
#	for r in replacementsDone:
#		f.write(str(r[0])+" "+str(r[1])+"\n")
#	f.close()


