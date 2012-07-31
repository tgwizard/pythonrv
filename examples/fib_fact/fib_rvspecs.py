from pythonrv import rv, dbc

from fib import fib

@rv.monitor(fib=fib)
def unit_test_spec(event):
	x = event.fn.fib.inputs[0]
	y = event.fn.fib.result

	if x == 1: assert y == 1
	if x == 2: assert y == 1
	if x == 3: assert y == 2
	if x == 4: assert y == 3
	if x == 5: assert y == 5
	if x == 6: assert y == 8

@rv.monitor(fib=fib)
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
