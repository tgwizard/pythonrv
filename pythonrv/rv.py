# -*- coding: utf-8 -*-
import instrumentation

_registered_specs = []

def spec(func):
	# dummy decorator
	return func

def monitors(**kwargs):
	def decorator(spec):
		return spec

def register(*specs):
	_registered_specs.extend(specs)
