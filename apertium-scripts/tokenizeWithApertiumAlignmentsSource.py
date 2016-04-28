import sys
ENCODING="utf-8"

def fixMultiWordsWithInflection(lexform):
	partsplus=lexform.split(u"+")
	finalpp=[]
	for partp in partsplus:
		if u"#" in partp:
			partsmark=partp.split(u"#")
			if len(partsmark) == 2:
				startTagsI=partsmark[0].find(u"<")
				finalpp.append(partsmark[0][:startTagsI]+u"#"+partsmark[1]+partsmark[0][startTagsI:]  )
			else:
				finalpp.append(partp)
		else:
			finalpp.append(partp)

	return u"+".join(finalpp)

#returns a list of tuples [ (surface1,[lex11,lex12,etc]) , (surface2,[..])  ]
def parseLexicalForms(line):
	returnlist=[]
	partsbystartingsymbol=line.split(u"^")
	for partst in partsbystartingsymbol:
		if len(partst.strip()) > 0:
			partsbyending=partst.split(u"$")
			if len(partsbyending) == 2:
				partsoflexform=partsbyending[0].split(u"/")
				#if not u"<" in partsoflexform[1]:
				#	return []
				returnlist.append( (partsoflexform[0],[  fixMultiWordsWithInflection(lf)  for lf in  partsoflexform[1:] ] )  )
	return returnlist

def parseAllowedAnalysisSL(line):
	returnset=set()
	partsbystartingsymbol=line.split(u"^")
	for partst in partsbystartingsymbol:
		if len(partst.strip()) > 0:
			partsbyending=partst.split(u"$")
			if len(partsbyending) == 2:
				partsoflexform=partsbyending[0].split(u"/")
				for p in  partsoflexform:
					returnset.add(p.lower())
	return returnset

def extractLemmaAndPos(p):
	return p.split(u">")[0]+u">".lower()

def parseAllowedAnalysisTL(line):
	returnset=dict()
	returnsetLemmaAndPos=dict()
	curPos=0
	partsbydebug=line.split("[debug-transfer")
	if len(partsbydebug) > 1:
		usefulpart=partsbydebug[0]
		#now identofy chunks
		partsbychunkstart=usefulpart.split(u"{")
		chunkMode=True
		if len(partsbychunkstart) == 1:
			chunkMode=False
		if chunkMode:
			partsbychunkstart=partsbychunkstart[1:]
		for partcs in partsbychunkstart:
			partsbychunkend = partcs.split("}")
			if len(partsbychunkend) == 2 or ( len(partsbychunkend)==1 and not chunkMode  ):
				insidechunk=partsbychunkend[0]
				#identify lexical forms inside chunk
				partsbystartingsymbol=insidechunk.split(u"^")
				for partst in partsbystartingsymbol:
					partsbyending=partst.split(u"$")
					if len(partsbyending) == 2:
						curPos+=1
						partsoflexform=partsbyending[0].split(u"/")
						for p in  partsoflexform:
							if not p.lower() in returnset:
								returnset[p.lower()]=[]
							returnset[p.lower()].append(curPos)
							ponlylemmaandpos=extractLemmaAndPos(p)
							if not ponlylemmaandpos in returnsetLemmaAndPos:
								returnsetLemmaAndPos[ponlylemmaandpos]=[]
							returnsetLemmaAndPos[ponlylemmaandpos].append(curPos)
	return returnset,returnsetLemmaAndPos

for line in sys.stdin:
	line=line.rstrip("\n").decode(ENCODING)
	parts=line.split("\t")
	#first part is result of analysing input with Apertium
	#second part is output of debug transfer
	
	#we have to print disambiguated first part, ||| plus alignments between output of transfer and what we have analysed
	anLexForms_l=parseLexicalForms(parts[0])
	lexFormsToPosition,lexFormsSimpleToPosition = parseAllowedAnalysisTL(line)
	
	
	usedInputAlignments=set()

	#do alignment!!!!
	outputAlignments=[]
	curIndex=0
	for sf,lflist in anLexForms_l:
		curIndex+=1
		#try exact macth
		exactMatches=[ lexFormsToPosition[lf.lower()]  for lf in lflist if lf.lower() in lexFormsToPosition]
		if len(exactMatches) > 0:
			if len(exactMatches) == 1:
				#onlt one exact match: perfect. choose the first  input token that has not been used yet
				notusedinput=[ i   for i in exactMatches[0] if i not in usedInputAlignments  ]
				if len(notusedinput) > 0:
					outputAlignments.append((notusedinput[0],curIndex))
					usedInputAlignments.add(notusedinput[0])
				else:
					#just use the first input point
					outputAlignments.append((exactMatches[0][0],curIndex))
			else:
				#we have more than one exact match: keeo only the not used inputs
				notusedinputS=set()
				for match in exactMatches:
					notusedinputS|=set([ i   for i in match if i not in usedInputAlignments  ])
				if len(notusedinputS) > 0:
					inputp=min(notusedinputS)
					outputAlignments.append((inputp,curIndex))
					usedInputAlignments.add(inputp)
				else:
					outputAlignments.append((exactMatches[0][0],curIndex))
		else:
			#use approx matches
			approxMatches=[ lexFormsSimpleToPosition[extractLemmaAndPos(lf)]  for lf in lflist if extractLemmaAndPos(lf) in lexFormsSimpleToPosition ]
			notusedinputS=set()
			for match in approxMatches:
				notusedinputS|=set([ i   for i in match if i not in usedInputAlignments  ])
				if len(notusedinputS) > 0:
					inputp=min(notusedinputS)
					outputAlignments.append((inputp,curIndex))
					usedInputAlignments.add(inputp)
				else:
					outputAlignments.append((exactMatches[0][0],curIndex))

	#print output: we are not interested in disambiguating	
	print (u" ".join(u"^"+sf+u"/"+lfs[0]+u"$" for sf,lfs in anLexForms_l)+u" ||| "+u" ".join(unicode(a)+u"-"+unicode(b) for a,b in outputAlignments  )).encode(ENCODING)
	

	
