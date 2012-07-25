# -*- coding: utf-8 -*-
import unittest

from pythonrv.dotdict import dotdict

class TestDotdict(unittest.TestCase):
	def test_initializer(self):
		d = dotdict(val=7, foo='x')
		assert 'val' in d
		assert d.val == 7
		assert d.foo == 'x'

	def test_set_get_del(self):
		d = dotdict()

		assert d.val == None
		d.val = 'x'
		assert d.val == 'x'
		assert d['val'] == 'x'
		del d.val
		assert d.val == None

		d['val'] = 7
		assert d['val'] == 7
		assert d.val == 7
		del d['val']
		assert d['val'] == None

	def test_in(self):
		d = dotdict()
		assert 'val' not in d
		d.val = 7
		assert 'val' in d
		del d.val
		assert 'val' not in d

	def test_str(self):
		d = dotdict(val=7, foo='x')
		e = dict(val=7, foo='x')
		assert str(d) == str(e)

		d2 = dict(x=d)
		e2 = dict(x=e)
		assert str(d2) == str(e2)
