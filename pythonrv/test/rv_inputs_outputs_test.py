# -*- coding: utf-8 -*-
import unittest
from nose.tools import nottest

from pythonrv import rv

class TestInputOutput(unittest.TestCase):
	def test_inputs_outputs(self):
		class M(object):
			def m(self, x, y=None, **kwargs):
				self.foo ='m'
				x['x2'] = 9
				y = -1
				kwargs['z']['z'] = 0
				return 'ret'

		@rv.monitor(m=M.m)
		def spec(event):
			inputs = event.fn.m.inputs
			input_kwargs = event.fn.m.input_kwargs
			old_self, x = inputs
			y = input_kwargs['y']
			z = input_kwargs['z']

			result = event.fn.m.result

			outputs = event.fn.m.outputs
			output_kwargs = event.fn.m.output_kwargs
			out_self, out_x = outputs
			out_y = output_kwargs['y']
			out_z = output_kwargs['z']

			raise ValueError("in(%s %s %s %s) result(%s) out(%s %s %s %s)" %
					(old_self.foo, x, y, z, result, out_self.foo, out_x, out_y, out_z))

		a = M()
		a.foo = 'initial'
		with self.assertRaises(ValueError) as e:
			a.m({'x': 7}, y='y', z={'z': 8})
		self.assertEquals(e.exception.message,
				"in(initial {'x': 7} y {'z': 8}) result(ret) out(m {'x2': 9, 'x': 7} y {'z': 0})")

	@nottest
	def test_input_output_copied_in_history(self):
		# TODO:
		# I don't have the energy to fix this now
		# the problem is now that the outputs in an event is the args part of
		# the dbc state, but it should be the outargs. But if we use outargs, then
		# we cannot modify the output data, so it is more difficult to write
		# tests...
		class M(object):
			def m(self, some_dict):
				pass

		@rv.monitor(m=M.m)
		def spec(event):
			if len(event.history) == 1:
				self.assertEquals(event.fn.m.inputs[1]['x'], 'a')
				event.fn.m.inputs[1]['x'] = 'b'
				self.assertEquals(event.fn.m.inputs[1]['x'], 'b')
				self.assertEquals(event.fn.m.outputs[1]['x'], 'a')
				event.fn.m.outputs[1]['x'] = 'b'
				self.assertEquals(event.fn.m.outputs[1]['x'], 'b')
			else:
				self.assertEquals(event.prev.fn.m.inputs[1]['x'], 'b')
				self.assertEquals(event.prev.fn.m.outputs[1]['x'], 'b')

		a = M()
		some_dict = dict(x = 'a')
		a.m(some_dict)
		self.assertEquals(some_dict['x'], 'b')

		some_dict['x'] = 'c'
		a.m(some_dict)
		self.assertEquals(some_dict['x'], 'c')

		assert False


	def test_spec_executed_after(self):
		class M(object):
			def m(self):
				raise ValueError("m")

		@rv.monitor(m=M.m)
		def spec(event):
			raise ValueError("spec")

		a = M()
		with self.assertRaises(ValueError) as e:
			a.m()
		self.assertEquals(e.exception.message, "m")
