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
			self.assertEquals(event.history[0].prev, None)
			raise ValueError("call %d" % len(event.history))

		a = M()
		for i in range(rv.DEFAULT_MAX_HISTORY_SIZE):
			with self.assertRaises(ValueError) as e:
				a.m()
			self.assertEquals(e.exception.message, "call %d" % (i+1))

	def test_event_prev(self):
		class M(object):
			def m(self, i):
				pass

		@rv.monitor(m=M.m)
		def spec(event):
			if len(event.history) > 1:
				assert event.history[-2].fn.m.inputs[1] == event.prev.fn.m.inputs[1]

		a = M()
		for i in range(10):
			a.m(i)

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
		@rv.spec(history_size=10)
		def spec(event):
			raise ValueError("call %d" % len(event.history))

		a = M()
		for i in range(1,10):
			with self.assertRaises(ValueError) as e:
				a.m()
			self.assertEquals(e.exception.message, "call %d" % i)

	def test_monitor_prev(self):
		class M(object):
			def m(self, i):
				pass

		@rv.monitor(m=M.m)
		def spec(event):
			if len(event.history) > 1:
				assert event.history[-2].fn.m.inputs[1] == event.fn.m.prev.inputs[1]

		a = M()
		for i in range(10):
			a.m(i)

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

	# test history size limit
	def test_history_sizes(self):
		for i in range(35):
			# we always have at least 1 in the history
			history_size = max(i, 1)
			class M(object):
				def m(self):
					pass

			@rv.monitor(m=M.m)
			@rv.spec(history_size=i)
			def spec(event):
				raise ValueError("%d %d" % (len(event.history), len(event.fn.m.history)))

			a = M()
			for j in range(1, 80):
				with self.assertRaises(ValueError) as e:
					a.m()
				if (j <= history_size):
					self.assertEquals(e.exception.message, "%d %d" % (j, j))
				else:
					self.assertEquals(e.exception.message, "%d %d" % (history_size, history_size))

	def test_infinite_history_size(self):
		# won't really test infinite size...
		class M(object):
			def m(self):
				pass

		@rv.spec(history_size=rv.INFINITE_HISTORY_SIZE)
		@rv.monitor(m=M.m)
		def spec(event):
			raise ValueError(len(event.history))

		a = M()
		for i in range(200):
			with self.assertRaises(ValueError) as e:
				a.m()
			self.assertEquals(e.exception.message, i+1)

	def test_negative_history_size(self):
		class M(object):
			def m(self):
				pass

		with self.assertRaises(ValueError) as e:
			@rv.spec(history_size=-3)
			@rv.monitor(m=M.m)
			def spec(event):
				raise ValueError(len(event.history))
		self.assertEquals(e.exception.message, "Negative max history sizes (-3) are not allowed")

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
		@rv.spec(history_size=100)
		def spec(event):
			self.assertEquals((len(event.history)-1)/3, event.called_function.inputs[1])
			self.assertEquals(len(event.called_function.history), event.called_function.inputs[1]+1)

			if event.fn.m.called:
				if len(event.history) > 1:
					self.assertTrue(event.prev.fn.o.called)
			if event.fn.n.called:
				self.assertTrue(event.prev.fn.m.called)
			if event.fn.o.called:
				self.assertTrue(event.prev.fn.n.called)

		a = M()
		for i in range(10):
			a.m(i)
			a.n(i)
			a.o(i)
