# -*- coding: utf-8 -*-
import types
import inspect

_StaticMethodType = type(staticmethod(lambda: None))

def instrument(obj, func, pre=None, post=None, attach=True):
	"""
	Instruments func with a wrapper function that will call all functions in pre
	before and all functions in post after it calls func.
	"""
	# swap places
	if not func:
		func, obj = obj, func

	# try to get the function from the container object
	if isinstance(func, basestring):
		if hasattr(obj, func):
			func = getattr(obj, func)
		else:
			raise ValueError("Cannot access function %s on container obj %s" % (func, obj))

	if not inspect.isroutine(func):
		raise ValueError("Function cannot be found or accessed %s" % func)

	# classmethods and staticmethods are wrapped win an object
	# the "inner function" can be accessed through the __func__ attribute
	inner_func = func.__func__ if hasattr(func, '__func__') else func

	if not obj:
		if hasattr(func, 'im_class'):
			pass
			obj = func.im_class
		else:
			obj = inspect.getmodule(func)

	if attach and not hasattr(obj, func.__name__):
		raise ValueError("Container object %s doesn't have an attribute %s" % (obj, func))

	wrapper, _dbc = setup_wrapper(obj, func, inner_func, attach)

	# populate the wrapper with the given condiitions
	def validate_callable(p):
		if hasattr(p, '__call__'):
			return p
		raise TypeError("Contract condition %s is not callable" % p)
	def populate(key, value):
		if not value:
			return
		try:
			for p in value:
				_dbc[key].append(validate_callable(p))
		except TypeError:
			_dbc[key].append(validate_callable(value))

	populate('pre', pre)
	populate('post', post)

	return wrapper

def setup_wrapper(obj, func, inner_func, attach=True):

	# bail early if we've already rewritten the target function
	if hasattr(inner_func, '_dbc'):
		return inner_func, inner_func._dbc

	wrapper = make_wrapper()
	wrapper.func_name = inner_func.func_name
	wrapper.__module__ = inner_func.__module__

	# copy function attributes from target to wrapper
	for key, value in inner_func.func_dict.items():
		wrapper.func_dict[key] = value

	# the dict to store wrapper data
	_dbc = {
			'target': inner_func,
			'pre': [],
			'post': [],
	}
	wrapper._dbc = _dbc

	is_class = isinstance(obj, type) or isinstance(obj, types.ClassType)
	args, varargs, varkw, defaults = inspect.getargspec(inner_func)

	if not args or args[0] not in ('self', 'cls', 'klass'):
		# static function or method
		if func.__class__ == _StaticMethodType or is_class:
			# static method
			wrapper = staticmethod(wrapper)
		else:
			# static function
			pass
	elif args[0] == 'self':
		# method
		if type(obj) == types.InstanceType:
			# method of an existing instance
			# why this works, I don't know
			_dbc['target'] = func
	else:
		# class method
		wrapper = classmethod(wrapper)

	if attach:
		# attach the wrapper to the target functions container object
		# use the "outer" function, which can be accessed through normal means
		setattr(obj, inner_func.__name__, wrapper)

	return wrapper, _dbc

def make_wrapper():
	def wrapper(*args, **kwargs):
		if hasattr(wrapper, '_dbc'):
			_dbc = wrapper._dbc
		elif hasattr(wrapper, '__func__') and hasattr(wrapper.__func__, '_dbc'):
			_dbc = wrapper.__func__._dbc
		else:
			raise TypeError("wrapper is of a weird type...")

		def call_condition(p):
			if hasattr(_dbc['target'], '__self__'):
				p(_dbc['target'].__self__, *args, **kwargs)
			p(*args, **kwargs)


		for p in _dbc['pre']:
			call_condition(p)

		result = _dbc['target'](*args, **kwargs)

		for p in _dbc['post']:
			call_condition(p)

		return result
	return wrapper
