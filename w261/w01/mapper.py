#!/usr/bin/python
import sys
import re
count = 0
WORD_RE = re.compile(r"[\w']+")
filename = sys.argv[2]
findword = sys.argv[1]
wc = 0
with open (filename, "r") as myfile:
    #Please insert your code
    for line in myfile:
        if re.search(findword, line, re.I) != None:
            wc += 1
print wc        
        