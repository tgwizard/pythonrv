# -*- coding: utf-8 -*-

# inspired by stuff on the web
class dotdict(object):
	def __init__(self, **kwargs):
		self.__dict__.update(kwargs)

	def __getattr__(self, attr):
		return self[attr]

	def __getitem__(self, attr):
		return self.__dict__.get(attr, None)

	def __setitem__(self, attr, val):
		self.__dict__[attr] = val
		return self.__dict__[attr]

	def __delitem__(self, attr):
		del self.__dict__[attr]

	def __contains__(self, attr):
		return attr in self.__dict__

	def __repr__(self):
		return repr(self.__dict__)
