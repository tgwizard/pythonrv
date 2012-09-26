#!/usr/bin/env python

def fib(n):
    a = 1
    b = 1
    for i in range(1,n):
        c = a + b
        a = b
        b = c
    return a
