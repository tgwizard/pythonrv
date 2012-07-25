# -*- coding: utf-8 -*-
from instrumentation import instrument, use_state
from dotdict import dotdict

class Monitor(object):
	def __init__(self, name, function):
		self.name = name
		self.function = function
		print "creating monitor: ", self
		super(Monitor, self).__init__()

	def with_state(self, state):
		return StatefulMonitor(state, self)

	def __repr__(self):
		return "Monitor('%s', %s)" % (self.name, self.function)

class StatefulMonitor(object):
	def __init__(self, state, monitor):
		self.state = state
		self.monitor = monitor
		self.name = monitor.name

		if hasattr(self.monitor.function, '__func__'):
			self.called = self.state.wrapper == self.monitor.function.__func__
		else:
			self.called = self.state.wrapper == self.monitor.function

	def next(self, *args):
		pass

	def __repr__(self):
		return "StatefulMonitor(%s, %s)" % (self.state, self.monitor)

class Monitors(object):
	def __init__(self):
		self.monitors = {}
		self.oneshots = []

	def with_state(self, state):
		return StatefulMonitors(state, self)

	def add_monitor(self, monitor):
		self.monitors[monitor.name] = monitor

	def __repr__(self):
		return "Monitors(%s)" % self.monitors

class StatefulMonitors(object):
	def __init__(self, state, monitors):
		self.state = state
		self.monitors = monitors

	def __getattr__(self, name):
		return self[name]

	def __getitem__(self, name):
		monitor = self.monitors.monitors[name]
		monitor = StatefulMonitor(self.state, monitor)
		self.__dict__[name] = monitor
		return monitor

	def next(self, monitor, error_msg=None):
		error_msg = error_msg or "Next function called should have been %s" % monitor.name
		def next_should_be_monitor(monitors):
			assert monitors[monitor.name].called, error_msg
		self.monitors.oneshots.append(next_should_be_monitor)

	def __repr__(self):
		return "StatefulMonitors(%s, %s)" % (self.state, self.monitors)


def monitors(**kwargs):
	def decorator(spec):
		spec_rv = dotdict()
		spec_rv.monitors = Monitors()

		for name, func in kwargs.items():
			print "monitor %s" % name
			print func
			if is_rv_instrumented(func):
				print "func is already instrumented for rv"
			else:
				print "will instrument func for rv"
				func = instrument(None, func, pre=pre_func_call, post=post_func_call,
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

@use_state(rv=True)
def post_func_call(state):
	for spec in state.rv.specs:
		m = spec._prv.monitors
		sm = m.with_state(state)
		call_oneshots(sm, spec)

		spec(sm)
	pass

def call_oneshots(stateful_monitors, spec):
	if not stateful_monitors.monitors.oneshots:
		return
	for oneshot in stateful_monitors.monitors.oneshots:
		oneshot(stateful_monitors)
	stateful_monitors.monitors.oneshots = []
