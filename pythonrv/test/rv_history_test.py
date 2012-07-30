# -*- coding: utf-8 -*-
import unittest

from pythonrv import rv

class TestHistory(unittest.TestCase):
	def test_simple(self):
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

	def test_prev(self):
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

	def test_inputs_and_outputs(self):
		class M(object):
			def m(self, foo):
				ret = foo['x']
				foo['x'] += 1
				return ret

		@rv.monitor(m=M.m)
		def spec(event):
			if len(event.history) > 1:
				assert event.prev != event
				print event.prev.fn.m.inputs
				print event.prev.fn.m.result
				print event.prev.fn.m.outputs
				v = event.prev.fn.m.inputs[1]['x'] + event.prev.fn.m.result + event.prev.fn.m.outputs[1]['x']
				raise ValueError("prev vals %d" % v)


		a = M()
		a.m(dict(x=0))
		for i in range(1,10):
			with self.assertRaises(ValueError) as e:
				a.m(dict(x=i))
			self.assertEquals(e.exception.message, "prev vals %d" % ((i-1)*2 + i))

