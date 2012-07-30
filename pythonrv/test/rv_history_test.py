# -*- coding: utf-8 -*-
import unittest

from pythonrv import rv

class TestHistory(unittest.TestCase):
	# test history for event
	def test_event_simple(self):
		class M(object):
			def m(self):
				pass

		@rv.monitor(m=M.m)
		def spec(event):
			assert event.history[-1] == event
			raise ValueError("call %d" % len(event.history))

		a = M()
		for i in range(1,10):
			with self.assertRaises(ValueError) as e:
				a.m()
			self.assertEquals(e.exception.message, "call %d" % i)

	def test_event_prev(self):
		class M(object):
			def m(self):
				pass

		@rv.monitor(m=M.m)
		def spec(event):
			if len(event.history) > 1:
				assert event.history[-1] == event
				assert event.history[-2] == event.prev

		a = M()
		for i in range(1,10):
			a.m()

	def test_event_inputs_and_outputs(self):
		class M(object):
			def m(self, foo):
				ret = foo['x']
				foo['x'] += 1
				return ret

		@rv.monitor(m=M.m)
		def spec(event):
			if len(event.history) > 1:
				assert event.prev != event
				v = event.prev.fn.m.inputs[1]['x'] + event.prev.fn.m.result + event.prev.fn.m.outputs[1]['x']
				raise ValueError("prev vals %d" % v)

		a = M()
		a.m(dict(x=0))
		for i in range(1,10):
			with self.assertRaises(ValueError) as e:
				a.m(dict(x=i))
			self.assertEquals(e.exception.message, "prev vals %d" % ((i-1)*2 + i))

	# test history for single monitor
	def test_monitor_simple(self):
		class M(object):
			def m(self):
				pass

		@rv.monitor(m=M.m)
		def spec(event):
			assert event.fn.m.history[-1] == event.fn.m
			raise ValueError("call %d" % len(event.history))

		a = M()
		for i in range(1,10):
			with self.assertRaises(ValueError) as e:
				a.m()
			self.assertEquals(e.exception.message, "call %d" % i)

	def test_monitor_prev(self):
		class M(object):
			def m(self):
				pass

		@rv.monitor(m=M.m)
		def spec(event):
			if len(event.history) > 1:
				assert event.fn.m.history[-1] == event.fn.m
				assert event.fn.m.history[-2] == event.fn.m.prev
				assert event.history[-1].fn.m == event.fn.m
				assert event.history[-2].fn.m == event.fn.m.prev

		a = M()
		for i in range(1,10):
			a.m()

	def test_monitor_inputs_and_outputs(self):
		class M(object):
			def m(self, foo):
				ret = foo['x']
				foo['x'] += 1
				return ret

		@rv.monitor(m=M.m)
		def spec(event):
			if len(event.history) > 1:
				assert event.fn.m.prev != event.fn.m
				v = event.fn.m.prev.inputs[1]['x'] + event.fn.m.prev.result + event.fn.m.prev.outputs[1]['x']
				raise ValueError("prev vals %d" % v)


		a = M()
		a.m(dict(x=0))
		for i in range(1,10):
			with self.assertRaises(ValueError) as e:
				a.m(dict(x=i))
			self.assertEquals(e.exception.message, "prev vals %d" % ((i-1)*2 + i))

	# test many
	def test_many_monitors(self):
		class M(object):
			def m(self, i):
				pass
			def n(self, i):
				pass
			def o(self, i):
				pass

		@rv.monitor(m=M.m, n=M.n, o=M.o)
		def spec(event):
			self.assertEquals((len(event.history)-1)/3, event.active_function.inputs[1])
			self.assertEquals(len(event.active_function.history), event.active_function.inputs[1]+1)

			if event.fn.m.called:
				if len(event.history) > 1:
					self.assertTrue(event.prev.fn.o.called)
			if event.fn.n.called:
				self.assertTrue(event.prev.fn.m.called)
			if event.fn.o.called:
				self.assertTrue(event.prev.fn.n.called)

		a = M()
		old_default_size = rv.DEFAULT_MAX_HISTORY_SIZE
		rv.DEFAULT_MAX_HISTORY_SIZE = 100

		for i in range(10):
			a.m(i)
			a.n(i)
			a.o(i)

		rv.DEFAULT_MAX_HISTORY_SIZE = old_default_size
