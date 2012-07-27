# -*- coding: utf-8 -*-
from instrumentation import instrument, use_state
from dotdict import dotdict


class Monitor(object):
	def __init__(self, name, function):
		self.name = name
		self.function = function
		self.oneshots = []

	def __repr__(self):
		return "Monitor('%s', %s)" % (self.name, self.function)


class Monitors(object):
	def __init__(self):
		self.monitors = {}
		self.oneshots = []

	def add_monitor(self, monitor):
		self.monitors[monitor.name] = monitor

	def __repr__(self):
		return "Monitors(%s)" % self.monitors


class EventMonitor(object):
	def __init__(self, state, monitor):
		self.state = state
		self.monitor = monitor
		self.name = monitor.name

		if hasattr(self.monitor.function, '__func__'):
			self.called = self.state.wrapper == self.monitor.function.__func__
		else:
			self.called = self.state.wrapper == self.monitor.function

	def inputs(self):
		# TODO: make it possible for this to work when not called. how?
		self._assert_called()
		return self.state.inargs

	def input_kwargs(self):
		self._assert_called()
		return self.state.inkwargs

	def outputs(self):
		self._assert_called()
		return self.state.outargs

	def output_kwargs(self):
		self._assert_called()
		return self.state.outkwargs

	def result(self):
		self._assert_called()
		return self.state.result

	def next(self, func, func_args=None, func_kwargs=None):
		func_args = func_args or tuple()
		func_kwargs = func_kwargs or dict()

		def on_next_call(monitors):
			func(monitors, *func_args, **func_kwargs)

		self.monitor.oneshots.append(on_next_call)

	def _assert_called(self):
		if not self.called:
			raise ValueError("Cannot get inputs for a function that isn't called")

	def __repr__(self):
		return "StatefulMonitor(%s, %s)" % (self.state, self.monitor)


class EventFunctions(object):
	def __init__(self, state, monitors):
		for name, monitor in monitors.monitors.items():
			sm = EventMonitor(state, monitor)
			self.__dict__[name] = sm
			if sm.called:
				self._active_monitor = sm

	def __getitem__(self, name):
		return self.__dict__[name]


class Event(object):
	def __init__(self, state, monitors):
		self.state = state
		self._monitors = monitors

		fn = EventFunctions(state, monitors)
		self.fn = fn
		self.active_function = fn._active_monitor

	def next(self, monitor, error_msg=None):
		name_to_check = monitor.name
		error_msg = error_msg or "Next function called should have been %s" % name_to_check
		def next_should_be_monitor(event):
			assert event.fn[name_to_check].called, error_msg
		self._monitors.oneshots.append(next_should_be_monitor)

	def __repr__(self):
		return "Event(%s, %s)" % (self.state, self.monitors)


def monitor(**kwargs):
	def decorator(spec):
		spec_rv = dotdict()
		spec_rv.monitors = Monitors()

		for name, func in kwargs.items():
			obj = None
			if not hasattr(func, '__call__'):
				# try to expand the func into both object and function
				try:
					obj, func = func
				except:
					raise ValueError("Function %s to monitor is not callable, or iterable of (obj, func)" % str(func))

			if not is_rv_instrumented(func):
				func = instrument(obj, func, pre=pre_func_call, post=post_func_call,
						extra={'use_rv': True, 'rv': dotdict(specs=[])})

			func_rv = func._prv.rv
			func_rv.specs.append(spec)

			spec_rv.monitors.add_monitor(Monitor(name, func))

		spec._prv = spec_rv
		return spec
	return decorator

def is_rv_instrumented(func):
	return hasattr(func, '_prv') and not func._prv.rv is None

def add_oneshot(target, func):
	pass

@use_state(rv=True)
def pre_func_call(state):
	pass

@use_state(rv=True, inargs=True)
def post_func_call(state):
	for spec in state.rv.specs:
		monitors = spec._prv.monitors
		event = Event(state, monitors)
		call_oneshots(event, spec)

		spec(event)
	pass

def call_oneshots(event, spec):
	monitors = event._monitors
	if monitors.oneshots:
		for oneshot in monitors.oneshots:
			oneshot(event)
		monitors.oneshots = []

	monitor = event.active_function.monitor
	if monitor.oneshots:
		for oneshot in monitor.oneshots:
			oneshot(event)
		monitor.oneshots = []
