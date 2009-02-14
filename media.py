#! /usr/bin/env python

"""media.py - classes for loading media files

this file contains classes to load and store media files.
The files can be loaded lazily, or at any time you see fit.
"""

import os, pygame

class ResourceLoader(dict):
    """ResourceLoader - base class for loading resources
    files are stored in a dictionary with the filename as key. by default, files are
    loaded the moment you try to access them, but you can also pre-load files.

    since all basic functionality is in ResourceLoader, derived classes only have to implement the load method.
    If they want to do some postprocessing on the resources, you can implement a locate method which calls
    the base locate method to retrieve the file, and then does the processing.
    """

    def __init__(self, paths, set_as_global=True):
        """ResourceLoader(paths) -> ResourceLoader
        paths is a tuple of directories to search through
        """
        common.Singleton.__init__(self, set_as_global)
        self.paths = list(paths) if isinstance(paths, (list, tuple, set)) else [paths]

    def __missing__(self, key):
        """indexing operation -> [resource]
        Key is usually the filename of something. What is returned depends on the filetype being loaded
        """
        dict.__setitem__(self, key, self.locate(key))
        return dict.__getitem__(self, key)

    def __setitem__(self, key, value):
        """raise a RuntimeError.
        it is not legal to set items in the dictionary to a different value.
        It is essentially an immutable dictionary, since its contents depend on outside resources.
        """
        raise RuntimeError("The ResourceLoader class does not support assignment")

    def locate(self, filename):
        """locate(filename) -> [resource]
        locate finds a file, then uses the load function to load it.
        It raises a FileError if the file is not found in any path. If you want to do any post-processing
        on a loaded resource, override this method in your class, call the base class method, then process away
        """
        resource = None
        for path in self.paths:
            try:
                resource = self.load(os.path.join(path, filename))
            except IOError, pygame.error:
                #error, probably file not found. Try the next path
                continue
            else:
                #no error? then we can quit and return the found resource
                break
        else:
            #This means we didn't break out of the loop, and found nothing but errors
            raise IOError("could not open file %s (paths: %s)" % (filename, self.paths))
        return resource

    def load(self, filename):
        """load(self, filename) -> None
        this method is the one to override if you want to derive from this class.
        it is used by the base class to load all files.
        """
        return open(filename)

    def preload(self, *filenames):
        """preload(self, *filenames) -> None
        this can be used to preload some files before you actually need them.
        This can be usefull to prevent latencies during a game. Since you don't
        need the resources just yet, nothing is returned.
        """
        for filename in filenames:
            dict.__setitem__(self, filename, self.locate(filename))


class ImageLoader(ResourceLoader):
    """ImageLoader - used to load and access images."""

    def load(self, filename):
        """load(filename, colorkey=None) -> pygame.Surface
        note that colorkey must be either None or an RGB-tuple.
        """
        return pygame.image.load(filename)

    def locate(self, filename, alpha=False):
        """locate(filename, alpha=False) -> pygame.Surface
        uses the base class locate to load the file, then performs a little post-processing.
        If you need per-pixel alpha, you can't use indexing notation and you'll have to preload
        with that option explicitly
        """
        image = ResourceLoader.locate(self, filename)
        if alpha:
            image.convert_alpha()
        else:
            image.convert()
        return image

    def preload(self, *tuples):
        """preload(self, tuples) -> None
        preloads a list of files. The arguments are all tuples with the filename
        first, and an alpha argument second which specifies wether you want per-pixel alpha.
        """
        for args in tuples:
            self.resources[filename] = self.locate(*args)


class SoundLoader(ResourceLoader):
    """SoundLoader - used to load, access and play sounds
    note that the class is not te be used for music. The pygame.mixer.music
    module does a good enough job, and can use streaming (Bonus!!).
    """
    def load(self, filename):
        """load(filename) -> pygame.mixer.Sound"""
        return pygame.mixer.Sound(filename)

    def locate(self, filename):
        """locate(filename) -> pygame.mixer.Sound
        if the pygame.mixer module is not loaded, a dummy soundclass is returned
        which does nothing.
        """
        if not pygame.mixer:
            return NoSound()
        return ResourceLoader.locate(self, filename)

    def play(self, filename, loops=0, maxtime=0):
        """play(self, file) -> pygame.mixer.Channel
        plays the file, loading it if needed
        """
        return self[filename].play(loops, maxtime)


class NoSound:
    """NoSound - used in case there is no sound available, with a dummy play method"""
    def play(self):
        """play() -> None"""
        pass
