# -*- coding: utf-8 -*-
import unittest

from pythonrv import dbc

class TestState(unittest.TestCase):
	def test_state_and_simple_args(self):
		@dbc.use_state()
		def p(state):
			assert state.function_name == 'm'
			assert 'result' not in state
			assert 'inargs' not in state
			assert 'inkwargs' not in state
			assert 'outargs' not in state
			assert 'outkwargs' not in state
			assert len(state.args) == 1
			assert state.args[0] == 2
			assert len(state.kwargs) == 0

		@dbc.contract(pre=p)
		def m(x, y=7, **kwargs):
			return x + y

		# multiple calls to make sure cleanup is done
		assert m(2) == 9
		assert m(2) == 9
		assert m(2) == 9
		assert m(2) == 9

	def test_kwargs_simple(self):
		@dbc.use_state()
		def p(state):
			assert len(state.args) == 1
			assert state.args[0] == 2
			assert len(state.kwargs) == 2
			assert state.kwargs['y'] == 12
			assert state.kwargs['z'] == 5

		@dbc.contract(pre=p)
		def m(x, y=7, **kwargs):
			return x + y + kwargs['z']

		# multiple calls to make sure cleanup is done
		assert m(2, y=12, z=5) == 2+12+5
		assert m(2, y=12, z=5) == 2+12+5
		assert m(2, y=12, z=5) == 2+12+5
		assert m(2, y=12, z=5) == 2+12+5

	def test_output_args_going_through(self):
		@dbc.use_state()
		def p(state):
			assert 'result' not in state

			assert len(state.args[0]) == 1
			assert state.args[0]['moo'] == 2
			assert len(state.kwargs) == 1
			assert len(state.kwargs['y']) == 0

		@dbc.use_state()
		def q(state):
			assert 'result' in state
			assert state.result == 12

			assert len(state.args[0]) == 2
			assert state.args[0]['moo'] == 3
			assert len(state.kwargs) == 1
			assert len(state.kwargs['y']) == 1
			assert state.kwargs['y']['val'] == 7

		@dbc.contract(pre=p,post=q)
		def m(x, y=None):
			x['foo'] = 'bar'
			x['moo'] = 3
			if not y is None:
				y['val'] = 7
			return 12

		assert m({'moo': 2}, y={}) == 12
		assert m({'moo': 2}, y={}) == 12
		assert m({'moo': 2}, y={}) == 12

	def test_inargs(self):
		@dbc.use_state(inargs = True)
		def p(state):
			assert 'result' not in state
			assert 'inargs' in state
			assert 'inkwargs' in state

			assert len(state.args[0]) == 1
			assert state.args[0]['moo'] == 2
			assert len(state.kwargs) == 1
			assert len(state.kwargs['y']) == 0

			assert state.args == state.inargs
			assert state.kwargs == state.inkwargs

		@dbc.use_state(inargs = False)
		def p2(state):
			# these fields are not present because p doesn't require them
			assert 'inargs' in state
			assert 'inkwargs' in state


		@dbc.use_state()
		def q(state):
			assert 'result' in state
			assert state.result == 12

			assert len(state.args[0]) == 2
			assert state.args[0]['moo'] == 3
			assert len(state.kwargs) == 1
			assert len(state.kwargs['y']) == 1
			assert state.kwargs['y']['val'] == 7

			assert state.args != state.inargs
			assert state.kwargs != state.inkwargs

			assert len(state.inargs[0]) == 1
			assert state.inargs[0]['moo'] == 2
			assert len(state.inkwargs) == 1
			assert len(state.inkwargs['y']) == 0

		@dbc.contract(pre=(p,p2),post=q)
		def m(x, y=None):
			x['foo'] = 'bar'
			x['moo'] = 3
			if not y is None:
				y['val'] = 7
			return 12

		assert m({'moo': 2}, y={}) == 12
		assert m({'moo': 2}, y={}) == 12
		assert m({'moo': 2}, y={}) == 12

	def test_local_store(self):
		@dbc.use_state(local_store = True)
		def p(state):
			assert 'local_store' in state
			state.local_store['val'] = state.local_store.get('val', 0)+1
			assert state.local_store['val'] == state.args[0]

		@dbc.use_state(local_store = True)
		def p2(state):
			state.local_store['val'] = state.local_store.get('val', 0)+2
			assert state.local_store['val'] == state.args[0] * 2

		@dbc.use_state(local_store = True)
		def q(state):
			state.local_store['val'] = state.local_store.get('val', 0)-1
			assert state.local_store['val'] == state.args[0] * -1

		@dbc.contract(pre=(p,p2),post=q)
		def m(i):
			return -1

		for i in range(1,10):
			assert m(i) == -1

	def test_state_many_masters(self):
		@dbc.use_state(local_store = True)
		def p(state):
			fn = state.function_name
			if fn == 'd':
				assert state.args[0] == -1
				state.local_store['val'] = 'n'
			elif fn == 'm':
				assert state.local_store['val'] == 'n'
				state.local_store['val'] = 'm'
			elif fn == 'n':
				assert state.local_store['val'] == 'm'
				state.local_store['val'] = 'n'
			else:
				assert False, "Unknown function caller %s" % fn

		@dbc.contract(pre=p)
		def m():
			pass

		@dbc.contract(pre=p)
		def n():
			pass

		@dbc.contract(pre=p)
		def d(i):
			pass

		d(-1)
		for i in range(20):
			m()
			n()
