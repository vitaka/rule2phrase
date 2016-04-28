#!/usr/bin/python
# coding=utf-8
# -*- encoding: utf-8 -*-

import sys,re,codecs;

for lex in sys.stdin:
	lex=lex.decode('utf-8').strip()
	if lex.find(u"__REGEXP__") == -1:
		forms=lex.split(u":")
		supform=None
		lexform=None
		
		if len(forms) == 2:
			supform=forms[0]
			lexform=forms[1]
		elif len(forms) ==3:
			if forms[1]==u">":
				supform=forms[0]
				lexform=forms[2]
		
		if supform and lexform:
			print lexform.encode('utf-8')
