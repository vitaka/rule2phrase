#!/usr/bin/python
# coding=utf-8
# -*- encoding: utf-8 -*-

import getopt,sys,subprocess;
from expandPTLib import *

ENC='utf-8'

dupFile=sys.argv[1]
als=True
if len(sys.argv)>=3 and sys.argv[2]=="noals":
	als=False

replacementsDone=list()
curLine=-1
for line in sys.stdin:
	curLine+=1
	line=line.decode(ENC).strip()
	parts=line.split(u" ||| ")
	surfaceForms=parts[0].strip()
	words=surfaceForms.split(u"[sep_word_vmsanchez_e][sep_word_vmsanchez_s]")[1:]
	alternativess=list()
	for word in words:
		alternatives=list()
		for alternative in word.split(u"/"):
			if alternative.strip().find(u"~")<0:
				alternatives.append(alternative.strip())
		alternativess.append(alternatives)
	generatedLines=1
	for alternatives in alternativess:
		generatedLines= generatedLines*len(alternatives)

	if generatedLines > 1:
		replacementsDone.append((curLine,generatedLines))

	for alt in range(generatedLines):
		denominator=1
		sentence=list()
		for i in range(len(alternativess)):
			setsize=len(alternativess[i])
			index=(alt/denominator)%setsize
			sentence.append(alternativess[i][index])
			denominator=denominator*setsize

		alignmentsAnalysis=SentenceAlignments()
		offset=0
		for i in range(len(sentence)):
			numwords=len(sentence[i].strip().split())
			for j in range(numwords):
				alignmentsAnalysis.alignments.append((i+1+offset+j,i+1))
			offset+=(numwords-1)
		if als:
			print u" ".join(sentence).encode(ENC)+" ||| "+alignmentsAnalysis.toString().encode(ENC)+" ||| "+u" ||| ".join(parts[2:]).encode(ENC)
		else:
			print u" ".join(sentence).encode(ENC)
f=open(dupFile,"w")
for r in replacementsDone:
	f.write(str(r[0])+" "+str(r[1])+"\n")
f.close()
