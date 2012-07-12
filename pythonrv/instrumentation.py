# -*- coding: utf-8 -*-
import types
import inspect

_StaticMethodType = type(staticmethod(lambda: None))

def instrument(obj, func, pre=None, post=None, attach=True):
	"""
	Instruments func with a wrapper function that will call all functions in pre
	before and all functions in post after it calls func.
	"""

	# try to get the function from the container object
	if isinstance(func, basestring):
		if hasattr(obj, func):
			func = getattr(obj, func)
		else:
			raise ValueError("Cannot access function %s on container obj %s" % (func, obj))

	if not inspect.isroutine(func):
		raise ValueError("Function %s cannot be found or accessed, or is not a function" % func)

	if not obj:
		# we don't have an object; the function was given as a reference to it
		if hasattr(func, 'im_class'):
			# function is part of a class
			obj = func.im_class
		else:
			# function is globally accessible through its module
			obj = inspect.getmodule(func)

	wrapper, _dbc = setup_wrapper(obj, func, attach)

	# populate the wrapper with the given pre/post-functions
	def populate(key, value):
		if not value:
			return
		if hasattr(value, '__call__'):
			_dbc[key].append(value)
		else:
			try:
				# try to iterate through the value; works if it is an iterable
				for p in value:
					populate(key, p)
			except TypeError as e:
				raise TypeError("Contract condition %s is not callable" % p, e)

	populate('pre', pre)
	populate('post', post)

	return wrapper

def setup_wrapper(obj, func, attach=True):

	# classmethods and staticmethods are wrapped win an object
	# the "inner function" can be accessed through the __func__ attribute
	inner_func = func.__func__ if hasattr(func, '__func__') else func

	# bail early if we've already rewritten the target function
	if hasattr(inner_func, '_dbc'):
		return inner_func, inner_func._dbc

	wrapper = make_wrapper()

	copy_function_details(wrapper, inner_func)

	# the dict to store data for the wrapper
	_dbc = {
			'target': inner_func,
			'pre': [],
			'post': [],
	}
	wrapper._dbc = _dbc

	args, varargs, varkw, defaults = inspect.getargspec(inner_func)

	is_class = isinstance(obj, type) or isinstance(obj, types.ClassType)

	# FIXME: this is not a good way to check for static methods and functions
	if not args or args[0] not in ('self', 'cls', 'klass'):
		# static function or method
		if type(func) == _StaticMethodType or is_class:
			# static method
			wrapper = staticmethod(wrapper)
		else:
			# static function
			pass
	elif args[0] == 'self':
		# method
		if type(obj) == types.InstanceType:
			# method of an existing instance
			# FIXME: I don't know why this works
			_dbc['target'] = func
	else:
		# class method
		wrapper = classmethod(wrapper)

	if attach:
		# attach the wrapper to the target functions container object
		# use the "outer" function, which can be accessed through normal means
		if not hasattr(obj, inner_func.__name__):
			raise ValueError("Container object %s doesn't have an attribute %s" % (obj, func))

		setattr(obj, inner_func.__name__, wrapper)

	return wrapper, _dbc

def make_wrapper():
	def wrapper(*args, **kwargs):
		if hasattr(wrapper, '_dbc'):
			# this is usually the case
			_dbc = wrapper._dbc
		elif hasattr(wrapper, '__func__') and hasattr(wrapper.__func__, '_dbc'):
			# this happens if wrapper has been made into a classmethod or a
			# staticmethod. wrapper has been wrapped by descriptor objects; we can
			# access the real wrapper through the __func__ attribute
			_dbc = wrapper.__func__._dbc
		else:
			raise TypeError("wrapper is of a weird type...")

		def call_condition(p):
			if hasattr(_dbc['target'], '__self__'):
				# the target function was attached to an instance when we wrapped
				# it, so the pre/post-functions will expect a self argument first.
				# this is stored in the target's __self__ attribute
				p(_dbc['target'].__self__, *args, **kwargs)
			p(*args, **kwargs)

		# pre-functions
		for p in _dbc['pre']:
			call_condition(p)

		# target function
		result = _dbc['target'](*args, **kwargs)

		# post-functions
		for p in _dbc['post']:
			call_condition(p)

		return result
	return wrapper

def copy_function_details(dest, src):
	# copy some important attributes
	dest.__name__ = src.__name__
	dest.__module__ = src.__module__
	dest.__doc__ = src.__doc__
	dest.__dict__.update(src.__dict__)
	dest.__defaults__ = src.__defaults__
	#dest.__kwdefaults__ = src.__kwdefaults__
	assert not hasattr(src, '__kwdefaults__')

