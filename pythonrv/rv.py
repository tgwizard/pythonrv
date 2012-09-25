# -*- coding: utf-8 -*-

import logging

import instrumentation
from dotdict import dotdict

##################################################################
### defaults and constants
##################################################################

DEFAULT_MAX_HISTORY_SIZE = 2
INFINITE_HISTORY_SIZE = -1

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

DEFAULT_ERROR_LEVEL = ERROR

##################################################################
### decorators
##################################################################

def monitor(**monitorees):
	def decorator(spec):
		spec_info = _spec_info_for_spec(spec)

		for name, func in monitorees.items():
			obj = None
			if not hasattr(func, '__call__'):
				# try to expand the func into both object and function
				try:
					obj, func = func
				except:
					raise ValueError("Function %s to monitor is not callable, or iterable of (obj, func)" % str(func))

			if not _is_rv_instrumented(func):
				func = instrumentation.instrument(obj, func, pre=pre_func_call, post=post_func_call,
						extra={'use_rv': True, 'rv': dotdict(specs=[])})

			func_rv = func._prv.rv
			func_rv.specs.append(spec)

			spec_info.add_monitor(Monitor(name, func))

		return spec
	return decorator

def spec(**options):
	def decorator(spec_func):
		spec_info = _spec_info_for_spec(spec_func)
		spec_info.error_level = options.get('level', DEFAULT_ERROR_LEVEL)
		history_size = options.get('history_size', DEFAULT_MAX_HISTORY_SIZE)
		if history_size < -1:
			raise ValueError("Negative max history sizes (%d) are not allowed" % history_size)
		spec_info.max_history_size = history_size

		enable_copy_args = options.get('enable_copy_args', True)
		spec_info.copy_func = None if enable_copy_args else instrumentation.NO_COPY_FUNC
		return spec_func
	return decorator

def _is_rv_instrumented(func):
	return hasattr(func, '_prv') and not func._prv.rv is None

def _spec_info_for_spec(spec):
	if '_prv' not in spec.__dict__:
		spec._prv = dotdict()
	if 'spec_info' not in spec._prv:
		spec._prv.spec_info = SpecInfo()
	return spec._prv.spec_info

##################################################################
### info and data about specifications and monitors
##################################################################

class SpecInfo(object):
	def __init__(self):
		self.monitors = {}
		self.oneshots = []
		self.history = []
		self.active = True
		self.error_level = DEFAULT_ERROR_LEVEL
		self.max_history_size = DEFAULT_MAX_HISTORY_SIZE
		self.copy_func = None

	def add_monitor(self, monitor):
		self.monitors[monitor.name] = monitor

	def __repr__(self):
		return "SpecInfo(%s, active=%s, error_level=%s, max_history_size=%s, copy_func=%s)" % \
			(self.monitors, self.active, self.error_level, self.max_history_size, self.copy_func)

class Monitor(object):
	def __init__(self, name, function):
		self.name = name
		self.function = function
		self.oneshots = []
		self.history = []

	def _remove_spec_from_function(self, spec):
		self.function._prv.rv.specs.remove(spec)

	def __repr__(self):
		return "Monitor('%s', %s)" % (self.name, self.function)

##################################################################
### pre and post functions
##################################################################

@instrumentation.use_state(rv=True)
def pre_func_call(state):
	pass

@instrumentation.use_state(rv=True, inargs=True, outargs=True)
def post_func_call(state):
	# create a copy of this list so that we can modify it while we iterate...
	for spec in list(state.rv.specs):
		# 1. Create event data from state
		spec_info = spec._prv.spec_info
		event_data = EventData(spec_info, state)

		# 2. Make history
		_make_history(spec_info, event_data)

		# 3. Create a "monitored event" to pass to the spec
		event = Event(spec, spec_info, event_data)

		# 4. Call any oneshots for this spec
		one_shot_errors = _call_oneshots(spec_info, event)

		# 5. Call spec
		spec_errors = _call_spec(spec, event)

		_cleanup_spec(spec, spec_info)

		_handle_errors(spec_info, one_shot_errors + spec_errors)

def _call_oneshots(spec_info, event):
	errors = []
	monitor = event.called_function.monitor

	def all_oneshots():
		for oneshot in spec_info.oneshots:
			yield oneshot
		for oneshot in monitor.oneshots:
			yield oneshot

	for oneshot in all_oneshots():
		try:
			oneshot(event)
		except AssertionError as e:
			errors.append(e)

	spec_info.oneshots = []
	monitor.oneshots = []

	return errors

def _call_spec(spec, event):
	if not _should_call_spec(spec, event):
		return []

	try:
		spec(event)
	except AssertionError as e:
		return [e]
	return []

def _should_call_spec(spec, event):
	if event._should_call_spec:
		return True
	return False

