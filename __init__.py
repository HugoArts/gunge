#! /usr/bin/env python

__all__ = ('event', 'clock', 'media', 'display')

#struct that will contain some objects like the event manager, display, and clock
class locals:
    interpolate = None
    manager = None
    display = None
    clock = None

#many modules depend on the event.manager existing, so do that first
import event

locals.manager = event.manager = event.Manager()


#import other modules
import clock
import media
import display
import sprite

def init(display_size, caption, background=None, flags=0):
    import pygame
    if background is None:
        background = pygame.Surface(display_size)
    locals.display = display.Display(display_size, caption, background, flags)
    locals.clock = clock.Clock(25)
    return (locals.manager, locals.display, locals.clock)

def set_interpolation(func):
    locals.interpolate = sprite.interpolate = func
