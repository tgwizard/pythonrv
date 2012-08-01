#!/usr/bin/env python

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
import fib_rvspecs

import logging
from pythonrv import rv
rv.configure(error_handler=rv.LoggingErrorHandler())
logging.basicConfig(filename="log", level=logging.WARNING, filemode="w", format="%(asctime)s - %(levelname)s - %(message)s")

from fib import fib

def main():
	print "Fibonacci numbers:"
	for i in range(1, 20):
		print "%d -> %d" %(i, fib(i))

if __name__ == '__main__':
	main()
