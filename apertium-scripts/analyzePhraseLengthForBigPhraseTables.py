#!/usr/bin/python
# coding=utf-8
# -*- encoding: utf-8 -*-

import re,sys,gzip;

class DebugMosesSentence:
	def __init__(self):
		self.phraseLengths=list()
		self.phrasesFromApertiumLengths=list()
		self.numPhrasesFromBaseline=0
		self.numUnknownPhrases=0

class DebugMosesTranslation:
	def __init__(self, phraseTable,expandedPhraseTable, ffsource, fftranslation):
		self.sentences=list()
		self.phraseInfoRe=re.compile(r"\|(\d+)-(\d+)\|")
		self.phraseTable=set()
		self.expandedPhraseTable=set()
		self.preloadedInput=set()
		self.preLoadInput(ffsource,fftranslation)
		self.phraseTable=self.loadPhraseTable(phraseTable)
		self.expandedPhraseTable=self.loadPhraseTable(expandedPhraseTable)
		print >> sys.stderr, str(len(self.preloadedInput))+" preloaded phrases. "+str(len(self.phraseTable))+" entries in base phrase table. "+str(len(self.expandedPhraseTable))+" entries in expanded phrase table. "
	
	def loadPhraseTable(self,phraTable):
		myphrasetable=set()
		for line in phraTable:
			line=line.decode('utf-8').strip()
			parts=line.split(u"|||")
			if len(parts) >= 2:
				entry=parts[0].strip()+u" ||| "+parts[1].strip()
				if entry in self.preloadedInput:
					myphrasetable.add(entry)
		return myphrasetable

	def preLoadInput(self, fsource,ftranslation):
		lineSource=fsource.readline()
		lineTranslation=ftranslation.readline()
		while len(lineSource) > 0 and len(lineTranslation)>0:
			lineSource=lineSource.decode('utf-8').strip()
			lineTranslation=lineTranslation.decode('utf-8').strip()
			if len(lineSource) > 0 and len(lineTranslation)>0:
				source=lineSource
				sentence=lineTranslation
				sourceSentenceList=source.strip().split()
				iterator=self.phraseInfoRe.finditer(sentence)
 				prevPos=0
				for match in iterator:
					targetPhrase=sentence[prevPos:match.start()]
					firstSrcWord=int(match.group(1))
					secondSrcWord=int(match.group(2))
					sourcePhrase=u" ".join(sourceSentenceList[firstSrcWord:secondSrcWord+1] )
					tosearch=sourcePhrase+u" ||| "+targetPhrase.strip()
					self.preloadedInput.add(tosearch)
					prevPos=match.end()
 			lineSource=fsource.readline()
 			lineTranslation=ftranslation.readline()

		
	def processSentence(self,source,sentence,newTranslationFile):
		debugSentence = DebugMosesSentence()
		sourceSentenceList=source.strip().split()
		newSentence=list()
		iterator=self.phraseInfoRe.finditer(sentence)
		prevPos=0
		for match in iterator:
			targetPhrase=sentence[prevPos:match.start()]
			newSentence.append(targetPhrase)
			
			firstSrcWord=int(match.group(1))
			secondSrcWord=int(match.group(2))
			numwords=secondSrcWord-firstSrcWord+1
			
			debugSentence.phraseLengths.append(numwords)
			
			sourcePhrase=u" ".join(sourceSentenceList[firstSrcWord:secondSrcWord+1] )
			tosearch=sourcePhrase+u" ||| "+targetPhrase.strip()
			#print >>sys.stderr, "searching: '"+tosearch.encode('utf-8')+"'"
			if tosearch in self.phraseTable:
				debugSentence.numPhrasesFromBaseline+=1
				newSentence.append(match.group())
			else:
				if tosearch in self.expandedPhraseTable:
			 		newSentence.append(u"+"+match.group())
			 		debugSentence.phrasesFromApertiumLengths.append(numwords)
				else:
					debugSentence.numUnknownPhrases+=1
					newSentence.append(u"*"+match.group())
			
			prevPos=match.end()
			
		newSentence.append(sentence[prevPos:])
		
		newTranslationFile.write(u"".join(newSentence).encode('utf-8')+"\n")
		self.sentences.append(debugSentence)
	
	def printFinalStats(self):
		sumLength=0
		sumApertiumLength=0
		numPhrases=0
		numSentence=0
		numBaselinePhrases=0
		numUnknownPhrases=0
		for mosesSentence in self.sentences:
			numBaselinePhrases+=mosesSentence.numPhrasesFromBaseline
			numUnknownPhrases+=mosesSentence.numUnknownPhrases
			sentPhrases=mosesSentence.phraseLengths
			numPhrases+=len(sentPhrases)
			for length in sentPhrases:
				sumLength+=length
			for length in mosesSentence.phrasesFromApertiumLengths:
				sumApertiumLength+=length
			print str(numSentence)+": "+str(len(sentPhrases))+" phrases"
			numSentence+=1
		numApertiumPhrases=numPhrases-numUnknownPhrases-numBaselinePhrases
		print "avg phrases per sentence: "+str(numPhrases*1.0/numSentence)+ ", "+str(numPhrases)+" phrases, "+str(numSentence)+" sentences"
		print "avg phrase length: "+str(sumLength*1.0/numPhrases)+ ", "+str(sumLength)+" total length, "+str(numPhrases)+" total phrases"
		if numApertiumPhrases > 0:
			print "avg Apertium phrase length: "+str(sumApertiumLength*1.0/numApertiumPhrases)+ ", "+str(sumApertiumLength)+" total length, "+str(numApertiumPhrases)+" total phrases"
		else:
			print "No Apertium phrases"
		print "% phrases from baseline phrase table: "+str(numBaselinePhrases*100.0/numPhrases)+"% , "+str(numBaselinePhrases)+" phrases from baseline, "+str(numPhrases)+" total phrases"
		print "% phrases from new phrase table: "+str(numApertiumPhrases*100.0/numPhrases)+"% , "+str((numPhrases-numUnknownPhrases-numBaselinePhrases))+" phrases from new phrase table, "+str(numPhrases)+" total phrases"
		print "% unknown phrases: "+str(numUnknownPhrases*100.0/numPhrases)+"% , "+str(numUnknownPhrases)+" unknown phrases, "+str(numPhrases)+" total phrases"


