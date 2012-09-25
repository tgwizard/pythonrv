# -*- coding: utf-8 -*-
import types
import inspect
import copy

from dotdict import dotdict

DEEP_COPY_FUNC = copy.deepcopy
NO_COPY_FUNC = lambda x: x
copy_func = DEEP_COPY_FUNC

def instrument(obj, func, pre=None, post=None, attach=True, extra=None):
	"""
	Instruments func with a wrapper function that will call all functions in pre
	before and all functions in post after it calls func.
	"""
	extra = extra or {}

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
			if func.__self__:
				# it is bound to an instance
				obj = func.__self__
			else:
				obj = func.im_class
		else:
			# function is globally accessible through its module
			obj = inspect.getmodule(func)

	wrapper, _prv = setup_wrapper(obj, func, attach)

	# update _prv with extra data
	for key, item in extra.items():
		if key in _prv:
			raise ValueError("extra data cannot overide existing attribute (%s) in _prv" % key)
		_prv[key] = item

	# populate the wrapper with the given pre/post-functions
	def populate(container, value):
		if not value:
			return
		if hasattr(value, '__call__'):
			container.append(value)
			if hasattr(value, '_prv_use_state'):
				use_state = value._prv_use_state
				for k, v in use_state.items():
					if v:
						_prv.use_state[k] = True
				_prv.use_state['use'] = True
		else:
			try:
				# try to iterate through the value; works if it is an iterable
				for p in value:
					populate(container, p)
			except TypeError as e:
				raise TypeError("Contract condition %s is not callable" % p, e)

	populate(_prv.pre, pre)
	populate(_prv.post, post)

	return wrapper

def setup_wrapper(obj, func, attach=True):

	# classmethods and staticmethods are wrapped win an object
	# the "inner function" can be accessed through the __func__ attribute
	inner_func = func.__func__ if hasattr(func, '__func__') else func

	# bail early if we've already rewritten the target function
	if hasattr(inner_func, '_prv'):
		return inner_func, inner_func._prv

	wrapper = make_wrapper()

	copy_function_details(wrapper, inner_func)

	# the dict to store data for the wrapper
	_prv = dotdict()
	_prv.target = inner_func
	_prv.pre = []
	_prv.post = []
	_prv.use_state = dotdict()
	_prv.use_state.use = False
	_prv.use_state.inargs = False
	_prv.use_state.global_store = False
	_prv.state = dotdict()

	wrapper._prv = _prv

	args, varargs, varkw, defaults = inspect.getargspec(inner_func)

	# FIXME: this is not a good way to check for static methods and functions
	if type(obj) == types.ModuleType:
		# static global function
		pass
	elif not args or args[0] not in ('self', 'cls', 'klass'):
		# static method
		wrapper = staticmethod(wrapper)
	elif args[0] == 'self':
		# method
		if func.im_self:
			# method of an existing instance
			# func is a bound user-defined method object
			# we need func, and not inner_func, since it will provide the self
			# argument when we call it
			_prv.target = func
	else:
		# class method
		wrapper = classmethod(wrapper)

	if attach:
		# attach the wrapper to the target functions container object
		# use the "outer" function, which can be accessed through normal means
		if not hasattr(obj, inner_func.__name__):
			raise ValueError("Container object %s doesn't have an attribute %s" % (obj, func))

		setattr(obj, inner_func.__name__, wrapper)
		wrapper = getattr(obj, inner_func.__name__)

	return wrapper, _prv

def make_wrapper():
	def wrapper(*args, **kwargs):
		if hasattr(wrapper, '_prv'):
			# this is usually the case
			_prv = wrapper._prv
		elif hasattr(wrapper, '__func__') and hasattr(wrapper.__func__, '_prv'):
			# this happens if wrapper has been made into a classmethod or a
			# staticmethod. wrapper has been wrapped by descriptor objects; we can
			# access the real wrapper through the __func__ attribute
			_prv = wrapper.__func__._prv
		else:
			raise TypeError("wrapper is of a weird type...")

		# setup possible use of state
		use_state = _prv.use_state
		state = _prv.state

		# commence ugly hack:
		# FIXME: this sets the copy_func for all specs for this wrapper. It should
		# only be for the one needing a special copy_func.
		local_copy_func = None
		if hasattr(_prv, 'rv'):
			if hasattr(_prv.rv, 'spec'):
				for spec in _prv.rv.specs:
					local_copy_func = local_copy_func or spec._prv.spec_info.copy_func
		local_copy_func = local_copy_func or copy_func

		if use_state.use:
			state.function_name = _prv.target.__name__
			state.args = args
			state.kwargs = kwargs

			# setup store in state
			if use_state.global_store:
				state.global_store = state.global_store or {}

			# setup input args in state as copies of args
			if use_state.inargs:
				state.inargs = local_copy_func(args)
				state.inkwargs = {}
				state.inkwargs.update(local_copy_func(kwargs))

			if use_state.rv:
				state.rv = _prv.rv
				state.wrapper = wrapper

		def call_condition_with_self(p):
			if hasattr(_prv.target, '__self__'):
				# the target function was attached to an instance when we wrapped
				# it, so the pre/post-functions will expect a self argument first.
				# this is stored in the target's __self__ attribute
				p(_prv.target.__self__, *args, **kwargs)
			else:
				p(*args, **kwargs)

		def call_condition_with_state(p):
			if hasattr(p, '_prv_use_state'):
				# the condition has been marked that it wants to use "dbc state". send
				# state as the only argument

				# setup the conditions local store, if required
				p_use_state = p._prv_use_state
				if 'local_store' in p_use_state and p_use_state['local_store']:
					if not hasattr(p, '_prv_local_store'):
						p._prv_local_store = {}
					state.local_store = p._prv_local_store

				p(state)

				# cleanup
				# TODO: fix
				if 'local_store' in p_use_state and p_use_state['local_store']:
					del state.local_store
			else:
				call_condition_with_self(p)

		# pre-functions
		for p in _prv.pre:
			call_condition_with_state(p)

		# target function
		result = _prv.target(*args, **kwargs)

		# copy result into state
		if use_state.use:
			state.result = result

			if use_state.outargs:
				state.outargs = local_copy_func(args)
				state.outkwargs = {}
				state.outkwargs.update(local_copy_func(kwargs))


		# post-functions
		for p in _prv.post:
			call_condition_with_state(p)

		# cleanup state
		if use_state.use:
			if 'inargs' in state:
				del state.inargs
				del state.inkwargs
			if 'outargs' in state:
				del state.outargs
				del state.outkwargs
			state.args = None
			state.kwargs = None
			del state.result

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

def use_state(**state_options):
	state_options = state_options or {}
	def decorator(func):
		setattr(func, '_prv_use_state', state_options)
		return func
	return decorator
