# -*- coding: utf-8 -*-
import unittest
import logging

from mock_and_helpers import TestLogging
from pythonrv import rv

error_levels = [rv.DEBUG, rv.INFO, rv.WARNING, rv.ERROR, rv.CRITICAL]

class TestConfiguration(unittest.TestCase):
	def test_configuration(self):
		config = rv.get_configuration()
		rv.configure(error_handler=1234)
		self.assertEquals(rv.get_configuration()['error_handler'], 1234)
		rv.configure(**config)

class TestRaiseExceptionErrorHandler(unittest.TestCase):
	def test_defaults(self):
		h = rv.RaiseExceptionErrorHandler()
		h.handle(rv.DEBUG, [AssertionError('buffy1')])
		h.handle(rv.INFO, [AssertionError('buffy2')])
		h.handle(rv.WARNING, [AssertionError('buffy3')])

		with self.assertRaises(AssertionError) as e:
			h.handle(rv.ERROR, [AssertionError('buffy4')])
		self.assertEquals(e.exception.message, 'buffy4')

		with self.assertRaises(AssertionError) as e:
			h.handle(rv.CRITICAL, [AssertionError('buffy5')])
		self.assertEquals(e.exception.message, 'buffy5')

	def test_levels(self):
		for level_i, level in enumerate(error_levels):
			h = rv.RaiseExceptionErrorHandler(level)
			for i, t in enumerate(error_levels):
				if i < level_i:
					h.handle(t, [AssertionError('spike')])
				else:
					with self.assertRaises(AssertionError) as e:
						h.handle(t, [AssertionError('willow')])
					self.assertEquals(e.exception.message, 'willow')


class TestLoggingErrorHandler(TestLogging):
	def test_defaults(self):
		h = rv.LoggingErrorHandler()

		h.handle(rv.DEBUG, [AssertionError('buffy1')])
		self.assertLog(logging.DEBUG, 'buffy1')

		h.handle(rv.INFO, [AssertionError('buffy2')])
		self.assertLog(logging.INFO, 'buffy2')

		h.handle(rv.WARNING, [AssertionError('buffy3')])
		self.assertLog(logging.WARNING, 'buffy3')

		h.handle(rv.ERROR, [AssertionError('buffy3')])
		self.assertLog(logging.ERROR, 'buffy3')

		h.handle(rv.CRITICAL, [AssertionError('buffy3')])
		self.assertLog(logging.CRITICAL, 'buffy3')

class TestRVWithLoggingErrorHandler(TestLogging):
	def setUp(self):
		super(TestRVWithLoggingErrorHandler, self).setUp()
		self.old_rv_config = rv.get_configuration()
		rv.configure(error_handler=rv.LoggingErrorHandler())

	def tearDown(self):
		super(TestRVWithLoggingErrorHandler, self).tearDown()
		rv.configure(**self.old_rv_config)

	def test_rv_logging(self):
		class M(object):
			def m(self):
				pass
		@rv.monitor(m=M.m)
		def spec(event):
			assert False, 'wheel'

		a = M()
		a.m()
		self.assertLog(logging.ERROR, 'wheel')

class TestSpecErrorLevels(TestLogging):
	def setUp(self):
		super(TestSpecErrorLevels, self).setUp()
		self.old_rv_config = rv.get_configuration()

	def tearDown(self):
		super(TestSpecErrorLevels, self).tearDown()
		rv.configure(**self.old_rv_config)

	def test_raise(self):
		for level_i, level in enumerate(error_levels):
			rv.configure(error_handler=rv.RaiseExceptionErrorHandler(level=level))
			for i, t in enumerate(error_levels):
				class M(object):
					def m(self):
						pass

				@rv.monitor(m=M.m)
				@rv.spec(level=t)
				def spec(event):
					assert False, "of time"

				a = M()
				if i < level_i:
					a.m()
				else:
					with self.assertRaises(AssertionError) as e:
						a.m()
					self.assertEquals(e.exception.message, 'of time')

	def test_log(self):
		rv.configure(error_handler=rv.LoggingErrorHandler())
		for i, t in enumerate(error_levels):
			class M(object):
				def m(self):
					pass

			@rv.monitor(m=M.m)
			@rv.spec(level=t)
			def spec(event):
				assert False, "of time"

			a = M()
			a.m()
			self.assertLog(t, "of time")

