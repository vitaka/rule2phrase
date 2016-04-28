#!/usr/bin/python
# coding=utf-8
# -*- encoding: utf-8 -*-

import sys,re,codecs, gzip

mwd=dict()
dictf=dict()
pattern=re.compile(r"<[a-z]+>")

newFormat=True

if not sys.argv[2]:
	print >>sys.stderr, "Not enough parameters. Aborting"
	exit(1)

useAnalysisMw=False
useGenerationMW=False

if sys.argv[2]=="analysis":
	useAnalysisMw=True
elif sys.argv[2]=="generation":
	useGenerationMW=True
else:
	useAnalysisMw=True
	print >>sys.stderr, "WARNING: Wrong value for parameter 2. It should be 'analysis' or 'generation'. Using 'analysis'"


#if working with new format, open output files in gzip format
if newFormat:
	fmult=gzip.open(sys.argv[1]+"/multiwords-pre.gz",'w')
	flem=gzip.open(sys.argv[1]+"/lemmas-pre.gz",'w')


for lex in sys.stdin:
	lex=lex.decode('utf-8').strip()
	forms=lex.split(u":")
	supform=None
	lexform=None
	analysis=True
	generation=True
	if len(forms) == 2:
		supform=forms[0]
		lexform=forms[1]
	elif len(forms) ==3:
		if forms[1]==u"<":
			supform=forms[0]
			lexform=forms[2]
			analysis=False
		if forms[1]==u">":
			supform=forms[0]
			lexform=forms[2]
			generation=False
	
	if supform and ( (useAnalysisMw and analysis) or (useGenerationMW and generation) ):
		numwords=len(supform.split())
		if numwords >1:
			if newFormat:
				fmult.write("#"+str(numwords)+"\t"+lexform.encode("utf-8")+"\n")
			else:
				if not numwords in mwd:
					mwd[numwords]=[]
				mwd[numwords].append(lexform)
	
	if lexform and ( (useAnalysisMw and analysis) or (useGenerationMW and generation) ):
		match=pattern.search(lexform)
		if match:
			lemma=lexform[:match.start()]
			tag=lexform[match.start():]
			if newFormat:
				flem.write("#"+tag.encode("utf-8")+"\t"+lemma.encode("utf-8")+"\n")
			else:
				if not tag in dictf:
					dictf[tag]=[]
				dictf[tag].append(lemma)

if newFormat:
	fmult.close()
	flem.close()
else:
	if len(dictf)>0:
		f=codecs.open(sys.argv[1]+"/lemmas",encoding='utf-8',mode='w')
		for tag in dictf.keys():
			f.write(u'#'+tag+'\n')
			for lemma in dictf[tag]:
				f.write(lemma+'\n')
		f.close()

	if len(mwd)>0:
		f=codecs.open(sys.argv[1]+"/multiwords",encoding='utf-8',mode='w')
		for numWords in mwd.keys():
			f.write(u'#'+unicode(numWords)+'\n')
			for lex in mwd[numWords]:
				f.write(lex+'\n')
		f.close()

