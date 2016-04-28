import re, codecs, sys;

class SentenceAlignments:
	def __init__(self):
		self.alignments=list()

	def parse(self,stralign):
		self.alignments=list()
		alist=stralign.split()
		for a in alist:
			parts=a.strip().split(u"-")
			if len(parts) == 2:
				self.alignments.append(( int(parts[0]) , int(parts[1]) ))

	def wordsAlignedWithTarget(self,targetWord):
		words=list()
		for a in self.alignments:
			if a[1]==targetWord:
				words.append(a[0])
		return words

	def toString(self):
		outlist=list()
		for a in self.alignments:
			outlist.append(unicode(a[0])+u"-"+unicode(a[1]))
		return u" ".join(outlist).strip()

	def toStringMinusOne(self):
		outlist=list()
		for a in self.alignments:
			outlist.append(unicode(a[0]-1)+u"-"+unicode(a[1]-1))
		return u" ".join(outlist).strip()

	def toStringInverse(self):
		outlist=list()
		for a in self.alignments:
			outlist.append(unicode(a[1])+u"-"+unicode(a[0]))
		return u" ".join(outlist).strip()

	def toStringInverseMinusOne(self):
		outlist=list()
		for a in self.alignments:
			outlist.append(unicode(a[1]-1)+u"-"+unicode(a[0]-1))
		return u" ".join(outlist).strip()

	def copy(self):
		copied=SentenceAlignments()
		copied.alignments=list(self.alignments)
		return copied

	def getRuleSegments(self,rules,isowords,als):
		validRuleSegments=list()

		finalRuleWordSets=list()
		finalIsoWordSets=list()
		for rule in rules:
			finalRuleWordSets.append(self.getFinalWords(set(rule),als))

		for word in isowords:
			wordset=set()
			wordset.add(word)
			finalIsoWordSets.append(self.getFinalWords(wordset,als))

		for i in range(len(rules)):
			found=False
			for finalWord in finalRuleWordSets[i]:
				for comparationRuleNum in range(len(rules)):
					if comparationRuleNum != i:
						if finalWord in finalRuleWordSets[comparationRuleNum]:
							found=True
							break

				for isoWordNum in range(len(isowords)):
					if finalWord in finalIsoWordSets[isoWordNum]:
						found=True
						break
				if found:
					break
			if not found:
				ruleSegment=sorted(list( finalRuleWordSets[i]))
				validRuleSegments.append(ruleSegment)
		return validRuleSegments


	def getFinalWords(self,initialWords,als):
		if len(als)==0:
			return initialWords
		else:
			nextAls=als[1:]
			al=als[0]
			nextWords=set()
			for a in al.alignments:
				if a[0] in initialWords:
					nextWords.add(a[1])
			return self.getFinalWords(nextWords,nextAls)

	def merge(self, als, minimum=True):
		if len(als) > 0:
			srcWords=set()
			for a in als[0].alignments:
				srcWords.add(a[0])
			for srcW in srcWords:
				inputset=set()
				inputset.add(srcW)
				finalAl=self.finalAlignment(inputset,als,minimum)
				if minimum:
					if len(finalAl) == 1:
						self.alignments.append((srcW,finalAl.pop()))
				else:
					for fa in finalAl:
						self.alignments.append((srcW,fa))

	def finalAlignment(self,srcs,als,minimum):
		if len(als) <= 0:
			return srcs
		else:
			provisionalTargets=set()
			discardedTargets=set()
			for a in als[0].alignments:
				if a[0] in srcs:
					provisionalTargets.add(a[1])
				else:
					discardedTargets.add(a[1])
			if minimum:
				targets=provisionalTargets - discardedTargets
			else:
				targets=provisionalTargets
			return self.finalAlignment(targets,als[1:],minimum)

class MultiwordLexicalForms:
	def __init__(self):
		self.mwlexforms=dict()

	def load(self, file):
		#print >> sys.stderr, "loading multiword lexical forms ..."
		mwlexforms=self.mwlexforms
		currentNumber=0
		f=codecs.open(file,encoding='utf-8',mode='r')
		line=f.readline()
		while line!=u"":
			line= line.strip()
			if line != u"":
				if line[0] == u'#':
					if currentNumber != 0:
						print  >> sys.stderr, str(currentNumber)+" -> "+str(len(mwlexforms[currentNumber])) +" entries"
					currentNumber=int(line[1:])
					mwlexforms[currentNumber]=set()
				else:
					if currentNumber != 0:
						mwlexforms[currentNumber].add(line)
			line=f.readline()
		f.close()

	def getNumWords(self, lexicalUnit):
		output=1
		for numWords in self.mwlexforms.keys():
			if lexicalUnit in self.mwlexforms[numWords]:
				output=numWords
		return output

