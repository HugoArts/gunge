#! /usr/bin/env python

"""event.py - implement callback based event handling on top of the pygame event queue."""

import pygame, inspect

class Manager:
    """contains the main loop that handles all the events"""

    def __init__(self):
        self.handlers = {}
        self.bind(self.on_quit, pygame.QUIT)

    def on_quit(self, event):
        self.keeprunning = False

    def bind(self, handler, event_type=None):
        """bind handler object. The handler's callback will be called if the event occurs"""
        event_type = event_type or handler.type
        if event_type not in self.handlers:
            self.handlers[event_type] = []

        self.handlers[event_type].append(handler)

    def unbind(self, handler, event_type=None):
        """unbind previously bound handler"""
        event_type = event_type or handler.type
        self.handlers[event_type].remove(handler)

    def mainloop(self):
        """main loop of the program, dispatches events to handlers""" 
        self.keeprunning = True

        while self.keeprunning:
            for event in pygame.event.get():
                for handler in self.handlers.get(event.type, []):
                    handler(event)


class Binder:
    """represents a handler for a specific event"""

    def __init__(self, eventtype, callback, attr_filter):
        """create a new event binder for the specified type
        the callback will be invoked if the event occurs, provided the binder is actually bound in the manager. The attr_filter can be used to specify
        values that certain attributes of the event must have for the callback to be invoked. It is a dictionary of the form {'attr_name': required_value}
        """
        self.type = eventtype
        self.func = callback
        self.filter = attr_filter

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

        self.func(event)


def bind(handler_list, eventtype, attr_filter):
    """decorator that can be used to statically bind methods. the first argument is a dict that must be declared as a class variable"""
    def decorator(func):
        print func
        if len(inspect.getargspec(func)[0]) != 2:
            raise ValueError("Function does not have correct number of arguments (expected (self, event))")

        handler_list.append((func.func_name, eventtype, attr_filter))
        return func
    return decorator
