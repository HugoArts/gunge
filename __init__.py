#! /usr/bin/env python

__all__ = ('event', 'clock', 'media', 'display')

#many modules depend on the event.manager existing, so do that first
import event

manager = event.manager = event.Manager()


#import other modules
import clock
import media
import display
