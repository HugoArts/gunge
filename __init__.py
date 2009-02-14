#! /usr/bin/env python

#many modules depend on the event.manager existing, so do that first
import event

manager = event.manager = event.Manager()


#import other modules
import clock
import media
