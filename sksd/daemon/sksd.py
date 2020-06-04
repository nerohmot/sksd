# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 15:16:59 2020

@author: hoeren
"""

import os
import shutil
import configparser
import zeroconf

from daemon.stevens import daemon_ABC

mode = "development"


# idea : use Qt, this way we can use the 'timer' to wake up the deamon every
# 'TTL' seconds to re-publish.
# Also ... maybe go the 'asyncio' way ... is ideal for the (single) connections
# to a spyder instance ...

class sksd(daemon_ABC):

    def run(self):
        print("Hello")
        print("goodbye")
        self.stop()


if __name__ == "__main__":
    name = '.'.join(os.path.basename(__file__).split('.')[:-1])
    if mode.upper().startswith("DEV"):
        config_dir = os.path.dirname(__file__)
    else:
        config_dir = os.path.join(os.path.sep, "etc", name)

    daemon = sksd(config_dir)
