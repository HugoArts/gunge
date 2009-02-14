#! /usr/bin/env python

"""contains the display class which is responsible for the actual display surface"""

import pygame.display
import gunge.event

class Display(gunge.event.Handler):
    """represents the display surface, or the screen that is actually being shown"""
    #caption = property(pygame.display.get_caption, pygame.display.set_caption)

    def __init__(self, size, caption, background, flags=0):
        gunge.event.Handler.__init__(self)

        self.screen = pygame.display.set_mode(size, flags)
        self.rect = self.screen.get_rect()
        self.caption = caption
        self.background = background

    @gunge.event.bind(gunge.event.RENDER)
    def render(self, event):
       self.screen.blit(self.background, (0,0))

    @gunge.event.bind(gunge.event.BUFSWAP)
    def buffer_swap(self, event):
        pygame.display.flip()


def lerp(prev_val, new_val, interpolation):
    return prev_val + ((new_val - prev_val) * interpolation)