# Extract alignments from the Apertium debug information attached to a sentence.
# Provides alignments from the following stages: pretransfer, transfer, generation and postgeneration.
# Analysis alignments must be computed using a different tool
class DebugInfo:
	def __init__(self,apertiumOutput,srcSentence,multiwordTargetLexForms=MultiwordLexicalForms(),removeFromTranslation=[u"."],removeFromDebugPostGen=[u".",u"~."],removeFromDebugTransfer=[u"{transfer-rule sent --^.<sent>$ -- ^0-.<sent>$ transfer-rule}"],removeFromDebugTransfer2level=[u"{transfer-rule sent --^.<sent>$ -- {start-chunk ^0-.<sent>$ end-chunk} transfer-rule}"], removeFromDebugInterchunk=[u"{interchunk-rule fi_frase --^punt<sent>{^.<sent>$}$ -- ^0-punt<sent>{^.<sent>$}$ interchunk-rule}",u"{interchunk-rule punt --^punt<sent>{^.<sent>$}$ -- ^0-punt<sent>{^.<sent>$}$ interchunk-rule}"],removeFromDebugPostchunk=[u"{norule-chunk ^.<sent>$ norule-chunk}",u"{postchunk-rule ^punt<sent>{^.<sent>$}$ -- ^0-.<sent>$ postchunk-rule}"]):
		self.rawtranslation=apertiumOutput
		self.translation=None
		self.debugPreTransfer=None
		self.numPreTransferSrcWords=0
		self.debugTransfer=None
		self.debugPostGen=None
		self.debugPostchunk=None
		self.debugInterchunk=None
		self.removeFromTranslation=removeFromTranslation
		self.removeFromDebugPostGen=removeFromDebugPostGen
		self.removeFromDebugTransfer=removeFromDebugTransfer
		self.removeFromDebugTransfer2level=removeFromDebugTransfer2level
		self.removeFromDebugInterchunk=removeFromDebugInterchunk
		self.removeFromDebugPostchunk=removeFromDebugPostchunk
		self.srcSentence=srcSentence
		self.multiwordTargetLexForms=multiwordTargetLexForms
		self.transferRules=list()
		self.isolatedWords=list()
		self.sourceWords=list()


	#Extracts the debug information from the different Apertium stages
	def extractModuleOutputs(self,searchForPostGen=True,searchForPreTransfer=True, multiLevelTransfer=False, removeDebugTransferEnd=True):
		translation=u""
		debugPreTransfer=u""
		debugTransfer=u""
		debugPostGen=u""
		debugPostchunk=u""
		debugInterchunk=u""

		sepPostGen=u"[debug-postgen",u"debug-postgen]"
		sepTransfer=u"[debug-transfer",u"debug-transfer]"
		sepPreTransfer=u"[debug-pretransfer",u"debug-pretransfer]"
		sepInterchunk=u"[debug-interchunk",u"debug-interchunk]"
		sepPostchunk=u"[debug-postchunk",u"debug-postchunk]"

		rawoutput=self.rawtranslation
		prev=0

