#!/usr/bin/python
''' map function copies stdin to stdout '''
from __future__ import print_function
import sys
for line in sys.stdin:
    print(line.strip(), '')