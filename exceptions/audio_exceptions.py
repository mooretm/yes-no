""" Custom exceptions for the audiomodel class.

    Written by: Travis M. Moore
    Last edited: July 18, 2023
"""

class InvalidAudioDevice(Exception):
    """ Invalid audio device """

    def __init__(self, device, *args):
        super().__init__(args)
        self.device = device


    def __str__(self):
        return f'Audio Exception: {self.device} is not a valid audio device ID!'


class InvalidRouting(Exception):
    """ Invalid channel routing """

    def __init__(self, channels, routing, *args):
        super().__init__(args)
        self.channels = channels
        self.routing = routing


    def __str__(self):
        return f'Audio Exception: Audio has {self.channels} channel(s), but routing of {self.routing}.'


class Clipping(Exception):
    """ Audio clipping has occurred """