def _handle_errors(spec_info, errors):
	if len(errors) > 0:
		_error_handler.handle(spec_info.error_level, errors)

def _cleanup_spec(spec, spec_info):
	if spec_info.active:
		return
	if len(spec_info.oneshots) > 0:
		# the spec itself has remaining oneshots
		return
	if len([oneshot for monitor in spec_info.monitors.values() for oneshot in monitor.oneshots]) > 0:
		# some monitor has remaining oneshots
		return

	for monitor in spec_info.monitors.values():
		monitor._remove_spec_from_function(spec)


##################################################################
### history functions
##################################################################

def _make_history(spec_info, event_data):
	if len(spec_info.history) > 0:
		event_data.prev = spec_info.history[-1]
	else:
		event_data.prev = None
	spec_info.history.append(event_data)

	func_data = event_data.called_function
	monitor = spec_info.monitors[func_data.name]
	if len(monitor.history) > 0:
		func_data.prev = monitor.history[-1]
	else:
		func_data.prev = None
	monitor.history.append(func_data)

	# check sizes
	_truncate_history(spec_info, spec_info.max_history_size)
	_truncate_history(monitor, spec_info.max_history_size)

def _truncate_history(el, max_len=None):
	if max_len == INFINITE_HISTORY_SIZE:
		return
	if max_len is None:
		max_len = DEFAULT_MAX_HISTORY_SIZE

	if len(el.history) > max_len:
		# we always have at least 1 in the history
		el.history = el.history[-max_len:(max_len+1)]
		if len(el.history) > 0:
			el.history[0].prev = None

##################################################################
### plain data objects
##################################################################

class EventData(object):
	def __init__(self, spec_info, state):
		self.fn = EventDataFunctions(spec_info, state)
		self.called_function = self.fn._called

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
				self._called = em

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
			self.outputs = state.args
			self.output_kwargs = state.kwargs
			self.result = state.result

	def __repr__(self):
		return "FunctionCallData(%s, %s)" % (self.name, self.called)


##################################################################
### objects with logic
##################################################################

class Event(object):
	def __init__(self, spec_function, spec_info, event_data):
		self._spec_function = spec_function
		self._spec_info = spec_info
		self._should_call_spec = spec_info.active

		self.history = spec_info.history
		self.prev = event_data.prev

		self.fn = EventFunctions(spec_info, event_data.fn)
		self.called_function = self.fn._called

	def next(self, next_function):
		self._spec_info.oneshots.append(next_function)

	def next_called_should_be(self, monitor, error_msg=None):
		name_to_check = monitor.name
		error_msg = error_msg or "Next function called should have been %s" % name_to_check
		def next_should_be_monitor(event):
			assert event.fn[name_to_check].called, error_msg
		self.next(next_should_be_monitor)

	def finish(self, success=True, msg=None):
		self._should_call_spec = self._spec_info.active = False
		if not success:
			raise AssertionError(msg)

	def success(self, msg=None):
		self.finish(success=True, msg=msg)

	def failure(self, msg=None):
		self.finish(success=False, msg=msg)

	def __repr__(self):
		return "Event(%s)" % (self.fn)

class EventFunctions(object):
	def __init__(self, spec_info, event_data_functions):
		self._functions = []
		for name, monitor in spec_info.monitors.items():
			function_call_data = event_data_functions[name]
			fe = FunctionCallEvent(monitor, function_call_data)
			self._functions.append(fe)
			self.__dict__[name] = fe
			if fe.called:
				self._called = fe

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

##################################################################
### configuration
##################################################################

class RaiseExceptionErrorHandler(object):
	def __init__(self, level=ERROR):
		self.level = level

	def handle(self, level, errors):
		if level >= self.level:
			# TODO: somehow raise all errors, not just the first one
			for e in errors:
				raise e

	def __repr__(self):
		return "RaiseExceptionErrorHandler(%d)" % self.level

class LoggingErrorHandler(object):
	def __init__(self):
		self.logger = logging.getLogger('pythonrv')

	def handle(self, level, errors):
		for e in errors:
			self.logger.log(level, e)

	def __repr__(self):
		return "LoggingErrorHandler()"

DEFAULT_ERROR_HANDLER = RaiseExceptionErrorHandler()
_error_handler = DEFAULT_ERROR_HANDLER
_enable_copy_args = True

def configure(**options):
	global _error_handler, _enable_copy_args
	_error_handler = options.get('error_handler', DEFAULT_ERROR_HANDLER)
	_enable_copy_args = options.get('enable_copy_args', True)
	instrumentation.copy_func = instrumentation.DEEP_COPY_FUNC if _enable_copy_args else instrumentation.NO_COPY_FUNC

def get_configuration():
	global _error_handler, _enable_copy_args
	return {
			'error_handler': _error_handler,
			'enable_copy_args': _enable_copy_args
		}
