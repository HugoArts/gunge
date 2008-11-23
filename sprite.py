#! /usr/bin/env python

"""sprite.py - sprite class for everything that appears on screen"""

from gunge import event

class Sprite:
    """Base class for all game objects - 2D only"""
    handlers = {}

    def __init__(self, img, rect):
        self.img = img
        self.rect = rect

        for name, handler in self.handlers.items():
            handler.func = getattr(self, name)
            event.manager.bind(handler)
