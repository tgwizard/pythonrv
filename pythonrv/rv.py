# -*- coding: utf-8 -*-
from instrumentation import instrument, use_state
from dotdict import dotdict

##################################################################
### defaults and constants
##################################################################

DEFAULT_MAX_HISTORY_SIZE = 10

##################################################################
### decorators
##################################################################

def monitor(**kwargs):
	def decorator(spec):
		spec_rv = dotdict()
		spec_rv.spec_info = SpecInfo()

		for name, func in kwargs.items():
			obj = None
			if not hasattr(func, '__call__'):
				# try to expand the func into both object and function
				try:
					obj, func = func
				except:
					raise ValueError("Function %s to monitor is not callable, or iterable of (obj, func)" % str(func))

			if not _is_rv_instrumented(func):
				func = instrument(obj, func, pre=pre_func_call, post=post_func_call,
						extra={'use_rv': True, 'rv': dotdict(specs=[])})

			func_rv = func._prv.rv
			func_rv.specs.append(spec)

			spec_rv.spec_info.add_monitor(Monitor(name, func))

		spec._prv = spec_rv
		return spec
	return decorator

def _is_rv_instrumented(func):
	return hasattr(func, '_prv') and not func._prv.rv is None

##################################################################
### info and data about specifications and monitors
##################################################################

class SpecInfo(object):
	def __init__(self):
		self.monitors = {}
		self.oneshots = []
		self.history = []

	def add_monitor(self, monitor):
		self.monitors[monitor.name] = monitor

	def __repr__(self):
		return "SpecInfo(%s)" % self.monitors

class Monitor(object):
	def __init__(self, name, function):
		self.name = name
		self.function = function
		self.oneshots = []
		self.history = []

	def __repr__(self):
		return "Monitor('%s', %s)" % (self.name, self.function)

##################################################################
### pre and post functions
##################################################################

@use_state(rv=True)
def pre_func_call(state):
	pass

@use_state(rv=True, inargs=True)
def post_func_call(state):
	for spec in state.rv.specs:
		# 1. Create event data from state
		spec_info = spec._prv.spec_info
		event_data = EventData(spec_info, state)

		# 2. Make history
		_make_history(spec_info, event_data)

		# 3. Create a "monitored event" to pass to the spec
		event = Event(spec_info, event_data)

		# 5. Call any oneshots for this spec
		_call_oneshots(spec_info, event)

		# 6. Call spec
		spec(event)

def _call_oneshots(spec_info, event):
	if spec_info.oneshots:
		for oneshot in spec_info.oneshots:
			oneshot(event)
		spec_info.oneshots = []

	monitor = event.active_function.monitor
	if monitor.oneshots:
		for oneshot in monitor.oneshots:
			oneshot(event)
		monitor.oneshots = []

##################################################################
### history functions
##################################################################

def _make_history(spec_info, event_data):
	if len(spec_info.history) > 0:
		event_data.prev = spec_info.history[-1]
	else:
		event_data.prev = None
	spec_info.history.append(event_data)

	func_data = event_data.active_function
	monitor = spec_info.monitors[func_data.name]
	if len(monitor.history) > 0:
		func_data.prev = monitor.history[-1]
	else:
		func_data.prev = None
	monitor.history.append(func_data)

	# check sizes
	_truncate_history(spec_info)
	_truncate_history(monitor)

def _truncate_history(el, max_len=None):
	# FIXME: cannot reset the "outer" history, need to get inner reference
	if max_len is None:
		max_len = DEFAULT_MAX_HISTORY_SIZE
	if len(el.history) > max_len:
		el.history = el.history[-max_len:]
		if len(el.history) > 0:
			el.history[0].prev = None

##################################################################
### plain data objects
##################################################################

class EventData(object):
	def __init__(self, spec_info, state):
		self.fn = EventDataFunctions(spec_info, state)
		self.active_function = self.fn._active

	def __repr__(self):
		return "EventData(%s)" % (self.fn)

class EventDataFunctions(object):
	def __init__(self, spec_info, data):
		self._functions = []
		for name, monitor in spec_info.monitors.items():
			em = FunctionCallData(monitor, data)
			self._functions.append(em)
			self.__dict__[name] = em
			if em.called:
				self._active = em

	def __getitem__(self, name):
		return self.__dict__[name]

	def __repr__(self):
		return "EventDataFunctions(%s)" % self._functions

class FunctionCallData(object):
	def __init__(self, monitor, state):
		self.name = monitor.name
		if hasattr(monitor.function, '__func__'):
			self.called = state.wrapper == monitor.function.__func__
		else:
			self.called = state.wrapper == monitor.function

		# inputs/outputs
		if self.called:
			self.inputs = state.inargs
			self.input_kwargs = state.inkwargs
			self.outputs = state.outargs
			self.output_kwargs = state.outkwargs
			self.result = state.result

	def __repr__(self):
		return "FunctionCallData(%s, %s)" % (self.name, self.called)


##################################################################
### objects with logic
##################################################################

class Event(object):
	def __init__(self, spec_info, event_data):
		self._spec_info = spec_info

		self.history = spec_info.history
		self.prev = event_data.prev

		self.fn = EventFunctions(spec_info, event_data.fn)
		self.active_function = self.fn._active

	def next(self, monitor, error_msg=None):
		name_to_check = monitor.name
		error_msg = error_msg or "Next function called should have been %s" % name_to_check
		def next_should_be_monitor(event):
			assert event.fn[name_to_check].called, error_msg
		self._spec_info.oneshots.append(next_should_be_monitor)

	def success(self, msg=None):
		pass

	def failure(self, msg=None):
		pass

	def __repr__(self):
		return "Event(%s)" % (self.fn)

class EventFunctions(object):
	def __init__(self, spec_info, event_data_functions):
		for name, monitor in spec_info.monitors.items():
			function_call_data = event_data_functions[name]
			fe = FunctionCallEvent(monitor, function_call_data)
			self.__dict__[name] = fe
			if fe.called:
				self._active = fe

	def __getitem__(self, name):
		return self.__dict__[name]

	def __repr__(self):
		return "EventFunctions(%s)" % self._functions

class FunctionCallEvent(object):
	def __init__(self, monitor, function_call_data):
		self.monitor = monitor

		self.history = monitor.history
		if hasattr(function_call_data, 'prev'):
			self.prev = function_call_data.prev

		# copy data from function_call_data
		self.name = function_call_data.name
		self.called = function_call_data.called
		if function_call_data.called:
			# TODO: make it possible for this to work when not called. how?
			self.inputs = function_call_data.inputs
			self.input_kwargs = function_call_data.input_kwargs
			self.outputs = function_call_data.outputs
			self.output_kwargs = function_call_data.output_kwargs
			self.result = function_call_data.result

	def next(self, func, func_args=None, func_kwargs=None):
		func_args = func_args or tuple()
		func_kwargs = func_kwargs or dict()

		def on_next_call(monitors):
			func(monitors, *func_args, **func_kwargs)

		self.monitor.oneshots.append(on_next_call)

	def __repr__(self):
		return "FunctionCallEvent(%s, %s)" % (self.name, self.called)