#		if searchForPostGen:
#			ps=rawoutput.find(sepPostGen[0],prev)
#		else:
#			ps=rawoutput.find(sepTransfer[0],prev)
#		while ps > -1:
		while True:
			if len(rawoutput[prev:].strip()) == 0:
				break
			translationFound=False
			if searchForPostGen:
				ps=rawoutput.find(sepPostGen[0],prev)
				if ps <0:
					print >> sys.stderr, "Error 1 parsing translation of phrase: "+rawoutput.encode('utf-8')+" From prev: "+rawoutput[prev:].encode('utf-8')
					break
				pe=rawoutput.find(sepPostGen[1],ps+len(sepPostGen[0]))
				if pe <0:
					print >> sys.stderr, "Error 2 parsing translation of phrase: "+rawoutput.encode('utf-8')
					break
				debugPostGen+=rawoutput[ps+len(sepPostGen[0]):pe]
				translation+=rawoutput[prev:ps]
				translationFound=True
				prev=pe+len(sepPostGen[1])

			if multiLevelTransfer:
				ps=rawoutput.find(sepPostchunk[0],prev)
				if ps <0:
					if translationFound:
						print >> sys.stderr, "Error 3 parsing translation of phrase: "+rawoutput.encode('utf-8')
					break
				pe=rawoutput.find(sepPostchunk[1],ps+len(sepPostchunk[0]))
				if pe <0:
					print >> sys.stderr, "Error 4 parsing translation of phrase: "+rawoutput.encode('utf-8')
					break
				debugPostchunk+=rawoutput[ps+len(sepPostchunk[0]):pe]
				if not translationFound:
					translation+=rawoutput[prev:ps]
					translationFound=True
				prev=pe+len(sepPostchunk[1])

				ps=rawoutput.find(sepInterchunk[0],prev)
				if ps <0:
					print >> sys.stderr, "Error 5 parsing translation of phrase: "+rawoutput.encode('utf-8')
					break
				pe=rawoutput.find(sepInterchunk[1],ps+len(sepInterchunk[0]))
				if pe <0:
					print >> sys.stderr, "Error 6 parsing translation of phrase: "+rawoutput.encode('utf-8')
					break
				debugInterchunk+=rawoutput[ps+len(sepInterchunk[0]):pe]
				prev=pe+len(sepInterchunk[1])

			ps=rawoutput.find(sepTransfer[0],prev)
			if ps > -1:
				if not translationFound:
					translation+=rawoutput[prev:ps]
					translationFound=True
				pe=rawoutput.find(sepTransfer[1],ps+len(sepTransfer[0]))
				if pe > -1:
					debugTransfer+=rawoutput[ps+len(sepTransfer[0]):pe]
					prev=pe+len(sepTransfer[1])
					if searchForPreTransfer:
						ps=rawoutput.find(sepPreTransfer[0],prev)
						if ps > -1:
							pe=rawoutput.find(sepPreTransfer[1],ps+len(sepPreTransfer[0]))
							if pe > -1:
								debugPreTransfer+=(u"{ "+rawoutput[ps+len(sepPreTransfer[0]):pe]+u" }")
								prev=pe+len(sepPreTransfer[1])
							else:
								print >> sys.stderr, "Error 7 parsing translation of phrase: "+rawoutput.encode('utf-8')
								break
						else:
							print >> sys.stderr, "Error 8 parsing translation of phrase: "+rawoutput.encode('utf-8')
							break

				else:
					print >> sys.stderr, "Error 9 parsing translation of phrase: "+rawoutput.encode('utf-8')
					break
			else:
				if translationFound:
					print >> sys.stderr, "Error 10 parsing translation of phrase: "+rawoutput.encode('utf-8')
				break

		#print >> sys.stderr, "translation: '"+translation.encode('utf-8')+"' debugTransfer: '"+debugTransfer.encode('utf-8')+"'"

		#TODO: regla que ademas de sent tiene mas cosas
		#remove final dot from the three representations

		translation=translation.strip()
		if len(self.removeFromTranslation)>0:
			longestEnding=u""
			for ending in self.removeFromTranslation:
				if translation.endswith(ending) and len(ending) > len(longestEnding):
					longestEnding=ending
			if len(longestEnding)>0:
				self.translation=translation[:-len(longestEnding)].strip()
			else:
				self.translation=translation.strip()
		else:
			self.translation=translation.strip()

		debugPostGen=debugPostGen.strip()
		if len(self.removeFromDebugPostGen)  > 0:
			longestEnding=u""
			for ending in self.removeFromDebugPostGen:
				if debugPostGen.endswith(ending) and len(ending) > len(longestEnding):
					longestEnding=ending
			if len(longestEnding)>0:
				self.debugPostGen=debugPostGen[:-len(longestEnding)].strip()
			else:
				self.debugPostGen=debugPostGen.strip()
		else:
			self.debugPostGen=debugPostGen.strip()

		debugTransfer=debugTransfer.strip()
		removeFromDebugTransfer=self.removeFromDebugTransfer
		if multiLevelTransfer:
			removeFromDebugTransfer=self.removeFromDebugTransfer2level
		if len(removeFromDebugTransfer) > 0 and removeDebugTransferEnd:
			longestEnding=u""
			for ending in removeFromDebugTransfer:
				if debugTransfer.endswith(ending) and len(ending) > len(longestEnding):
					longestEnding=ending
			if len(longestEnding)>0:
				self.debugTransfer=debugTransfer[:-len(longestEnding)].strip()
			else:
				self.debugTransfer=debugTransfer.strip()
		else:
			self.debugTransfer=debugTransfer.strip()

		debugInterchunk=debugInterchunk.strip()
		if len(self.removeFromDebugInterchunk) > 0:
			longestEnding=u""
			for ending in self.removeFromDebugInterchunk:
				if debugInterchunk.endswith(ending) and len(ending) > len(longestEnding):
					longestEnding=ending
			if len(longestEnding)>0:
				self.debugInterchunk=debugInterchunk[:-len(longestEnding)].strip()
			else:
				self.debugInterchunk=debugInterchunk.strip()
		else:
			self.debugInterchunk=debugInterchunk.strip()

		debugPostchunk=debugPostchunk.strip()
		if len(self.removeFromDebugPostchunk) > 0:
			longestEnding=u""
			for ending in self.removeFromDebugPostchunk:
				if debugPostchunk.endswith(ending) and len(ending) > len(longestEnding):
					longestEnding=ending
			if len(longestEnding)>0:
				self.debugPostchunk=debugPostchunk[:-len(longestEnding)].strip()
			else:
				self.debugPostchunk=debugPostchunk.strip()
		else:
			self.debugPostchunk=debugPostchunk.strip()

		self.debugPreTransfer=debugPreTransfer

	#Extract alignments from pretransfer, transfer (1 level), generation and postgeneration
	def extractAlignments(self):
		self.extractPreTransferAlignments()
		self.extractTransferAndGenerationAlignments()
		self.extractPostGenerationAlignments()

	def extractPreTransferAlignments(self):
		self.alignmentsPreTransfer=SentenceAlignments()
		self.numPreTransferSrcWords=0
		debugPreTransfer=self.debugPreTransfer
		startSent=u"{"
		endSent=u"}"
		limit=u"--"

		numWordsBefore=0
		posstartsentence=debugPreTransfer.find(startSent)
		while posstartsentence > -1:
			poslimit=debugPreTransfer.find(limit,posstartsentence+len(startSent))
			if poslimit > -1:
				posendsentence=debugPreTransfer.find(endSent,poslimit+len(limit))
				if posendsentence > -1:
					self.numPreTransferSrcWords+=int(debugPreTransfer[posstartsentence+len(startSent):poslimit].strip())
					awords=debugPreTransfer[poslimit+len(limit):posendsentence].strip().split()
					aptdict=dict()
					for aw in awords:
						al=aw.split("-")
						if len(al) == 2:
							aptdict[int(al[0])+numWordsBefore]=int(al[1])
					numWordsBefore=self.numPreTransferSrcWords
					posstartsentence=debugPreTransfer.find(startSent,posendsentence+len(endSent))
				else:
					print >> sys.stderr, "Error parsing pretrasnfer info. End of sentence not found"
					break
			else:
				print >> sys.stderr, "Error parsing pretrasnfer info. Limit not found"
				break

		self.numPreTransferSrcWords-=1
		offset=0
		for n in range (1,self.numPreTransferSrcWords+1):
			if n in aptdict.keys():
				numwords=aptdict[n]
				for m in range(numwords):
					self.alignmentsPreTransfer.alignments.append((n,n+offset+m))
				offset+=(numwords-1)
			else:
				self.alignmentsPreTransfer.alignments.append((n,n+offset))


	def extractTransferAndGenerationAlignments(self, withPostTransfer=False):


		sepIsoWord=u"{isolated-word"
		sepRule=u"{transfer-rule"
		sepRuleEnd=u"transfer-rule}"
		patternExtraSrcWords=re.compile(r"\+\d+-")
		patternFirstNumSrcWord=re.compile(r"\d+-")

		alignmentsTransfer=SentenceAlignments()
		alignmentsGeneration=SentenceAlignments()
		currentWord=0
		offset=0
		offsetGeneration=0
		debugTransfer=self.debugTransfer
		pos=debugTransfer.find(u"{")

		#numTransferSourceWords=0

		while pos > -1:
			if debugTransfer[pos:].startswith(sepIsoWord):
				currentWord+=1

				alignmentsTransfer.alignments.append((currentWord,currentWord+offset))
				self.isolatedWords.append(currentWord+offset)

				#Check if target is a multiword unit
				posPretlex=debugTransfer.find(u"--",pos)

				srcword=debugTransfer[pos+len(sepIsoWord):posPretlex]
				self.sourceWords.append(srcword.strip()[1:-1])

				postlex=debugTransfer.find(u"^",posPretlex)
				if postlex > -1:
					posendlex=debugTransfer.find(u"$",postlex)
					if posendlex > -1:
						#w=debugTransfer[postlex+1:posendlex].strip().split()
						w=debugTransfer[postlex+1:posendlex].strip()
						if w.startswith(u"0-"):
							w=w[2:]
						#print >> sys.stderr, "w: "+w.encode('utf-8')
						#numw=len(w)
						numw=self.multiwordTargetLexForms.getNumWords(w)
						wordlow=w[0:1].lower()+w[1:]
						numw2=self.multiwordTargetLexForms.getNumWords(wordlow)
						if numw2 > numw:
							numw=numw2

						for i in range(numw):
							alignmentsGeneration.alignments.append((currentWord+offset,currentWord+offset+offsetGeneration+i))
							#numTransferSourceWords+=1
						offsetGeneration+=(numw-1)
					else:
						print >> sys.stderr, "Error parsing transfer word (2)"
				else:
					print >> sys.stderr, "Error parsing transfer word"

				pos=debugTransfer.find(u"{",pos+1)
			elif debugTransfer[pos:].startswith(sepRule):
				currentWord+=1
				currentRule=list()

				#debug
				#print >>sys.stderr, "Found start rule in pos "+str(pos)+". Current word: "+str(currentWord)

				numTargetWords=0
				numSrcWords=0
				poslimit=debugTransfer.find(u"--",pos+len(sepRule))
				if poslimit > -1:
					poslimit2=debugTransfer.find(u"--",poslimit+2)
					if poslimit2 > -1:
						#identify source words
						srcwords=debugTransfer[poslimit+2:poslimit2]
						#prevpos=0
						#posstartword=srcwords.find(u"^",prevpos)
						#while posstartword > -1:
						#	numSrcWords+=1
						#	prevpos=posstartword
						#	posstartword=srcwords.find(u"^",prevpos+1)
						#numTransferSourceWords+=numSrcWords
						wordslist=self.extractWords(srcwords)
						numSrcWords+=len(wordslist)
						for sw in wordslist:
							self.sourceWords.append(sw.strip()[1:-1])

						#parse target words to find alignments
						poslimit3=debugTransfer.find(sepRuleEnd,poslimit2+2)
						if poslimit3 > -1:
							targetwords=debugTransfer[poslimit2+2:poslimit3]
							prevpos=0
							posstartword=targetwords.find(u"^",prevpos)

							#we store these target lex forms for applying pretransfer
							targetLexFormsForPostTransfer=[]


							while posstartword > -1:
								posendlex=targetwords.find(u"$",posstartword+1)

								if posendlex > -1:
									if not withPostTransfer:
										numTargetWords+=1
									else:
										#check that this is not an enclitic pronoun preceeded by verb
										iamenclitic=(targetwords[posstartword:posendlex].find(u"<prn><enc>") >= 0)
										if not iamenclitic:
											numTargetWords+=1
										else:
											#TODO: WARNING!!!! DANGER!!! check previous lex form. This WILL FAIL if the enclitic and the verb are processed by different rules
											if len(targetLexFormsForPostTransfer) < 1:
												numTargetWords+=1
											else:
												positionOfVerb=-1
												if targetLexFormsForPostTransfer[-1].find(u"<prn><enc>") >= 0 and len(targetLexFormsForPostTransfer) >=2 :
													positionOfVerb=-2
												if not (targetLexFormsForPostTransfer[positionOfVerb].find(u"<vblex>") >= 0 or targetLexFormsForPostTransfer[positionOfVerb].find(u"<vbmod>") >= 0 or targetLexFormsForPostTransfer[positionOfVerb].find(u"<vbhaver>") >= 0 or targetLexFormsForPostTransfer[positionOfVerb].find(u"<vaux>") >= 0 or targetLexFormsForPostTransfer[positionOfVerb].find(u"<vbser>") >= 0) :
													 numTargetWords+=1


									#debug
									#print >> sys.stderr, "NumTargetWords="+str(numTargetWords)

									#find source word number

									matchObject=patternFirstNumSrcWord.match(targetwords[posstartword+1:])
									if matchObject:
										number=int(matchObject.group()[:-1])
										alignmentsTransfer.alignments.append((currentWord+number,currentWord+numTargetWords-1+offset))
										currentRule.append(currentWord+numTargetWords-1+offset)

								if posendlex > -1:

									targetWordWithoutDebugMarks=list()

									#Find more source words in the current target word
									posstartsearch=posstartword+1
									if matchObject:
										posstartsearch+=len(matchObject.group())
									mymatch=patternExtraSrcWords.search(targetwords[posstartsearch:])
									while mymatch!=None and mymatch.start()+posstartsearch < posendlex:
										targetWordWithoutDebugMarks.append(targetwords[posstartsearch:posstartsearch+mymatch.start()+1])
										number=int(mymatch.group()[1:-1])
										alignmentsTransfer.alignments.append((currentWord+number,currentWord+numTargetWords-1+offset))
										posstartsearch=posstartsearch+mymatch.end()
										mymatch=patternExtraSrcWords.search(targetwords[posstartsearch:])
									targetWordWithoutDebugMarks.append(targetwords[posstartsearch:posendlex])

									#Check if target is a multiword unit
									w=u"".join(targetWordWithoutDebugMarks)

									targetLexFormsForPostTransfer.append(w)

									#print >>sys.stderr, "multiword: "+w.encode('utf-8')
									numw=self.multiwordTargetLexForms.getNumWords(w)
									wordlow=w[0:1].lower()+w[1:]
									numw2=self.multiwordTargetLexForms.getNumWords(wordlow)

									if numw2 > numw:
										numw=numw2

									#w=targetwords[posstartword:posendlex].strip().split()
									#numw=len(w)

									#debug
									#print >> sys.stderr,"target: "+targetwords[posstartword:posendlex].strip().encode('utf-8')+" numw="+str(numw)

									for i in range(numw):
										newAlignmentGeneration=(currentWord+numTargetWords-1+offset,currentWord+numTargetWords-1+offset+offsetGeneration+i)
										if not newAlignmentGeneration in alignmentsGeneration.alignments:
											alignmentsGeneration.alignments.append(newAlignmentGeneration)
									offsetGeneration+=(numw-1)

								else:
									print >> sys.stderr, "Error parsing transfer word (2)"

								prevpos=posstartword
								posstartword=targetwords.find(u"^",prevpos+1)
							#DEBUG:
							print >> sys.stderr, "Target lexical forms generated by rule: "+u" ".join(targetLexFormsForPostTransfer).encode('utf-8')

						else:
							print >> sys.stderr, "Error parsing transfer-rule (3)"

					else:
						print >> sys.stderr, "Error parsing transfer-rule (2)"

				else:
					print >> sys.stderr, "Error parsing transfer-rule"

				self.transferRules.append(currentRule)
				#print >> sys.stderr, "Processed rule starting at:"+debugTransfer[pos:].encode('utf-8')
				#print >> sys.stderr, "numsrc="+str(numSrcWords)+" numtarget="+str(numTargetWords)+" offset="+str(offset)

				offset-=numSrcWords-numTargetWords
				currentWord+=numSrcWords-1
				pos=debugTransfer.find(u"{",poslimit3+len(sepRuleEnd))

			else:
				pos=debugTransfer.find(u"{",pos+1)

		self.alignmentsTransfer=alignmentsTransfer
		self.alignmentsGeneration=alignmentsGeneration
		#self.numTransferSourceWords=numTransferSourceWords

	def extractTransferAndGenerationAlignments2level(self):
		transferAls, chunkAls=self.extractTransferAlignments2level()
		interchunkAls=self.extractInterchunkAlignments2level()
		postInputChunks,postchunkAls,generationAls=self.extractPostChunkAlignments2level()

		self.alignmentsTransfer=transferAls
		self.alignmentsInterchunk=self.getInterchunkWordAlignments(chunkAls,interchunkAls,postInputChunks)
		self.alignmentsPostchunk=postchunkAls
		self.alignmentsGeneration=generationAls

		#debug
		#print >> sys.stderr, "chunks list: "+ str(chunkAls)
		#print >> sys.stderr, "interchunk als (between chunks): "+ interchunkAls.toString().encode('utf-8')

		self.tranferAls=transferAls
		self.chunkAls=chunkAls
		self.interAls=interchunkAls
		self.postAls=postchunkAls

	def getInterchunkWordAlignments(self, chunkAls, interchunkAls,postInputChunks):
		iwals=SentenceAlignments()

		#debug
		#print >> sys.stderr, "Calculating interhcunk als :"+self.rawtranslation.encode('utf-8')+" extracted debug transfer<-- "+self.debugTransfer.encode('utf-8')+" --> "+" extracted debug interhcunk<-- "+self.debugInterchunk.encode('utf-8')+" --> "+str(chunkAls)+" "+interchunkAls.toString().encode('utf-8')

		for al in interchunkAls.alignments:

			startingTargetPos=0
			postInputChunksPos=al[1]-1
			for i in range(postInputChunksPos):
				startingTargetPos+=postInputChunks[i]
			prePos=al[0]-1
			j=0
			if len(chunkAls) > prePos:
				for s in chunkAls[prePos]:
					j+=1
					iwals.alignments.append((s,startingTargetPos+j))
			else:
				print >>sys.stderr, "Error: chunk referenced by interchunk alignment does not exist"
				print >> sys.stderr, self.rawtranslation.encode('utf-8')
				print >> sys.stderr, self.debugTransfer.encode('utf-8')


		if False:
			targetChunks=list()
			currentTargetPos=1

			for al in interchunkAls.alignments:
				wordsBelongToChunk=chunkAls[al[0]-1]
				targetChunkNum=al[1]
				if len(targetChunks)<targetChunkNum:
					for i in range(targetChunkNum-len(targetChunks)):
						targetChunks.append(list())
				for w in wordsBelongToChunk:
					targetChunks[targetChunkNum-1].append(w)

			currentTargetWord=1
			for chunk in targetChunks:
				for srcw in chunk:
					iwals.alignments.append((srcw,currentTargetWord))
					currentTargetWord+=1

		return iwals


	def extractPostChunkAlignments2level(self):
		sepRule=u"{postchunk-rule"
		sepRuleEnd=u"postchunk-rule}"
		sepIsoWord=u"{norule-chunk"
		sepIsoWordEnd=u"norule-chunk}"

		patternChunkHead=re.compile(r"\^[A-Za-z0-9_-]+(<[A-Za-z0-9_@]+>)+{")

		inputChunks=list()
		postAlignments=SentenceAlignments()
		generationAlignments=SentenceAlignments()

		localdebug=self.debugPostchunk

		currentSrcWord=1
		currentTargetWord=1
		currentGeneratedWord=1

		while True:
			#search {
			pos=localdebug.find(u"{")

			if pos <0:
				break

			localdebug=localdebug[pos:]

			if localdebug.startswith(sepRule):
				posEnd=localdebug.find(sepRuleEnd,len(sepRule))
				if posEnd < 0:
					print >> sys.stderr, "Error parsing 5 interchunk"
					break

				posStartWords=localdebug.find(u"{",1)
				if posStartWords < 0:
					print >> sys.stderr, "Error 6 parsing postchunk"
					break

				posEndWords=localdebug.find(u"}", posStartWords+1)
				if posEndWords < 0:
					print >> sys.stderr, "Error 7 parsing postchunk"
					break

				srcwords=self.extractWords(localdebug[posStartWords+1:posEndWords])
				inputChunks.append(len(srcwords))

				posStartTargetWords=localdebug.find(u"--",posEndWords)
				if posStartTargetWords < 0:
					print >> sys.stderr, "Error 8 parsing postchunk"
					break

				targetWordsStr=localdebug[posStartTargetWords+len(u"--"):posEnd]

				targetWordAls, targetWordsWithoutMarks = self.extractTargetWords(targetWordsStr)

				for i in range(len(targetWordAls)):
					t=targetWordAls[i]
					for srcw in t:
						postAlignments.alignments.append((currentSrcWord+srcw,currentTargetWord+i))

					twnomarks=targetWordsWithoutMarks[i]
					numw=self.multiwordTargetLexForms.getNumWords(twnomarks.strip())
					wordlow=twnomarks.strip()[0:1].lower()+twnomarks.strip()[1:]
					numw2=self.multiwordTargetLexForms.getNumWords(wordlow)

					#debug
					#print >>sys.stderr, "Checking multiword 1:'"+twnomarks.encode('utf-8')+"': "+str(numw)
					#print >>sys.stderr, "Checking multiword 1:'"+wordlow.encode('utf-8')+"': "+str(numw2)

					if numw2 > numw:
						numw=numw2

					for j in range(numw):
						generationAlignments.alignments.append((currentTargetWord+i,currentGeneratedWord+j))
					currentGeneratedWord+=numw

				currentSrcWord+=len(srcwords)
				currentTargetWord+=len(targetWordAls)

				localdebug=localdebug[posEnd+len(sepRuleEnd):]

			elif localdebug.startswith(sepIsoWord):


