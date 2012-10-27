# -*- coding: utf-8 -*-

from pythonrv import rv
from pythonrv.dotdict import dotdict

##################################################################
### decorators
##################################################################

def formal_spec(spec):
    return _make_machine(spec())


##################################################################
### the basic specification functions
##################################################################

def make_assert(*stms):
    x = [_make_lambda(a) for a in stms]
    return x


def make_next(next):
    if callable(next):
        return [lambda e: (True, None, next())]
    else:
        return [lambda e: (True, None, next)]

def make_if(exp=None, then=None, els=None):
    assert not exp is None, "The exp parameter is required"
    assert not then is None, "The then parameter is required"

    exp_lambda = _make_lambda(exp)
    then_lambda = _make_lambda(then)
    else_lambda = _make_lambda(True if els is None else els)

    return [lambda e: then_lambda(e) if exp_lambda(e) else else_lambda(e)]

def _make_lambda(assertion):
    if callable(assertion):
        return assertion

    try:
        if callable(assertion[0]):
            return assertion[0]
    except:
        pass

    return lambda e: assertion

##################################################################
### the basic specification functions
##################################################################

class Machine(object):
    def __init__(self, transitions):
        self.transitions = transitions
        # TODO: do this in a cleaner way, such as a class decorator
        self._prv = dotdict()
        self._prv.spec_info = rv.SpecInfo()
        self._prv.spec_info.max_history_size = rv.NO_HISTORY


    def __call__(self, event):
        new_transitions = []
        errors = []

        for t in self.transitions:
            e, msg, new = _extract_transition_results(t, event)

            if not e:
                pass
                errors.append((e, msg))
            new_transitions += new

        self.transitions = new_transitions

        for e, msg in errors:
            assert e, msg


def _extract_transition_results(transition, event):
    result = transition(event)
    e = None
    msg = None
    new = []
    try:
        e, msg, new = result
    except:
        try:
            e, msg = result
        except:
            e = result
    return e, msg, new

def _make_machine(transitions):
    return Machine(transitions)
