# -*- coding: utf-8 -*-

from instrumentation import instrument

def before(obj, func=None):
	obj, func = _ba_swap(obj, func)
	def decorator(precondition, *args):
		instrument(obj, func, pre=(precondition, args))
		return precondition
	return decorator

def after(obj, func=None, *args):
	obj, func = _ba_swap(obj, func)
	def decorator(postcondition):
		instrument(obj, func, post=(postcondition, args))
		return postcondition
	return decorator

def _ba_swap(o, f):
	if not f:
		return f, o
	return o, f

def contract(pre=None, post=None, requires=None, ensures=None):
	def decorator(func):
		return instrument(None, func, pre=(pre, requires), post=(post, ensures), attach=False)
	return decorator
