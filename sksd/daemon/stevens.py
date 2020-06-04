# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 12:51:04 2020

@author: Tom Hören

    best would be maybe to follow PEP3143 ( https://www.python.org/dev/peps/pep-3143/ )
    for daemonizing, although that also follows Stevens... in any case python-daemon
    is the package we then want to use ( https://pagure.io/python-daemon/tree/master )
    but the package to be installed via the conda-forge channel has no aarch64 support
    ( https://github.com/conda-forge/python-daemon-feedstock ) another option would
    be to use https://daemoniker.readthedocs.io/en/latest/ but I don't know that
    package (yet), that's why I implement a well behaved daemon based on stevens myself 😇

    references :
        https://dpbl.wordpress.com/2017/02/12/a-tutorial-on-python-daemon/

"""

import sys
import os
import time
import atexit
import signal
import configparser
import platform

from configparser import NoOptionError

from abc import ABC, abstractmethod


if not sys.version_info[0] == 3:
    raise Exception("not running on python3 !")


class daemon_ABC(ABC):
    """A generic daemon abstract base class for python3 under Linux"""

    verbose = True

    def __init__(self, confdir):
        if not os.path.exists(confdir):
            raise Exception(f"'{confdir}' does not exist (or is not accessable)!")

        name = self.__class__.__name__
        if self.verbose:
            print(f"daemon name = '{name}'")
            if platform.system() != "Windows":
                print(f"euid = '{os.geteuid()}'")  # not for windows !
                print(f"uid = '{os.getuid()}'")  # not for windows !


        self.pid_file = os.path.join(confdir, f"{name}.pid")
        if self.verbose:
            print(f"pid-file = '{self.pid_file}'")
        # TODO: if the pid file exists, open it, look what process did write it, and
        # look if the process is running, if so, report and die, if not so, remove
        # the pid file and go on.
        if os.path.exists(self.pid_file):
            if self.verbose:
                printf(f"pid-file already exists, looking for process ...  ", end="")
            try:
                os.remove(self.pid_file)
            except Exception as e:
                if self.verbose:
                    print("Failed.")
                raise Exception(f"pid-file '{self.pid_file}' already exitst and can't be removed! ({e})")
            if self.verbose:
                print("Done.")

        self.config_file = os.path.join(confdir, f"{name}.conf")
        if self.verbose:
            print(f"config-file = '{self.config_file}'")
        if not os.path.exists(self.config_file):
            raise Exception(f"'{self.config_file}' does not exitst!")

        self.config = configparser.ConfigParser()
        self.DEFAULT = {
            'enable': False}
        self.config["DEFAULT"] = self.DEFAULT
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
        if self.verbose:
            print("Reading config file ... ", end="")
        self.config.read(self.config_file)
        if self.verbose:
            print("Done.")
        self._post_process_config_file()

    def __del__(self):
        if os.path.exists(self.pid_file):
            os.remove(self.pid_file)

    def _post_process_config_file(self):
        """Fix minor flaws in the configuration file, and complain about major ones."""

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






    def daemonize(self):
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)  # exit first parent
        except OSError as err:
            sys.stderr.write(f"fork #1 failed: {err}")
            sys.exit(1)

        # decouple from parent environment
        os.chdir('/')
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)  # exit from second parent
        except OSError as err:
            sys.stderr.write(f"fork #2 failed: {err}")
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(os.devnull, 'r')
        so = open(os.devnull, 'a+')
        se = open(os.devnull, 'a+')

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write the pid file
        pid = str(os.getpid())
        with open(self.pid_file, 'w+') as f:
            f.write(pid + '\n')

        # make very sure that the destructor is called when we die
        atexit.register(self.__del__)

    def start(self):
        """Start the daemon."""

        # Check for a pid_file to see if the daemon already runs
        try:
            with open(self.pid_file, 'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None

        if pid:
            message = "pid_file {0} already exist. " + \
                      "Daemon already running?\n"
            sys.stderr.write(message.format(self.pid_file))
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        self.run()

    def stop(self):
        """Stop the daemon."""

        # Get the pid from the pid_file
        try:
            with open(self.pid_file, 'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None

        if not pid:
            message = "pid_file {0} does not exist. " + \
                      "Daemon not running?\n"
            sys.stderr.write(message.format(self.pid_file))
            return  # not an error in a restart

        # Try killing the daemon process
        try:
            while True:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            e = str(err.args)
            if e.find("No such process") > 0:
                if os.path.exists(self.pid_file):
                    os.remove(self.pid_file)
            else:
                print(str(err.args))
                sys.exit(1)

    def restart(self):
        """Restart the daemon."""
        self.stop()
        self.start()

    @abstractmethod
    def run(self):
        """Deamon business logic comes here"""
        pass