#				posStartWords=localdebug.find(u"{")
#				if posStartWords < 0:
#					print >> sys.stderr, "Error 2 parsing postchunk"
#					break
#				posEndWords=localdebug.find(u"{", posStartWords-1)
#				if posEndWords < 0:
#					print >> sys.stderr, "Error 3 parsing postchunk"
#					break

				posEnd=localdebug.find(sepIsoWordEnd,len(sepIsoWord))
				if posEnd < 0:
					print >> sys.stderr, "Error parsing 4 interchunk"
					break

				words=self.extractWords(localdebug[len(sepIsoWord):posEnd])
				inputChunks.append(len(words))

				for i in range(len(words)):
					postAlignments.alignments.append((currentSrcWord+i,currentTargetWord+i))
					word=words[i]
					if word != u"^$":
						wordlow=word.strip()[1:2].lower()+word.strip()[2:-1]
						numw=self.multiwordTargetLexForms.getNumWords(word.strip()[1:-1])
						numw2=self.multiwordTargetLexForms.getNumWords(wordlow)
						#debug
						#print >>sys.stderr, "Checking multiword 2:'"+word.encode('utf-8')+"': "+str(numw)
						#print >>sys.stderr, "Checking multiword 2:'"+wordlow.encode('utf-8')+"': "+str(numw2)

						if numw2 > numw:
							numw=numw2

						for j in range(numw):
							generationAlignments.alignments.append((currentTargetWord+i,currentGeneratedWord))
							currentGeneratedWord+=1

				currentSrcWord+=len(words)
				currentTargetWord+=len(words)

				localdebug=localdebug[posEnd+len(sepIsoWordEnd):]

			else:
				print >> sys.stderr, "Error 1 parsing postchunk"
				break
		return inputChunks,postAlignments,generationAlignments

	def extractInterchunkAlignments2level(self):
		sepRule=u"{interchunk-rule"
		sepRuleEnd=u"interchunk-rule}"
		sepIsoWord=u"{isolated-word"
		sepIsoWordEnd=u"isolated-word}"

		patternChunkHead=re.compile(r"\^(\d+-)?[A-Za-z0-9_-]+(<[A-Za-z0-9_@]+>)+{")

		interAlignments=SentenceAlignments()

		localdebug=self.debugInterchunk

		currentSrcChunk=1
		currentTargetChunk=1

		while True:
			#search {
			pos=localdebug.find(u"{")

			#debug
			#print >> sys.stderr, str(pos)

			if pos <0:
				break
			localdebug=localdebug[pos:]
			if localdebug.startswith(sepRule):

				#Process interchunk rule
				posFirstSeparator=localdebug.find(u"--")
				if posFirstSeparator < 0:
					print >> sys.stderr, "Error 1 parsing interchunk"
					break
				posSecondSeparator=localdebug.find(u"--",posFirstSeparator+len(u"--"))
				if posSecondSeparator < 0:
					print >> sys.stderr, "Error 2 parsing interchunk"
					break

				posEnd=localdebug.find(sepRuleEnd,len(sepRule))
				if posEnd < 0:
					print >> sys.stderr, "Error 3 parsing interchunk"
					break

				sourceChunksStr=localdebug[posFirstSeparator+len(u"--"):posSecondSeparator]
				targetChunksStr=localdebug[posSecondSeparator+len(u"--"):posEnd]

				#debug
				#print >> sys.stderr, sourceChunksStr.encode('utf-8')+" -> "+targetChunksStr.encode('utf-8')

				numSrcChunks=0
				#paste
				posstartsearch=0
				mymatch=patternChunkHead.search(sourceChunksStr[posstartsearch:])
				while mymatch!=None:
					#debug
					#print >> sys.stderr, "src match: "+mymatch.group().encode('utf-8')
					numSrcChunks+=1
					posstartsearch=posstartsearch+mymatch.end()
					mymatch=patternChunkHead.search(sourceChunksStr[posstartsearch:])
				#paste

				numTargetChunks=0
				#paste
				posstartsearch=0
				mymatch=patternChunkHead.search(targetChunksStr[posstartsearch:])
				while mymatch!=None:
					#debug
					#print >> sys.stderr, "target match: "+mymatch.group().encode('utf-8')
					numTargetChunks+=1
					if mymatch.group(1):
						number=int(mymatch.group(1)[:-1])
						interAlignments.alignments.append((currentSrcChunk+number,currentTargetChunk+numTargetChunks-1))
					posstartsearch=posstartsearch+mymatch.end()
					mymatch=patternChunkHead.search(targetChunksStr[posstartsearch:])
				#paste

				currentSrcChunk+=numSrcChunks
				currentTargetChunk+=numTargetChunks

				localdebug=localdebug[posEnd+len(sepRuleEnd):]

			elif localdebug.startswith(sepIsoWord):

				#Process interchunk iso word

				interAlignments.alignments.append((currentSrcChunk,currentTargetChunk))
				currentSrcChunk+=1
				currentTargetChunk+=1

				posEnd=localdebug.find(sepIsoWordEnd,len(sepIsoWord))
				if posEnd < 0:
					print >> sys.stderr, "Error parsing 4 interchunk"
					break

				#debug
				#print >> sys.stderr, localdebug[:posEnd]

				localdebug=localdebug[posEnd+len(sepIsoWordEnd):]
			else:
				print >> sys.stderr, "Error 5 parsing interchunk"
				break

		return interAlignments

	def extractTransferAlignments2level(self):
		sepRule=u"{transfer-rule"
		sepRuleEnd=u"transfer-rule}"
		sepStartChunk=u"{start-chunk"
		sepEndChunk=u"end-chunk}"

		patternExtraSrcWords=re.compile(r"\+\d+-")
		patternFirstNumSrcWord=re.compile(r"\d+-")

		localdebug=self.debugTransfer

		currentWordNumber=1
		currentTargetWordNumber=1

		transferals=SentenceAlignments()
		chunkAls=list()

		while True:
			#{transfer-rule
			if not localdebug:
				break
			pos=localdebug.find(sepRule)
			if pos<0:
				break

			#source words
			pos=localdebug.find(u"--",pos+len(sepRule))
			if pos<0:
				print >> sys.stderr, "Error parsing transfer-rule"
				break

			#end source words
			posEndSrcWords=localdebug.find(u"--",pos+len(u"--"))
			if posEndSrcWords<0:
				print >> sys.stderr, "Error parsing transfer-rule"
				break

			srcwords=localdebug[pos+len(u"--"):posEndSrcWords]
			wordslist=self.extractWords(srcwords)
			for sw in wordslist:
				self.sourceWords.append(sw.strip()[1:-1])

			#debug
			#print >> sys.stderr, "Src words list: "+str(wordslist)

			#process generated chunks
			posEndRule=localdebug.find(sepRuleEnd,posEndSrcWords+len(u"--"))
			if posEndRule<0:
				print >> sys.stderr, "Error parsing transfer-rule"
				break
			targetwords=localdebug[posEndSrcWords+len(u"--"):posEndRule]


			while True:
				posStartChunk=targetwords.find(sepStartChunk)
				if posStartChunk < 0:
					break

				posEndChunk=targetwords.find(sepEndChunk,posStartChunk+len(sepStartChunk))
				if posEndChunk < 0:
					print >> sys.stderr, "Error parsing transfer-rule"
					break

				curChunk=list()
				chunkTargetWords=targetwords[posStartChunk+len(sepStartChunk):posEndChunk]

				#process words from chunk
				twlist,twwordsWithoutMarks=self.extractTargetWords(chunkTargetWords)

				currentTargetWordIncrement=0
				for i in range(len(twlist)):
					w=twlist[i]
					twithoutdmarks=twwordsWithoutMarks[i]

					#debug
					#print >> sys.stderr, twithoutdmarks.encode('utf-8')
					if twithoutdmarks != u"":
						for w2 in w:
							transferals.alignments.append((w2+currentWordNumber,currentTargetWordIncrement+currentTargetWordNumber))
						curChunk.append(currentTargetWordIncrement+currentTargetWordNumber)
						currentTargetWordIncrement+=1

				currentTargetWordNumber+=currentTargetWordIncrement

				chunkAls.append(curChunk)
				targetwords=targetwords[posEndChunk+len(sepEndChunk):]

			localdebug=localdebug[posEndRule+len(sepRuleEnd):]
			currentWordNumber+=len(wordslist)

		return transferals,chunkAls

	#Returns list of lists
	#return[i] contains a list of the source words aligned with the target word in the
	#position i of the chunk (starting with 0)
	def extractTargetWords(self, targetwords):
		patternExtraSrcWords=re.compile(r"\+\d+-")
		patternFirstNumSrcWord=re.compile(r"\d+-")

		twordsWithoutMarks=list()
		twords=list()
		prevpos=0
		posstartword=targetwords.find(u"^",prevpos)
		while posstartword > -1:

			curTargetWord=list()

			#debug
			#print >> sys.stderr, "NumTargetWords="+str(numTargetWords)

			#find source word number
			matchObject=patternFirstNumSrcWord.match(targetwords[posstartword+1:])
			posendlex=targetwords.find(u"$",posstartword+1)
			if matchObject:
				number=int(matchObject.group()[:-1])
				curTargetWord.append(number)

			if posendlex > -1:

				targetWordWithoutDebugMarks=list()

				#Find more source words in the current target word
				posstartsearch=posstartword+1
				if matchObject:
					posstartsearch+=len(matchObject.group())
				mymatch=patternExtraSrcWords.search(targetwords[posstartsearch:])
				while mymatch!=None and mymatch.start()+posstartsearch < posendlex:
					targetWordWithoutDebugMarks.append(targetwords[posstartsearch:posstartsearch+mymatch.start()+1])
					number=int(mymatch.group()[1:-1])
					curTargetWord.append(number)
					posstartsearch=posstartsearch+mymatch.end()
					mymatch=patternExtraSrcWords.search(targetwords[posstartsearch:])

				targetWordWithoutDebugMarks.append(targetwords[posstartsearch:posendlex])

				twordsWithoutMarks.append(u''.join(targetWordWithoutDebugMarks))
				#targetWordWithoutDebugMarks es una lista que, al unirla, contiene la palabra en
				#lengua meta sin marcas de alineamiento


			else:
				print >> sys.stderr, "Error parsing transfer word (2)"

			twords.append(curTargetWord)
			prevpos=posstartword
			posstartword=targetwords.find(u"^",prevpos+1)

		return twords,twordsWithoutMarks

	def extractWords(self, srcwords):
		words=list()
		prevpos=0
		posstartword=srcwords.find(u"^",prevpos)
		while posstartword > -1:

			prevpos=posstartword
			posstartword=srcwords.find(u"^",prevpos+1)
			if posstartword> -1:
				words.append(srcwords[prevpos:posstartword])
			else:
				words.append(srcwords[prevpos:])

		return words

	def extractPostGenerationAlignments(self):
		alignmentsPostGeneration=SentenceAlignments()
		psrcwords=self.debugPostGen.strip().split()
		ptargetwords=self.translation.strip().split()

		offset=0
		i=0
		while i < len(psrcwords):
			#debug#
			#print>> sys.stderr, "i="+str(i)+" offset="+str(offset)+" word="+psrcwords[i].encode('utf-8')+" target="+ptargetwords[i+offset].encode('utf-8')
			##
			possymbol=psrcwords[i].find(u"~")
			#if psrcwords[i].startswith(u"~"):
			if possymbol>-1:
				#if psrcwords[i][1:] == ptargetwords[i+offset]:
				if psrcwords[i][:possymbol]+psrcwords[i][possymbol+1:] == ptargetwords[i+offset]:
					alignmentsPostGeneration.alignments.append((i+1,i+1+offset))
					i+=1
				else:
					#Asumo que todas las palabras que empiezan por ~ se juntan con la siguiente que no empieza por ~
					#Si hay 3, o se juntan todos o no se junta ninguna, pero
					#no se puedne juntar, por ejemplo, las 2 primeras
					j=0
					while True:
						j+=1
						repeat=False
						if i+j < len(psrcwords):
							if psrcwords[i+j-1].find(u"~") > -1:
								comparationWord=psrcwords[i+j]
								comparationWord2=u""
								if(i+j+1 < len(psrcwords)):
									if psrcwords[i+j+1].find(u"~")==-1:
										comparationWord2=psrcwords[i+j+1]
								possymbol2=comparationWord.find(u"~")
								if possymbol2>-1:
									comparationWord=comparationWord[:possymbol2]+comparationWord[possymbol2+1:]
								if len(ptargetwords)<=i+offset+1 or comparationWord != ptargetwords[i+offset+1] or (comparationWord2 !=u"" and comparationWord2!=ptargetwords[i+offset+2] ):
									repeat=True
						if not repeat:
							break

					for r in range(j):
						alignmentsPostGeneration.alignments.append((i+1+r,i+1+offset))
					offset-=j-1
					i+=j

			elif psrcwords[i]==ptargetwords[i+offset]:
				alignmentsPostGeneration.alignments.append((i+1,i+1+offset))
				i+=1
			else:
				print >> sys.stderr, "Error calculating post-generation alignments"
				i+=1
		self.alignmentsPostGeneration=alignmentsPostGeneration

	def extractAnalysisAlignments(self, smwlf):
		analysisAlignments=SentenceAlignments()
		offset=0
		for i in range(len(self.sourceWords)):
			w=self.moveHash(self.sourceWords[i])
			#print >> sys.stderr, w.encode('utf-8')
			numw=smwlf.getNumWords(w)
			wordlow=w[0:1].lower()+w[1:]
			numw2=smwlf.getNumWords(wordlow)
			if numw2> numw:
				numw=numw2
			for j in range(numw):
				analysisAlignments.alignments.append((i+1+offset+j,i+1))
			offset+=(numw-1)
		self.alignmentsAnalysis=analysisAlignments

	def moveHash(self,lexicalForm):
		posHash=lexicalForm.find(u"#")
		if posHash>=0:
			posStartTags=lexicalForm.find(u"<")
			modifiedStr=lexicalForm[:posHash]+lexicalForm[posStartTags:]+u"#"+lexicalForm[posHash+1:posStartTags]
			return modifiedStr
		else:
			return lexicalForm

def languageSpecificPostProcess(language, translation):
	if language == "fin":
		tp=translation
		#be careful with "/" in translations
		if u"/" in tp:
			partsSlash=tp.strip().split(u"/")
			#all the parts must contain the same number of words
			prevNumWords=None
			match=True
			for part in partsSlash:
				numWords=len(part.split(u" "))
				if prevNumWords != None:
					if numWords != prevNumWords:
						match=False
						break
				prevNumWords=numWords
			if match:
				#if all the parts contain the same number of words, choose the shortest part
				shortestAlt=partsSlash[0]
				for part in partsSlash[1:]:
					if len(part) < len(shortestAlt):
						shortestAlt=part
				tp=shortestAlt
			else:
				tp=u""
		return tp
	else:
		return translation
