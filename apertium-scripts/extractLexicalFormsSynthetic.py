#!/usr/bin/python
# coding=utf-8
# -*- encoding: utf-8 -*-

import re,sys,getopt;

pattern=re.compile(r"\^([^$]*)\$")

MAXN=3
ngram=list()

multipleLinesPrefix=None

try:
	opts, args = getopt.getopt(sys.argv[1:], "m:n:", ["multiplelines=","ngramorder=" ])
except getopt.GetoptError, err:
	# print help information and exit:
	print str(err) # will print something like "option -a not recognized"
	sys.exit(2)

for o, a in opts:
	if o in ("-m", "--multiplelines"):
		multipleLinesPrefix=a
	elif o in ("-n", "--ngramorder"):
		MAXN=int(a)
	else:
		assert False, "unhandled option"

numLine=1
for line in sys.stdin:
	line=line.decode('utf-8').strip()
	if multipleLinesPrefix:
		f=open(multipleLinesPrefix+str(numLine),'w')
	if len(line) > 0:
		ngram=[]
		for i in range(MAXN):
			ngram.append(u"NULL")
		matchesiter=pattern.finditer(line)
		for mymatch in matchesiter:
			ngram.append(mymatch.group())
			ngram=ngram[1:]
			print "WORD "+mymatch.group().encode('utf-8')
			for nord in range(2,MAXN+1):
				print str(nord)+"GRAM "+u"---".join(ngram[-nord:]).encode('utf-8')
			#print "TRIGRAM "+u"---".join(ngram[-3:]).encode('utf-8')
			#print "BIGRAM "+u"---".join(ngram[-2:]).encode('utf-8')
			if multipleLinesPrefix:
				f.write("WORD "+mymatch.group().encode('utf-8')+"\n")
				for nord in range(2,MAXN+1):
					f.write(str(nord)+"GRAM "+u"---".join(ngram[-nord:]).encode('utf-8')+"\n")
				#f.write("TRIGRAM "+u"---".join(ngram[-3:]).encode('utf-8')+"\n")
				#f.write("BIGRAM "+u"---".join(ngram[-2:]).encode('utf-8')+"\n")
	if multipleLinesPrefix:
		f.close()
	numLine+=1
