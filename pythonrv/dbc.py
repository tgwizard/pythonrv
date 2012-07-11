# -*- coding: utf-8 -*-

from instrumentation import instrument

def before(obj, func=None):
	def decorator(precondition):
		instrument(obj, func, pre=precondition)
		return precondition
	return decorator

def after(obj, func=None):
	def decorator(postcondition):
		instrument(obj, func, post=postcondition)
		return postcondition
	return decorator

def contract(pre=None, post=None):
	def decorator(func):
		return instrument(None, func, pre=pre, post=post, attach=False)
	return decorator
