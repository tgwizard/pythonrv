# -*- coding: utf-8 -*-
import unittest

from pythonrv import dbc

# define the functions we want to verify
def func_adam():
	return "adam"

def func_buffy():
	return "buffy"

def func_ceasar():
	return "ceasar"

def func_desmond(k, x=''):
	return k + func_desmond.val + x

def func_margaret():
	pass

def func_spike(x):
	return x

def func_zorro(x):
	return "zorro"

def func_attributes():
	return func_attributes.test_attrib
func_attributes.test_attrib = "test"

class AlohaGlobal(object):
	def __init__(self, x):
		self.x = x

	def shoot(self):
		return self.x

# and the tests
class TestOnFunctions(unittest.TestCase):
	def test_invalid_function_reference(self):
		with self.assertRaises(ValueError):
			@dbc.before('func_margaret')
			def a():
				pass

	def test_nonexisting_function(self):
		with self.assertRaises(ValueError):
			@dbc.before('func_this_doesnt_exist')
			def a():
				pass

	def test_local_function_not_working(self):
		def f():
			pass

		with self.assertRaises(ValueError):
			@dbc.before(f)
			def a():
				pass
		with self.assertRaises(ValueError):
			@dbc.before('f')
			def a():
				pass

	def test_return_value(self):
		@dbc.before(func_adam)
		def pre():
			x = 17
			return 4
		res = func_adam()
		assert "adam" == res

	def test_before_exec(self):
		@dbc.before(func_buffy)
		def pre():
			raise ValueError("precondition run")
		with self.assertRaises(ValueError):
			func_buffy()

	def test_after_exec(self):
		@dbc.before(func_ceasar)
		def post():
			raise ValueError("postcondition run")
		with self.assertRaises(ValueError):
			func_ceasar()

	def test_several_conditions(self):
		func_desmond.val = ''

		@dbc.before(func_desmond)
		def a(k, **kwargs):
			func_desmond.val += k + 'a' + kwargs['x']
		@dbc.after(func_desmond)
		def c(k, **kwargs):
			func_desmond.val += k + 'c' + kwargs['x']
		@dbc.after(func_desmond)
		def d(k, **kwargs):
			func_desmond.val += k + 'd' + kwargs['x']
		@dbc.before(func_desmond)
		def b(k, **kwargs):
			func_desmond.val += k + 'b' + kwargs['x']

		res = func_desmond('>', x='<')

		self.assertEqual(res, '>>a<>b<<')
		self.assertEqual(func_desmond.val, '>a<>b<>c<>d<')

	def test_existing_func_attribute(self):
		@dbc.before(func_attributes)
		def a():
			pass

		self.assertEquals(func_attributes.test_attrib, 'test')

	def test_explicit_call(self):
		def p(x):
			if x == 'p':
				raise ValueError('p')
		def m(x):
			if x == 'm':
				raise ValueError('m')
		def n(x):
			if x == 'n':
				raise ValueError('n')

		dbc.before(func_zorro)((p,m))
		dbc.after(func_zorro)(n)

		res = func_zorro(None)
		self.assertEquals(res, "zorro")

		with self.assertRaises(ValueError) as e:
			func_zorro('p')
		self.assertEquals(e.exception.message, 'p')

		with self.assertRaises(ValueError) as e:
			func_zorro('m')
		self.assertEquals(e.exception.message, 'm')

		with self.assertRaises(ValueError) as e:
			func_zorro('n')
		self.assertEquals(e.exception.message, 'n')

	def test_calling_cond_alone(self):
		class Aloha:
			def m(self, x):
				return x+1

		def p(self, x):
			if self == 8:
				raise ValueError("buffy")
			return 7

		q = dbc.before(Aloha, 'm')(p)

		with self.assertRaises(ValueError) as e:
			q(8, 7)
		self.assertEquals(e.exception.message, "buffy")
		self.assertEquals(q(None, 3), 7)

		@dbc.after(Aloha.m)
		def z(self, x):
			return 17

		self.assertEquals(z(None, None), 17)

