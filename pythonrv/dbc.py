# -*- coding: utf-8 -*-
import inspect

from instrumentation import instrument, use_state

def before(obj=None, func=None):
	"""
	Before decorates a function to be a precondition to another function `func`.
	It will instrument `func` with a wrapper function that will call all
	preconditions, then the function, and then any postconditions (see
	dbc.after). It is possible to use before (and after) more than once on the
	same function, new preconditions (postconditions) are appended to the
	existing ones.

	Use before when you want to add pre/post-conditions to a function but don't
	want to, or can't, modify the target function. Use dbc.contract if you can.

	Usage:

		def f(x):
			return x

		@dbc.before(f)
		def p(x):
			# do what you want here
			assert x

	Works on module-level functions, methods, class methods and static methods.
	It does not work on local functions.
	"""
	obj, func = _swap_if_not_func(obj, func)
	def decorator(precondition, *other_preconditions):
		instrument(obj, func, pre=(precondition, other_preconditions))
		return precondition
	return decorator

def after(obj, func=None):
	"""
	See before decorator above.
	"""
	obj, func = _swap_if_not_func(obj, func)
	def decorator(postcondition, *other_postconditions):
		instrument(obj, func, post=(postcondition, other_postconditions))
		return postcondition
	return decorator

def _swap_if_not_func(o, f):
	return (o, f) if f else (f, o)

def contract(pre=None, post=None, requires=None, ensures=None):
	"""
	Wraps the target function `func` with pre- and post-conditions that gets
	executed before and after the function.

	Usage:

		def pre(x):
			assert x

		def post(x):
			assert 17

		@dbc.contract(pre=pre, post=post)
		def f(x):
			return x

	Works on "all" functions.
	"""
	def decorator(func):
		return instrument(None, func, pre=(pre, requires), post=(post, ensures), attach=False)
	return decorator

