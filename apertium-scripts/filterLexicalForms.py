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
prefixFilteringStr=sys.argv[2]

if prefixFilteringStr == "prefix":
	prefixFiltering=True
else:
	prefixFiltering=False

print >>sys.stderr,str(len(allowedWords))+" words allowed loaded from ngrams"
for line in sys.stdin:
	line=line.decode(ENCODING).strip()
	lineLowCase=line[0:1]+line[1:2].lower()+line[2:]
	lineUpCase=line[0:1]+line[1:2].upper()+line[2:]
	if prefixFiltering:
		lineLowCaseClean=lineLowCase[1:-1]
		lineUpCaseClean=lineUpCase[1:-1]
		for allowedWord in allowedWords:
			if allowedWord.startswith(u"^"+lineLowCaseClean) or allowedWord.startswith(u"^"+lineUpCaseClean):
				print allowedWord.encode(ENCODING)
	else:
		if lineLowCase in allowedWords or lineUpCase in allowedWords:
			print line.encode(ENCODING)
	
