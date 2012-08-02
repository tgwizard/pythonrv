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

We can now write a specification for it, preferably in another file:

~~~ python
# rvspecs.py
import factorial

@rv.monitor(fact=factorial.factorial)
def simple_specification(event):
	assert event.fn.f.result >= event.fn.f.inputs[0]
~~~

This specification checks that all outputs are at least as big as the inputs.


