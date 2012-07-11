# -*- coding: utf-8 -*-
import types
import inspect

def dbc_condition_placeholder(*args, **kwargs):
	print "in dbc_condition_placeholder"

def before(obj, func=None):
	def decorator(precondition):
		instrument(obj, func, pre=precondition)
		return dbc_condition_placeholder
	return decorator

def after(obj, func=None):
	def decorator(postcondition):
		instrument(obj, func, post=postcondition)
		return dbc_condition_placeholder
	return decorator

def contract(pre=None, post=None):
	def decorator(func):
		pass
	return decorator

def instrument(obj, func, pre=None, post=None):
	"""
	Instruments func with a wrapper function that will call all functions in pre
	before and all functions in post after it calls func.
	"""
	# swap places
	if not func:
		func, obj = obj, func

	if isinstance(func, basestring):
		if hasattr(obj, func):
			func = getattr(obj, func)
		else:
			raise ValueError("Cannot access function %s on container obj %s" % (func, obj))
	if not obj:
		if inspect.isroutine(func):
			obj = inspect.getmodule(func)
		else:
			raise ValueError("Cannot access container obj for function %s" % func)

	if not hasattr(obj, func.__name__):
		print dir(func)
		raise ValueError("Container object %s doesn't have an attribute %s" % (obj, func))

	_dbc = attach_wrapper(obj, func)

	if pre:
		_dbc['pre'].append(pre)
	if post:
		_dbc['post'].append(post)

def attach_wrapper(obj, func):
	# bail early if we've already rewritten the target function
	if hasattr(func, '_dbc'):
		return func._dbc
	if hasattr(func, '__func__') and hasattr(func.__func__, '_dbc'):
		return func.__func__._dbc

	wrapper = make_wrapper()
	wrapper.func_name = func.func_name
	wrapper.__module__ = func.__module__

	# copy function attributes from target to wrapper
	for key, value in func.func_dict.items():
		wrapper.func_dict[key] = value

	# the dict to store wrapper data
	_dbc = {
			'target': func,
			'pre': [],
			'post': [],
			'is_classmethod': False,
	}
	wrapper._dbc = _dbc

	is_class = isinstance(obj, type) or isinstance(obj, types.ClassType)
	args, varargs, varkw, defaults = inspect.getargspec(func)

	if not args or args[0] not in ('self', 'cls', 'klass'):
		# static function or method
		if is_class:
			# static method
			wrapper = staticmethod(wrapper)
		else:
			# static function
			pass
	elif args[0] == 'self':
		# method
		pass
	else:
		# class method
		_dbc['is_classmethod'] = True
		wrapper = classmethod(wrapper)

	# attach the wrapper to the target functions container object
	setattr(obj, func.__name__, wrapper)

	return _dbc

def make_wrapper():
	def wrapper(*args, **kwargs):
		if hasattr(wrapper, '_dbc'):
			_dbc = wrapper._dbc
		elif hasattr(wrapper, '__func__') and hasattr(wrapper.__func__, '_dbc'):
			_dbc = wrapper.__func__._dbc
		else:
			raise TypeError("wrapper is of a weird type...")

		for p in _dbc['pre']:
			p(*args, **kwargs)
		if _dbc['is_classmethod']:
			result = _dbc['target'](*args[1:], **kwargs)
		else:
			result = _dbc['target'](*args, **kwargs)
		for p in _dbc['post']:
			p(*args, **kwargs)
		return result
	return wrapper
