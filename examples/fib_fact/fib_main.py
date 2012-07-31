#!/usr/bin/env python

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
import fib_rvspecs

from fib import fib

def main():
	print "Fibonacci numbers:"
	for i in range(1, 20):
		print "%d -> %d" %(i, fib(i))

if __name__ == '__main__':
	main()
