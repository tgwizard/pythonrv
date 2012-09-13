# -*- coding: utf-8 -*-
import unittest

from pythonrv import rv

class TestEventNext(unittest.TestCase):
	def test_event_next_called_should_be(self):
		class M(object):
			def m(self):
				pass

		@rv.monitor(m=M.m)
		def spec(event):
			event.next_called_should_be(event.fn.m)

		a = M()
		a.m()
		a.m()
		a.m()

	def test_event_next_called_should_be_more(self):
		class M(object):
			def m(self):
				pass
			def n(self):
				pass

		@rv.monitor(m=M.m, n=M.n)
		def spec(event):
			event.next_called_should_be(event.fn.m)

		a = M()
		a.n()
		a.m()
		a.m()
		with self.assertRaises(AssertionError) as e:
			a.n()
		self.assertEquals(e.exception.message, "Next function called should have been m")

	def test_event_general_next(self):
		class M(object):
			def m(self):
				pass
			def n(self):
				pass

		@rv.monitor(m=M.m, n=M.n)
		def spec(event):
			event.next(after)

		def after(event):
			raise AssertionError("turtle power")

		a = M()
		a.m()
		with self.assertRaises(AssertionError) as e:
			a.m()
		self.assertEquals(e.exception.message, "turtle power")

		with self.assertRaises(AssertionError) as e:
			a.m()
		self.assertEquals(e.exception.message, "turtle power")

		with self.assertRaises(AssertionError) as e:
			a.m()
		self.assertEquals(e.exception.message, "turtle power")

class TestMonitorNext(unittest.TestCase):
	def test_monitor_next_simple(self):
		class M(object):
			def m(self):
				pass

		def raise_error(event):
			raise ValueError("buffy")

		@rv.monitor(m=M.m)
		def spec(event):
			event.fn.m.next(raise_error)

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

		def raise_error(event):
			raise ValueError("buffy")

		@rv.monitor(m=M.m)
		def spec(event):
			event.fn.m.next(raise_error)

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

		def raise_error(event, x, y, **kwargs):
			raise ValueError(x + y + kwargs.get('z', -1))

		@rv.monitor(m=M.m)
		def spec(event):
			event.fn.m.next(raise_error, (1, 2), dict(z=15))

		a = M()
		a.m()
		with self.assertRaises(ValueError) as e:
			a.m()
		self.assertEquals(e.exception.message, 18)
