#! /usr/bin/env python

"""Time related classes and functions, most importantly the Clock class, which can be used to decouple game logic and rendering"""

import gunge.event
import time

class Clock(gunge.event.Handler):
    """used to separate game logic updates from rendering, i.e. not update the game every frame.

    This is done by being the first object to register for the UPDATE event. If not enough time has passed yet
    for a game update to occur, StopHandling will be raised to cancel the update. If too much time has passed, the
    clock can reinsert another UPDATE event to update again without rendering.
    """

    def __init__(self, tps=25):
        """initialize the clock.

        tps = ticks per second, the amount of game updates allowed per second
        """
        gunge.event.Handler.__init__(self)
        self.tps = tps
        self.tick = 1. / tps
        self.started = False
        self.interpolate = 1.

        # time.clock is a low resolution timer on some systems, use time.time instead if it is
        self.get_time = time.clock if time.clock() - time.clock() != 0 else time.time

    def set_tps(self, tps):
        """set the amount of ticks per second of the clock. Can only be done before the clock starts"""
        if self.started:
            raise Exception("can not set tps if the clock already started")

        self.tps = tps
        self.tick = 1. / tps

    def start(self):
        """start the clock

        You'll want to start handling events soon after you call this. It will expect update to be called soon after
        If you wait with the mainloop too long, the game time will lag behind the real time too much, resulting in a flood of
        updates without any renders.
        """
        self.clock_time = self.get_time()
        self.since_last_render = self.get_time()

        self.time = 0
        self.game_time = 0
        self.game_latency = 0
        self.last_update = 0

        self.frame_count = 0
        self.frame_rate = 0
        self.average_framerate = 0

        self.started = True

    @gunge.event.bind(gunge.event.UPDATE)
    def update(self, event):
        """called on an UPDATE event. should be the first handler to be called.
        
        checks if doing an update now would bring game time closer to real time than it currently is. If so, the update is
        allowed. Otherwise, StopHandling is raised to stop the update from happening.
        """
        if not self.started:
            return

        time_now = self.get_time()
        time_passed = time_now - self.clock_time

        self.clock_time = time_now
        self.time += time_passed
        self.game_latency += time_passed

        if self.game_latency - self.tick > 0:
        #if abs(self.game_latency - self.tick) < abs(self.game_latency):
            #this means that updating now would bring the game time closer to real time
            self.game_latency -= self.tick
            self.game_time += self.tick
            return gunge.event.HANDLE_AGAIN
        else:
            #if that is not the case, we should not update
            self.interpolate = (self.time - self.game_time) / self.tick
            return gunge.event.HANDLE_STOP

    @gunge.event.bind(gunge.event.BUFSWAP)
    def bufswap(self, event):
        time_now = self.get_time()
        time_passed = time_now - self.since_last_render

        self.since_last_render = time_now
        self.frame_rate = 1. / time_passed

        self.average_framerate = (self.average_framerate * self.frame_count + self.frame_rate) / (self.frame_count + 1)
        self.frame_count += 1

        if self.frame_count > 100:
            self.frame_count = 0
