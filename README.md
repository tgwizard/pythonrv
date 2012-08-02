# pythonrv

pythonrv is a runtime verification framework for python. It is the
implementation of a master thesis currently being written. Please see
[tgwizard.github.com/thesis](http://tgwizard.github.com/thesis) for more
information.

## Installing

pythonrv will be available as a pip package, with setup.py and everything.

## Coding

Clone the repository:

	git clone git@github.com:tgwizard/pythonrv.git
	cd pythonrv

Initialize the environment (preferrably through
[virtualenv](http://pypi.python.org/pypi/virtualenv), and possibly
[virtualenvwrapper](http://www.doughellmann.com/docs/virtualenvwrapper/)):

	pip install -r requirements.txt

Run the tests:

	./runtests.sh


## Runtime Verification

Runtime verification is the idea of verifying the correctness of a program
during its execution. Verification is done by checking of the program conforms
to its specifications.

There are several approaches to runtime verification, where pythonrv is one. It
is based on the idea that the specifications should be written in the target
programming language, in a similar manner to unit tests, and therefore make
them both more expressive and easier to learn.

The specifications written in pythonrv get "baked" into the target's source
code, so that whenever a function is called the specifications are executed as
well.

## Examples

First, lets say we have a function which correctness we want to verifiy:

~~~ python
# factorial.py
def factorial(n):
	res = 1
	for i in range(2, n)
		res *= i
	return res
~~~

We can now write specifications for it, preferably in another file:

~~~ python
# rvspecs.py
import factorial

@rv.monitor(fact=factorial.factorial)
def simple_specification(event):
	assert event.fn.fact.result >= event.fn.fact.inputs[0]

@rv.monitor(fact=factorial.factorial)
@rv.spec(history_size=rv.INFINITE_HISTORY_SIZE)
def simple_specification(event):
	in_out = (event.fn.fact.inputs[0], event.fn.fact.result)
	old_in_out = [(x.inputs[0], x.result) for x in event.fn.fact.history]

	for a in old_in_out:
		if in_out[0] > old_in_out[0]:
			assert in_out[1] >= old_in_out[1]
~~~

The first specification checks that all outputs are at least as big as the
inputs. The second specification verifies the input/output against the
historical data for the function; given a larger input, the output must be
larger-or-equal than before.

A specification is sent an event with information of the called function, its
history, and the history of all functions monitored by the specification.

~~~ python
@rv.monitor(fact=factorial.factorial)
@rv.spec(history_size=20)
def more_specifications(event):
	# here are all functions monitored
	event.fn
	# the currently called function can be accessed like this
	event.called_function
	# which in this case is the same as
	event.fn.fact

	# we can also check if a function was called
	assert event.fn.fact.called

	# the inputs, outputs and result can be accessed like this
	event.fn.fact.inputs        # a copy of the input argument tuple
	event.fn.fact.input_kwargs  # a copy of the input key-word argument dict
	event.fn.fact.outputs
	event.fn.fact.output_kwargs
	event.fn.fact.result

	# we can gain access to the previous event, and the previous function call
	event.prev
	event.fn.fact.prev

	# in this case, these two are equal
	assert event.prev.fn.fact == event.fn.fact.prev
	# but they needn't be if more than one function was monitored by this spec

	# we can gain access to the "entire" history
	for old_event in event.history:
		pass
	# and
	for old_fact_call in event.fn.fact.history:
		pass

	# we can also say that the next time some function, or a specific function,
	# that this spec montors something special should happen
	event.next(call_next_time)
	event.fn.fact.next(lambda e: None)

	# sometimes a specification can "finish" - it need not be verified again
	event.success("optional message telling that everything was ok")
	# or
	event.failure("we've failed, and there's no point continuing this verification")

def call_next_time(event):
	# here we gain access to all the same data as in the spec
~~~
