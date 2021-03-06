#! /usr/bin/env python

"""implement callback based event handling on top of the pygame event queue.

Some of the features are pseudo-static event binding using decorator syntax and advanced event filtering"""

import pygame
import inspect
import weakref
import gunge

#event types
UPDATE = pygame.USEREVENT + 1
RENDER = pygame.USEREVENT + 2
BUFSWAP = pygame.USEREVENT + 3

USEREVENT = pygame.USEREVENT + 4

#event return codes
HANDLE_AGAIN = -1
HANDLE_STOP  = -2

class Manager(object):
    """contains the main loop that handles all the events"""

    def __init__(self):
        self.handlers = {}
        self.bind(self.on_quit, pygame.QUIT)

    def on_quit(self, event):
        """default handler for the QUIT event, simply causes the mainloop function to return."""
        self.keeprunning = False

    def bind(self, handler, event_type=None):
        """bind handler object. The handler's callback will be called if the event occurs

        The event_type argument is only needed if the handler argument is not a Binder instance
        """
        event_type = event_type or handler.type
        if event_type not in self.handlers:
            self.handlers[event_type] = []

        self.handlers[event_type].append(handler)

    def unbind(self, handler, event_type=None):
        """unbind previously bound handler

        The event_type argument is only needed if the handler argument is not a Binder instance
        """
        event_type = event_type or handler.type
        self.handlers[event_type].remove(handler)

    def mainloop(self):
        """main loop of the program, dispatches events to handlers"""
        exit_events = [pygame.event.Event(UPDATE, {}),
                       pygame.event.Event(RENDER, {'interpolate': lambda: gunge.locals.clock.interpolate, 'display': gunge.locals.display}),
                       pygame.event.Event(BUFSWAP, {})]
        self.keeprunning = True
        while self.keeprunning:
            events = pygame.event.get() + exit_events
            while not len(events) == 0:
                event = events.pop()
                for handler in self.handlers.get(event.type, []):
                    a = handler(event)
                    if a == HANDLE_STOP:
                        break
                    elif a == HANDLE_AGAIN:
                        events.insert(0, event)


class Binder(object):
    """represents a callback for a specific event"""

    def __init__(self, eventtype, attr_filter, callback):
        """create a new event binder for the specified type

        The callback will be invoked if the event occurs, provided the binder is actually bound in the manager. The attr_filter can be used to specify
        constraints that certain attributes of the event must satisfy for the callback to be invoked. It is a dictionary of the form {'attr_name': filter_value}

        The filter value can have several different types, with different behaviours:
        - set:      passes if event.attr_name in filter_value
        - function: passes if filter_value(event.attr_name) is True
        - other:    passes if filter_value == event.attr_name
        """
        self.type = eventtype
        self.filter = attr_filter
        self.func = callback

        if len(inspect.getargspec(callback)[0]) == 2:
            self.instances = []
            self.call = self.method_call
        else:
            self.call = self.function_call

    def __call__(self, event):
        self.call(event)

    def filter_check(self, event):
        """check whether the filter matches the event."""
        for key, value in self.filter.items():
            event_key = getattr(event, key)
            #set: pass if any of the sets' values matches the event attribute
            if type(value) is set:
                if event_key not in value: return False
            #function: pass if the function returns True when called with the event attribute
            elif inspect.isroutine(value):
                if not value(event_key): return False
            #anything else: pass if the value matches the event attribute
            elif value != event_key:
                return False

        return True

    def method_call(self, event):
        """this is the callback activation method if the bound object is a method.

        if the bound object is a function, function_call will be used instead. It differs because methods will be called on each instance.
        """
        if self.filter_check(event):
            self.instances = filter(lambda x: x() is not None, self.instances)
            for instance in self.instances:
                self.func(instance(), event)

    def function_call(self, event):
        if self.filter_check(event):
            self.func(event)


class Handler(object):
    """class that can use the bind decorator.

    The bind decorator basically annotates the method with the required binding information through an attribute called binders.
    The actual binding is done in the __init__ function of this class. It looks through all of the members of the self object, and all
    methods that have the binders attribute will be bound at that time. This means that derived classes will retain the bindings of their parents,
    unless the method is overridden. In that case, the bindings must be explicity re-stated, which is desirable for clarity's sake.
    """

    def __init__(self):
        """intialize event handlers"""
        for name, method in inspect.getmembers(self, lambda mem: inspect.ismethod(mem) and hasattr(mem, 'binders')):
            for binder in method.binders:
                binder.instances.append(weakref.ref(self))

    def kill(self):
        """unbinds all event handlers for this instance. The worst thing that can be done to an object short of actually destroying it"""
        for name, method in inspect.getmembers(self, lambda mem: inspect.ismethod(mem) and hasattr(mem, 'binders')):
            for binder in method.binders:
                binder.instances = filter(lambda i: i() is not self, binder.instances)


def bind(eventtype, attr_filter=None):
    """decorator that can be used to statically bind methods. the first argument is a dict that must be declared as a class variable

    Note that this decorator must be used with an object derived from the Handler class, as the actual binding is done in the __init__ of that class.
    It is perfectly legal for a function to have multiple event bindings, and the bind decorator handles this.
    """
    if attr_filter is None:
        attr_filter = {}

    def decorator(func):
        if len(inspect.getargspec(func)[0]) > 2:
            raise ValueError("Function does not have correct number of arguments (expected (self, event) or (event))")
        binder = Binder(eventtype, attr_filter, func)
        manager.bind(binder)

        try:
            func.binders.append(binder)
        except AttributeError:
            func.binders = [binder]
        return func
    return decorator
