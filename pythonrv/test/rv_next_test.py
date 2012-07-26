# -*- coding: utf-8 -*-
import unittest

from pythonrv import rv

class TestMonitorsNext(unittest.TestCase):
	def test_monitors_next_simple(self):
		class M(object):
			def m(self):
				pass

		@rv.monitors(m=M.m)
		def spec(monitors):
			monitors.next(monitors.m)

		a = M()
		a.m()
		a.m()
		a.m()

	def test_monitors_next_more(self):
		class M(object):
			def m(self):
				pass
			def n(self):
				pass

		@rv.monitors(m=M.m, n=M.n)
		def spec(monitors):
			monitors.next(monitors.m)

		a = M()
		a.n()
		a.m()
		a.m()
		with self.assertRaises(AssertionError) as e:
			a.n()
		self.assertEquals(e.exception.message, "Next function called should have been m")

class TestMonitorNext(unittest.TestCase):
	def test_monitor_next_simple(self):
		class M(object):
			def m(self):
				pass

		def raise_error(monitors):
			raise ValueError("buffy")

		@rv.monitors(m=M.m)
		def spec(monitors):
			monitors.m.next(raise_error)

		a = M()
		a.m()
		with self.assertRaises(ValueError) as e:
			a.m()
		self.assertEquals(e.exception.message, "buffy")

	def test_monitor_next_multiple(self):
		class M(object):
			def m(self):
				pass
			def n(self):
				pass

		def raise_error(monitors):
			raise ValueError("buffy")

		@rv.monitors(m=M.m)
		def spec(monitors):
			monitors.m.next(raise_error)

		a = M()
		a.m()
		a.n()
		a.n()
		a.n()
		with self.assertRaises(ValueError) as e:
			a.m()
		self.assertEquals(e.exception.message, "buffy")

	def test_monitor_next_args(self):
		class M(object):
			def m(self):
				pass

		def raise_error(monitors, x, y, **kwargs):
			raise ValueError(x + y + kwargs.get('z', -1))

		@rv.monitors(m=M.m)
		def spec(monitors):
			monitors.m.next(raise_error, (1, 2), dict(z=15))

		a = M()
		a.m()
		with self.assertRaises(ValueError) as e:
			a.m()
		self.assertEquals(e.exception.message, 18)
