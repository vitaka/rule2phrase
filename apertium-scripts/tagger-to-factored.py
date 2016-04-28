#!/usr/bin/python3
# coding=utf-8
# -*- encoding: utf-8 -*-

# Convert a file tagged with the apertium-tagger -p -g to the factored
# format required by Moses

# Copyright (c) 2009-2013 Francis Tyers, released under the GNU GPL.
import sys;

class SimpleBufferedReader:
	def __init__(self):
		self.buffer=[]
	def read(self):
		if len(self.buffer) == 0:
			return sys.stdin.read(1)
		else:
			rvalue=self.buffer[0]
			self.buffer=self.buffer[1:]
			return rvalue
	def unread(self,c):
		self.buffer.append(c)

n_tags = -1;

if len(sys.argv) == 2: #{
	try: #{
		n_tags = int(sys.argv[1]);
	except: #{
		print('tagger-to-factored.py NUMTAGS');
		print('Values for NUMTAGS:');
		print('  0: No tags, just lemmatisation (2 factors)');
		print('  1: Only first (POS) tag (3 factors)');
		print(' >1: First (POS) tag and NUMTAGS morphological tags (4 factors)');
		print('Default is to print out all tags');
		
		sys.exit(-1);
	#}
#}


reader=SimpleBufferedReader()
#c = sys.stdin.read(1);
c= reader.read()

# Process a lexical unit, examples:
#
#  1. ^zadoù/tad<n><m><sg>$
#  2. ^mont da get/mont<vblex><inf># da get$
#  3. ^mat-tre/mat<adj><mf><sp>+tre<adv>$
#
def processWord(c, _tags): #{
	superficial = '';
	lemma = '';
	analysis = '';
	tags = '';
	unknown = False;

	#c = sys.stdin.read(1);
	c= reader.read()
	while c != '/': #{
		superficial = superficial + c;
		#c = sys.stdin.read(1);
		c= reader.read()
	#}

	superficial = superficial.replace(' ', '~');

	#c = sys.stdin.read(1);
	c= reader.read()
	while c != '<': #{
		if c == '*': #{
			unknown = True;
			lemma = superficial;
			break;
		#}
		lemma = lemma + c;
		#c = sys.stdin.read(1);
		c= reader.read()
	#}

	lemma = lemma.replace(' ', '~');

	if unknown == True: #{
		if _tags == 0: #{
			sys.stdout.write(superficial + '|' + lemma + ' ' );
		elif _tags == 1: #{
			sys.stdout.write(superficial + '|' + lemma + '|? ' );
		else: #{
			sys.stdout.write(superficial + '|' + lemma + '|?|? ' );
		#}
	#}

	while c != '$': #{
		analysis = analysis + c;
		#c = sys.stdin.read(1);
		c= reader.read()
	#}

	if unknown == True: #{
		#c = sys.stdin.read(1);
		c= reader.read()
		if c == "\n":
			sys.stdout.write(c)
		else:
			reader.unread(c)
		return;
	#}

	if '+' in analysis: #{
		gde = 0;
		for j in analysis: #{
			if j == '<' and gde == 0: #{
				gde = 1;
				tags = tags + '+<';
				continue;
			elif j == '+': #{
				gde = 0;
				lemma = lemma + '+';
				continue;
			#}

			if gde == 0: #{
				lemma = lemma + j;
			elif gde == 1: #{
				tags = tags + j;
			#}
		#}
		lemma = lemma.replace(' ', '~')
	else: #{
		tags = analysis;
	#}

	tags = tags.replace('>+<', '+');
	if tags.count('><') > 0: #{
		tag = tags.replace('><','.').strip('+><').split('.')[0];
	else: #{
		tag = tags.replace('><','.').strip('+><');
	#}

	#fix ^decided to go ahead/decide<vblex><pp># to go ahead$
	if "#" in tags:
		partstags=tags.split("#")
		if len(partstags) == 2:
			tags=partstags[0].rstrip(">")
			lemma=lemma+partstags[1].replace(' ', '~')

	
	if _tags == 0: #{
		sys.stdout.write(superficial + '|' + lemma + ' ');
	elif _tags == 1: #{
		sys.stdout.write(superficial + '|' + lemma + '|' + tag + ' ');
	elif _tags > 1: #{
		row_tags = tags.replace('><', '.').strip('+><').split('.');
		tags = '.'.join(row_tags[0:_tags]);
		sys.stdout.write(superficial + '|' + lemma + '|' + tag + '|' + tags + ' ' );
	else: #{
		sys.stdout.write(superficial + '|' + lemma + '|' + tag + '|' + tags.replace('><','.').strip('+><') + ' ' );
	#}
#}

while c: #{
	#print >>sys.stderr, c
	# Beginning of a lexical unit
	if c == '^': #{
		processWord(c, n_tags);
	#}

	# In some analysers, the comma is not analysed, it should be
	if c == ',': #{
		if n_tags == 0: #{
			sys.stdout.write(',|,');
		elif n_tags == 1: #{
			sys.stdout.write(',|,|cm');
		else: #{
			sys.stdout.write(',|,|cm|cm');
		#}
	#}

	# Newline is newline
	if c == '\n': #{
		sys.stdout.write(c);
	#}

	#c = sys.stdin.read(1);
	c= reader.read()
#}