#test
#debugTranslations.processSentence(u"bla bla|0-1| blo blo|2-2|")
#debugTranslations.printFinalStats()

if __name__ == "__main__":

	sourceFile=sys.argv[1]
	translationFile=sys.argv[2]
	newTranslationFile=sys.argv[3]
	oldPhraseTableFile=sys.argv[4]
	expandedPhraseTableFile=sys.argv[5]

	fsource=open(sourceFile,'r')
	ftranslation=open(translationFile,'r')
	fnewTranlation=open(newTranslationFile,'w')
	fpt=gzip.open(oldPhraseTableFile,'r')
	fept=gzip.open( expandedPhraseTableFile,'r')

	debugTranslations=DebugMosesTranslation(fpt,fept,fsource,ftranslation)

	fsource.close()
	ftranslation.close()
	fsource=open(sourceFile,'r')
	ftranslation=open(translationFile,'r')

	lineSource=fsource.readline()
	lineTranslation=ftranslation.readline()
	while len(lineSource) > 0 and len(lineTranslation)>0:
		lineSource=lineSource.decode('utf-8').strip()
		lineTranslation=lineTranslation.decode('utf-8').strip()
		if len(lineSource) > 0 and len(lineTranslation)>0:
			debugTranslations.processSentence(lineSource,lineTranslation,fnewTranlation)
		lineSource=fsource.readline()
		lineTranslation=ftranslation.readline()
	
	debugTranslations.printFinalStats()
	
	fsource.close()
	ftranslation.close()
	fnewTranlation.close()
	fpt.close()
	fept.close()
