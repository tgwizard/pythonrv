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

	def test_remove_and_next_still_called(self):
		class M(object):
			def m(self):
				pass
			def n(self):
				pass

		@rv.monitor(m=M.m, n=M.n)
		def spec(event):
			event.next(after)
			event.finish()

		self.assertEquals(len(M.m._prv.rv.specs), 1)
		self.assertEquals(len(M.n._prv.rv.specs), 1)

		def after(event):
			event.fn.n.next(after2)
			raise AssertionError("spike")

		def after2(event):
			raise AssertionError("hacket")

		a = M()
		a.m()
		with self.assertRaises(AssertionError) as e:
			a.m()
		self.assertEquals(e.exception.message, "spike")

		self.assertEquals(len(M.m._prv.rv.specs), 1)
		self.assertEquals(len(M.n._prv.rv.specs), 1)

		a.m()
		a.m()
		a.m()

		with self.assertRaises(AssertionError) as e:
			a.n()
		self.assertEquals(e.exception.message, "hacket")


		self.assertEquals(len(M.m._prv.rv.specs), 0)
		self.assertEquals(len(M.n._prv.rv.specs), 0)

		a.n()
		a.m()
		a.n()

	def test_complex_remove(self):
		class M(object):
			def m(self):
				pass
			def n(self):
				pass


		@rv.monitor(m=M.m,n=M.n)
		def spec1(event):
			event.called_function.outputs[0].calls += "1"
			if event.fn.n.called:
				event.success()
			pass

		@rv.monitor(m=M.m,n=M.n)
		def spec2(event):
			event.called_function.outputs[0].calls += "2"
			pass

		a = M()
		a.calls = ">"
		a.m()
		self.assertEquals(">12", a.calls)
		a.m()
		self.assertEquals(">1212", a.calls)
		a.n()
		self.assertEquals(">121212", a.calls)

		a.m()
		self.assertEquals(">1212122", a.calls)
		a.n()
		self.assertEquals(">12121222", a.calls)
