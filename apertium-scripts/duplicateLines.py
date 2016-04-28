#!/usr/bin/python
# coding=utf-8
# -*- encoding: utf-8 -*-

import re, sys, string,  getopt;

duplicatedLinesFile=""

try:
	opts, args = getopt.getopt(sys.argv[1:], "d:h", ["duplicatedLinesFile=","help"])
except getopt.GetoptError, err:
	# print help information and exit:
	print str(err) # will print something like "option -a not recognized"
	usage()
	sys.exit(2)

for o, a in opts:
	if o in ("-h", "--help"):
		usage()
		sys.exit()
	elif o in ("-d", "--duplicatedLinesFile"):
		duplicatedLinesFile=a
	else:
		assert False, "unhandled option"

dupLines=dict()

for line in open(duplicatedLinesFile):
	parts=line.split()
	if len(parts)==2:
		dupLines[int(parts[0])]=int(parts[1])

print >>sys.stderr, str(len(dupLines))+" duplicated lines"

lineNumber=-1
for line in sys.stdin:
	lineNumber+=1
	if lineNumber in dupLines:
		for i in range(dupLines[lineNumber]):
			print line.strip()
	else:
		print line.strip()
