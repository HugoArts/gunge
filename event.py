#! /usr/bin/env python

"""implement callback based event handling on top of the pygame event queue.

Some of the features are pseudo-static event binding using decorator syntax and advanced event filtering"""

import pygame
import inspect

#event types
UPDATE = pygame.USEREVENT + 1
RENDER = pygame.USEREVENT + 2
BUFSWAP = pygame.USEREVENT + 3

class Manager:
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
                       pygame.event.Event(RENDER, {}),
                       pygame.event.Event(BUFSWAP, {})]
        self.keeprunning = True

        while self.keeprunning:
            events = pygame.event.get() + exit_events
            while not len(events) == 0:
                event = events.pop()
                for handler in self.handlers.get(event.type, []):
                    try:
                        handler(event)
                    except StopHandling:
                        break
                    except HandleAgain:
                        events.insert(0, event)


class Binder:
    """represents a callback for a specific event"""

    def __init__(self, eventtype, attr_filter, *callbacks):
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
        self.funcs = list(callbacks)

    def __call__(self, event):
        """this is used as the callback activation, so that regular functions can also be added to the manager""" 
        #checking whether the filter matches. Several things are accepted as filter values
        for key, value in self.filter.items():
            event_key = getattr(event, key)
            #set: pass if any of the sets' values matches the event attribute
            if type(value) is set:
                if event_key not in value: return
            #function: pass if the function returns True when called with the event attribute
            elif inspect.isroutine(value):
                if not value(event_key): return
            #anything else: pass if the value matches the event attribute
            elif value != event_key:
                return

        for func in self.funcs:
            func(event)


class Handler:
    """class that can use the bind decorator.

    The bind decorator basically annotates the method with the required binding information through an attribute called binders.
    The actual binding is done in the __init__ function of this class. It looks through all of the members of the self object, and all
    methods that have the binders attribute will be bound at that time. This means that derived classes will retain the bindings of their parents,
    unless the method is overridden. In that case, the bindings must be explicity re-stated, which is desirable for clarity's sake.
    """

    def __init__(self):
        for name, method in inspect.getmembers(self, lambda mem: inspect.ismethod(mem) and hasattr(mem, 'binders')):
            for binder in method.binders:
                binder.funcs.append(method)


class StopHandling(Exception):
    """exception that can be thrown from inside an event handler to stop further handling of that event"""
    pass


class HandleAgain(Exception):
    """exception that can be thrown from inside an event handler to reinsert the current event into the front of the queue"""
    pass


def bind(eventtype, attr_filter=None):
    """decorator that can be used to statically bind methods. the first argument is a dict that must be declared as a class variable

    Note that this decorator must be used with an object derived from the Handler class, as the actual binding is done in the __init__ of that class.
    It is perfectly legal for a function to have multiple event bindings, and the bind decorator handles this.
    """
    if attr_filter is None:
        attr_filter = {}

    def decorator(func):
        if len(inspect.getargspec(func)[0]) != 2:
            raise ValueError("Function does not have correct number of arguments (expected (self, event))")
        binder = Binder(eventtype, attr_filter)
        manager.bind(binder)

        try:
            func.binders.append(binder)
        except AttributeError:
            func.binders = [binder]
        return func
    return decorator
