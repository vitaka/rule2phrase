#!/usr/bin/python
# coding=utf-8
# -*- encoding: utf-8 -*-

import sys;

ENCODING='utf-8'

#Load allowed words
def loadAllowedWords(file):
	startingSymbol=u"WORD"
	inWordSection=False
	alWords=set()
	for line in open(file):
		line=line.decode(ENCODING).strip()
		if line.startswith(startingSymbol):
			if not inWordSection:
				inWordSection=True
			alWords.add(line[len(startingSymbol):].strip())
		else:
			if inWordSection:
				break
	return alWords

allowedWords=loadAllowedWords(sys.argv[1])
print >>sys.stderr,str(len(allowedWords))+" words allowed loaded from ngrams"
for line in sys.stdin:
	line=line.decode(ENCODING).strip()
	parts=line.split(u"|||")
	words=parts[0].strip().split(u"--")
	ok=True
	
	#debug
	#print >> sys.stderr, str(parts)
	#print >> sys.stderr, str(words)
	
	for word in words:
		word=word.strip()
		wordLowCase=word[0:1]+word[1:2].lower()+word[2:]
		wordUpCase=word[0:1]+word[1:2].upper()+word[2:]
		if not ( wordLowCase in allowedWords or  wordUpCase in allowedWords):
			#debug
			#print >> sys.stderr, word.strip().encode(ENCODING)+" is not allowed"
			
			ok=False
			break
	if ok:
		print line.encode(ENCODING)
	

