#!/usr/bin/python
# coding=utf-8
# -*- encoding: utf-8 -*-

import getopt,sys;

try:
	opts, args = getopt.getopt(sys.argv[1:], "f:", ["field="])
except getopt.GetoptError, err:
	# print help information and exit:
	print str(err) # will print something like "option -a not recognized"
	usage()
	sys.exit(2)
field=None
for o, a in opts:
	if o in ("-f","--field"):
		field=a

if field:
	fpieces=field.split(u",")
	fields=[]
	for p in fpieces:
		fields.append(int(p))
	for line in sys.stdin :
		line=line.decode('utf-8').strip()
		pieces=line.split(u"|||")
		for i in range(len(fields)):
			field=fields[i]
			if field <=len(pieces):
				sys.stdout.write(pieces[field-1].strip().encode('utf-8'))
			else:
				print >> sys.stderr, "Line '"+line.encode('utf-8')+"' does not have enough fields ("+str(field)+")"
			if i<len(fields)-1:
				sys.stdout.write(" ||| ")
		print
		
