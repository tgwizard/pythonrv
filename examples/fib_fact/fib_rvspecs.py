from pythonrv import rv, dbc

import fib

@rv.monitor(fib=fib.fib)
def unit_test_spec(event):
	x = event.fn.fib.inputs[0]
	y = event.fn.fib.result

	if x == 1: assert y == 1
	if x == 2: assert y == 1
	if x == 3: assert y == 2
	if x == 4: assert y == 3
	if x == 5: assert y == 5
	if x == 6: assert y == 8

@rv.monitor(fib=fib.fib)
def old_data_spec(event):
	x = event.fn.fib.inputs[0]
	y = event.fn.fib.result

	data = [(x.inputs[0], x.result) for x in event.fn.fib.history]

	for x2, y2 in data:
		if x < x2:
			assert y <= y2
		elif x > x2:
			assert y >= y2
		else:
			assert y == y2

@rv.monitor(fib=fib.fib)
@rv.spec(level=rv.DEBUG)
def debug_spec(event):
	assert False, 'debug message'

@rv.monitor(fib=fib.fib)
@rv.spec(level=rv.INFO)
def info_spec(event):
	assert False, 'info message'

@rv.monitor(fib=fib.fib)
@rv.spec(level=rv.WARNING)
def warning_spec(event):
	assert False, 'warning message'

@rv.monitor(fib=fib.fib)
@rv.spec(level=rv.ERROR)
def error_spec(event):
	assert False, 'error message'

@rv.monitor(fib=fib.fib)
@rv.spec(level=rv.CRITICAL)
def critical_spec(event):
	assert False, 'critical message'
