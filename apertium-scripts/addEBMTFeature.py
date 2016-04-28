#!/usr/bin/python

#-------------------------------------------------------------------------------
# This file is part of OpenMaTrEx: a marker-driven corpus-based machine
# translation system.
# 
# Copyright (c) 2010 Dublin City University
# (c) 2010 Sergio Penkale
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#-------------------------------------------------------------------------------

import sys,gzip;

if (len(sys.argv) != 3):
    print "Usage: addEBMTFeature.py ebmt-phrases.gz phrase-table.gz";
    print "Assumes BOTH files are sorted, and that every ebmt-phrase appears in the phrase table";
    print "ebmt-phrases is a list of phrases of the form: 's ||| t |||' with no word alignment, and with no duplicates"
    sys.exit(1);

ebmt = gzip.open(sys.argv[1]);
pt = gzip.open(sys.argv[2]);

#I don't know if it's possible, but just in case I consider the case where 2 entries in the phrase table have the same phrase but different features/word-alignment
last = "";

current = ebmt.readline().rstrip();
for entry in pt:
    entry = entry.rstrip();
    spl = entry.split(" ||| ");
    phrase = " ||| ".join(spl[0:2]) + " |||";

    if (last and last != phrase):
    	current = ebmt.readline().rstrip();
    	last = "";

    if (phrase == current):
	print " ||| ".join(spl[:3]) + " 1 ||| " + " ||| ".join(spl[3:]);
	#print entry + " 1";
	#print " ||| ".join(spl[:-1]) + " ||| 1 " + spl[-1];
	last = phrase;

    else:
	print " ||| ".join(spl[:3]) + " 0 ||| " + " ||| ".join(spl[3:]);
	#print entry + " 0";
	#print " ||| ".join(spl[:-1]) + " ||| 0 " + spl[-1];

if (ebmt.readline()):
    sys.stderr.write("\nWARNING: there are ebmt phrases missing in the phrase table!!\n");

ebmt.close();
pt.close();
