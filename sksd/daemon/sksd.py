# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 15:16:59 2020

@author: hoeren
"""

import os
import shutil
import configparser
import zeroconf
import pprint

from daemon.stevens import daemon_ABC

mode = "development"


# idea : use Qt, this way we can use the 'timer' to wake up the deamon every
# 'TTL' seconds to re-publish.
# Also ... maybe go the 'asyncio' way ... is ideal for the (single) connections
# to a spyder instance ...

class sksd(daemon_ABC):

    verbose = True
    # enabled = True

    def pre_run(self):
        """Load the configuration file."""

        self.config_file = os.path.join(self.config_dir, f"{self.name}.conf")
        if self.verbose:
            print(f"config-file = '{self.config_file}'")

        if not os.path.exists(self.config_file):
            raise Exception(f"'{self.config_file}' does not exitst!")

        self.config = configparser.ConfigParser()

    # define boolean states
        self.config.BOOLEAN_STATES = {
            "1": True,
            "on": True,
            "On": True,
            "ON": True,
            "true": True,
            "True": True,
            "TRUE": True,
            "yes": True,
            "YES": True,
            "Yes": True,
            "y": True,
            "Y": True,
            "sure": True,
            "Sure": True,
            "SURE": True,
            "yup" : True,
            "Yup" : True,
            "YUP" : True,

            "0": False,
            "off": False,
            "Off": False,
            "OFF": False,
            "false": False,
            "False": False,
            "FALSE": False,
            "no": False,
            "No": False,
            "NO": False,
            "n": False,
            "N": False,
            "nope": False,
            "Nope": False,
            "NOPE": False}

    # define the default configuration.
        self.DEFAULT = {
            "enable": "False",
            "name": "",
            "guest_account": "",
            "guest_can_manage_environments": "True",
            "max_kernels": "AUTO",
            "exclude_environments" = "['base', '_*']"}
        self.config["DEFAULT"] = self.DEFAULT

    # read configuration
        if self.verbose:
            print("Reading config file ... ", end="")
        self.config.read(self.config_file)
        if self.verbose:
            print("Done.")

    # post-process the read configuration file.
        if self.verbose:
            print("Post-processing the config file ... ", end="")
        self.configuration = {
            }
        if self.verbose:
            print("Done.")
            cfg = pprint.PrettyPrinter(indent=4)




        if self.verbose:
            print("post processing the configuration file ...")

        # option : DEFAULT/enable
        try:
            self.config.getboolean("DEFAULT", "enable")
        except ValueError:
            raise Exception(f"Can not interprete '{self.config['DEFAULT']['enable']}' for the 'DEFAULT/enable' option")
        else:
            if self.verbose:
                print(f"   DEFAULT/enable = {self.config.getboolean('DEFAULT', 'enable')}")

        # option : DEFAULT/




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
