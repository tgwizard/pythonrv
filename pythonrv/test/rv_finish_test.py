# -*- coding: utf-8 -*-
import unittest

from pythonrv import rv

class TestSuccessAndFailure(unittest.TestCase):
	def test_success_removes_spec(self):
		class M(object):
			def m(self):
				pass

		@rv.monitor(m=M.m)
		def spec(event):
			event.success()
			raise ValueError("first time only")

		a = M()
		with self.assertRaises(ValueError) as e:
			a.m()
		self.assertEquals(e.exception.message, "first time only")

		a.m()
		a.m()
		a.m()

	def test_success_in_function_next(self):
		class M(object):
			def m(self):
				pass
			def n(self):
				pass

		@rv.monitor(m=M.m, n=M.n)
		def spec(event):
			event.fn.m.next(after)
			raise ValueError("first time only")

		def after(event):
			event.success()

		a = M()
		with self.assertRaises(ValueError) as e:
			a.m()
		self.assertEquals(e.exception.message, "first time only")

		a.m()
		a.m()
		a.m()

	def test_failure_removes_spec(self):
		class M(object):
			def m(self):
				pass

		@rv.monitor(m=M.m)
		def spec(event):
			event.failure("first time only")

		a = M()
		with self.assertRaises(AssertionError) as e:
			a.m()
		self.assertEquals(e.exception.message, "first time only")

		a.m()
		a.m()
		a.m()

	def test_failure_in_function_next(self):
		class M(object):
			def m(self):
				pass
			def n(self):
				pass

		@rv.monitor(m=M.m, n=M.n)
		def spec(event):
			event.fn.m.next(after)

		def after(event):
			event.failure("buffy")

		a = M()
		a.m()

		with self.assertRaises(AssertionError) as e:
			a.m()
		self.assertEquals(e.exception.message, "buffy")

		a.m()
		a.m()
		a.m()
