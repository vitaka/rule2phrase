#!/usr/bin/python
# coding=utf-8
# -*- encoding: utf-8 -*-

import re, sys, string;

endingsToReplace=dict()
endingsToReplace[r"{transfer-rule sent --\^.<sent>\$ -- {start-chunk \^0-.<sent>\$ end-chunk} transfer-rule}"]=u""
endingsToReplace[r"{transfer-rule porello sent --\^por ello<cnjadv>\$ \^.<sent>\$ -- {start-chunk \^for<pr>\$ end-chunk}{start-chunk \^that<prn><tn><3><4>\$ end-chunk}{start-chunk \^1-.<sent>\$ end-chunk} transfer-rule}"]=r"{transfer-rule porello --\^por ello<cnjadv>\$  -- {start-chunk \^for<pr>\$ end-chunk}{start-chunk \^that<prn><tn><3><4>\$ end-chunk} transfer-rule}"

for line in sys.stdin:
	line=line.decode('utf8').strip()
	for ending in endingsToReplace:
		if line.endswith(ending):
			line=line[:-len(ending)]+endingsToReplace[ending]
			break
	print line.encode('utf-8')

