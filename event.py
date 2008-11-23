#! /usr/bin/env python

"""event.py - implement callback based event handling on top of the pygame event queue."""

import pygame

class Manager:
    """contains the main loop that handles all the events"""

    def __init__(self):
        self.handlers = {}
        
    def bind(self, handler):
        """bind handler object. The handler's callback will be called if the event occurs"""
        if handler.event_type not in self.handlers:
            self.handlers[handler.type] = []

       self.handlers[handler.type].append(handler)

    def unbind(self, handler):
        """unbind previously bound handler"""
        self.handlers[handler.type].remove(handler)

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
        # if the type matches, and all filter values match their event attributes, the handler is called
        if event.type is self.type and all(filter_val == getattr(event, filter_key) for (filter_val, filter_key) in self.filter.items()):
            self.func(event)


def bind(handler_list, eventtype, attr_filter):
    """decorator that can be used to statically bind methods. the first argument is a dict that must be declared as a class variable"""
    def decorator(func):
        handler = Handler(eventtype, func, attr_filter)
        handler_list[handler.func_name] = handler
        return func
    return decorator
