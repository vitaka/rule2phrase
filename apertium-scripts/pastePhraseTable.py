#!/usr/bin/python
# coding=utf-8
# -*- encoding: utf-8 -*-

import getopt,sys, codecs;

try:
	opts, args = getopt.getopt(sys.argv[1:], "d:", ["delimiter="])
except getopt.GetoptError, err:
	# print help information and exit:
	print str(err) # will print something like "option -a not recognized"
	usage()
	sys.exit(2)
delimiter=" ||| "
for o, a in opts:
	if o in ("-d","--delimiter"):
		delimiter=a

files=list()
for arg in args:
	f=codecs.open(arg,encoding='utf-8',mode='r')
	files.append(f)

endfile=False

if len(files) > 0:
	while not endfile:
		toprint=list()
		for i in range(len(files)):
			f=files[i]
			line=f.readline()
			if line != u"":
				line=line.strip()
				toprint.append(line)
				if i<len(files)-1:
					toprint.append(delimiter)
			else:
				endfile=True
		if not endfile:
			print u''.join(toprint).encode('utf-8')

for f in files:
	f.close()
