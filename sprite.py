#! /usr/bin/env python

"""base sprite class that works with the gunge clock, interpolating on renders between logic updates"""

import gunge.event
import pygame

class Sprite(gunge.event.Handler):
    """base sprite class. Has standard update and render methods, and mechanisms for interpolation between frames
    
    two important attributes are the rect and img attributes. These are where the image is blitted, and what image is blitted, respectively
    """

    def __init__(self, img, pos=(0,0), speed=(0,0)):
        """initialize a sprite object. The img argument must be a pygame.Surface object"""
        gunge.event.Handler.__init__(self)
        
        self.img = img
        self.rect = self.img.get_rect()
        self.rect.topleft = pos
        self.prev_rect = self.rect

        self.speed = list(speed)

    @gunge.event.bind(gunge.event.UPDATE)
    def update(self, event):
        self.prev_rect = self.rect
        self.rect = self.rect.move(*self.speed)

    @gunge.event.bind(gunge.event.RENDER)
    def render(self, event):
        x = lerp(self.prev_rect.left, self.rect.left, event.interpolate())
        y = lerp(self.prev_rect.top, self.rect.top, event.interpolate())

        event.display.screen.blit(self.img, (x, y))


def lerp(prev, new, interpolation):
    return prev + ((new - prev) * interpolation)
