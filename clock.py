#! /usr/bin/env python

"""Time related classes and functions, most importantly the Clock class, which can be used to decouple game logic and rendering"""

import gunge.event
import time

class Clock(event.Handler):
    """used to separate game logic updates from rendering, i.e. not update the game every frame.

    This is done by being the first object to register for the UPDATE event. If not enough time has passed yet
    for a game update to occur, StopHandling will be raised to cancel the update. If too much time has passed, the
    clock can reinsert another UPDATE event to update again without rendering.
    """

    def __init__(self, tps=25):
        """initialize the clock.

        tps = ticks per second, the amount of game updates allowed per second
        """
        self.tps = tps
        self.tick = 1. / tps

        # time.clock is a low resolution timer on some systems, use time.time instead if it is
        self.get_time = time.clock if time.clock() - time.clock() != 0 else time.time

    def start(self):
        """start the clock

        You'll want to start handling events soon after you call this. It will expect update to be called soon after
        """
        self.time = self.get_time()

    def update(self, event):
        """called on an UPDATE event. should be the first handler to be called"""
        time_now = self.get_time()

        time_passed = time_now - self.time
        self.real_time = time_now

        if time_passed < self.tick:
            raise gunge.event.StopHandling()
