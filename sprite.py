#! /usr/bin/env python

"""sprite.py - sprite class for everything that appears on screen"""

from gunge import event

class Sprite:
    """Base class for all game objects - 2D only"""
    handlers = []

    def __init__(self, img, rect):
        self.img = img
        self.rect = rect
        self.binders = []

        for name, (evt_type, attr_filter) in self.handlers.items():
            binder = event.Binder(evt_type, getattr(self, name), attr_filter)
            self.binders.append(binder)
            event.manager.bind(binder)