class TestOnClassFunctions(unittest.TestCase):
	def test_method(self):
		class Aloha:
			def m(self):
				pass

		@dbc.before(Aloha, 'm')
		def a(self):
			pass
		@dbc.before(Aloha, Aloha.m)
		def b(self):
			pass

	def test_method_only_func_not_working(self):
		class Aloha:
			def m(self):
				pass

		@dbc.before(Aloha.m)
		def a(self):
			pass

	def test_classmethod(self):
		class Aloha:
			@classmethod
			def m(cls):
				pass

		@dbc.before(Aloha, 'm')
		def a(cls):
			pass
		@dbc.before(Aloha, Aloha.m)
		def b(cls):
			pass

	def test_staticmethod(self):
		class Aloha:
			@staticmethod
			def m():
				pass

		@dbc.before(Aloha, 'm')
		def a():
			pass
		@dbc.before(Aloha, Aloha.m)
		def b():
			pass

	def test_method_global_class(self):
		@dbc.before(AlohaGlobal, AlohaGlobal.shoot)
		def a(self):
			self.x += 1

		@dbc.after(AlohaGlobal, 'shoot')
		def b(self):
			self.x += 2

		obj = AlohaGlobal(2)
		res = obj.shoot()

		self.assertEquals(res, 3)
		self.assertEquals(obj.x, 5)

	def test_method_local_class(self):
		class Aloha(object):
			def __init__(self, x):
				self.x = x

			def shoot(self):
				return self.x

		@dbc.before(Aloha, 'shoot')
		def a(self):
			self.x += 1

		@dbc.after(Aloha, Aloha.shoot)
		def b(self):
			self.x += 2

		obj = Aloha(2)
		res = obj.shoot()

		self.assertEquals(res, 3)
		self.assertEquals(obj.x, 5)

	def test_class_method(self):
		class Aloha(object):
			@classmethod
			def cm(cls, x):
				return x + 1

			def adsf(self):
				pass

		@dbc.before(Aloha, Aloha.cm)
		def a(cls, x):
			cls.val += 'a'

		@dbc.after(Aloha, 'cm')
		def b(cls, x):
			cls.val += 'b'

		Aloha.val = 'q'

		class_res = Aloha.cm(7)
		self.assertEquals(class_res, 8)
		self.assertEquals(Aloha.val, 'qab')

		Aloha.val += '_'
		obj = Aloha()
		obj_res = obj.cm(2)
		self.assertEquals(obj_res, 3)
		self.assertEquals(Aloha.val, 'qab_ab')

	def test_static_method(self):
		class Aloha(object):
			@staticmethod
			def sm(x):
				return x + 1

		@dbc.before(Aloha, 'sm')
		def a(x):
			Aloha.val += 'a'
			pass

		@dbc.after(Aloha, 'sm')
		def b(x):
			Aloha.val += 'b'
			pass

		Aloha.val = 'q'
		class_res = Aloha.sm(7)
		self.assertEquals(class_res, 8)
		self.assertEquals(Aloha.val, 'qab')

		Aloha.val += '_'
		obj = Aloha()
		obj_res = obj.sm(2)
		self.assertEquals(obj_res, 3)
		self.assertEquals(Aloha.val, 'qab_ab')

	def test_object(self):
		class Aloha:
			def __init__(self, v):
				self.v = v
			def m(self, x):
				return x

		a = Aloha('a')
		b = Aloha('b')

		# binding on existing object on fresh method
		@dbc.after(b.m)
		def p(self, x):
			raise ValueError("buffy %s" % self.v)

		self.assertEquals(a.m(7), 7)

		with self.assertRaises(ValueError) as e:
			b.m(8)
		self.assertEquals(e.exception.message, "buffy b")

		# binding directly through existing object on fresh method
		@dbc.before(a.m)
		def p(self, x):
			if x == 'a':
				raise ValueError("spike %s" % x)
		self.assertEquals(a.m(7), 7)
		with self.assertRaises(ValueError) as e:
			a.m('a')
		self.assertEquals(e.exception.message, "spike a")
		self.assertEquals(a.m(7), 7)

		# binding on existing object on already bound method
		@dbc.before(b.m)
		def p(self, x):
			raise ValueError("angel %s" % self.v)
		self.assertEquals(a.m(7), 7)
		b.v = 'b2'
		with self.assertRaises(ValueError) as e:
			b.m(8)
		self.assertEquals(e.exception.message, "angel b2")
