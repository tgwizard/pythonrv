# -*- coding: utf-8 -*-

# I do sincerely apologise for the mess below. But the idea is quite simple:
# A callback is registered as a receiver to the signals. When called, this
# callback calls a monitoree, which is the function returned for monitoring.

##################################################################
### decorators
##################################################################

_counter = 0
_current_module = __import__(__name__)

def signal_monitoree(*signals):
    global _counter, _current_module
    monitoree_name = "django-signal-monitoree-%d" % _counter
    callback_name = "django-signal-callback-%d" % _counter
    _counter += 1

    def monitoree(sender, **kwargs):
        pass
    monitoree.__name__ = monitoree_name
    setattr(_current_module, monitoree_name, monitoree)

    def callback(sender, **kwargs):
        getattr(_current_module, monitoree_name)(sender, **kwargs)
    callback.__name__ = callback_name
    setattr(_current_module, callback_name, callback)

    for signal in signals:
        signal.connect(getattr(_current_module, callback_name))

    return _current_module, getattr(_current_module, monitoree_name)
