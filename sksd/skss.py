# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 09:02:00 2020

@author: hoeren

This is the Spyder Kernel Spinner Service proper.

It is no-arch, and the dependencies should support aarch64, Win, Linux, Darwin.

The service will be "wrapped" in a `daemon` per OS.

"""

import os
import sys
import platform
import shutil
import psutil
import configparser
import zeroconf
import time
import atexit
import signal
import socket
import ctypes
import codecs
import pprint
import ipaddress
import ifaddr

from zeroconf import IPVersion, ServiceInfo, Zeroconf
from constants import zeroconf_type, project_root
from constants import config_name, config_file, config_template

if not sys.version_info[0] == 3:
    raise Exception("not running on python3 !")


class SKSS:
    """Spyder Kernels Spinner Service."""

    verbose = True
    debug = True

    def __init__(self):
        # constants
        self.zeroconf_type = zeroconf_type
        self.config_name = config_name
        self.config_file = config_file
        self.config_template = config_template

        # os dependent stuff
        self.OS = platform.system()
        self.trace(f"Operating System = '{self.OS}'")
        if self.OS in ["Linux", "Darwin"]:
            self.config_path = os.path.join("/", "etc", config_file)
        elif self.OS == "Windows":
            self.config_path = os.path.join(r"C:\Users\Public", config_file)
        else:
            raise Exception(f"Unsupported OS : {self.OS}")
        self.trace(f"Configuration file = '{self.config_path}'")

        # configuration
        self.config = configparser.ConfigParser()

        # configuration (boolean states)
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
            #
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

        # configuration (define the default configuration)
        self.DEFAULT = {
            "enable": "True",
            "name": "",
            "guest_account": "",
            "guest_can_manage_environments": "False",
            "max_kernels": "AUTO",
            "exclude_environments" : "['base', '_*']"}
        self.config["DEFAULT"] = self.DEFAULT

        # configuration (generate if needed and read the configuration file)
        if not os.path.exists(self.config_path):
            self.trace(f"The Config file '{self.config_path}' does not exist.")
            if os.path.exists(os.path.dirname(self.config_path)):
                self.trace(f"Writing config file.")
                try:
                    self.write_default_config_file(self.config_path)
                except Exception as e:
                    self.trace(f"Failed writing config file ({e})")
                    sys.exit(1)
                else:
                    self.trace("Successfully writen the default config file.")
            else:
                self.trace(f"Also the directory '{os.path.dirname(self.config_path)}' doesn't exist.")
        self.trace("Rading config file.")
        self.config.read(self.config_path)
        self.trace(self.get_current_configuration())

        # configuration (post-processing)
        self.trace("Post processing config file.")
        for key in self.config["DEFAULT"]:
            if key in ['enable', 'guest_can_manage_environments']:
                value = str(self.config["DEFAULT"].getboolean(key))
                self.config.set("DEFAULT", key, value)
            if "\n" in self.config['DEFAULT'][key]:
                value = self.config['DEFAULT'][key].replace('\n', '|')
                self.config.set("DEFAULT", key, value)
            if key == "max_kernels":
                value = self.config['DEFAULT'][key]
                cores = psutil.cpu_count()
                if value.upper().startswith('AUTO'):
                    value = str(cores - 1)
                if 'CORES' in value:
                    value = value.replace('CORES', str(cores))
                value = str(int(eval(value)))
                self.config.set("DEFAULT", key, value)
        for section in self.config.sections():
            self.config.remove_section(section)
        self.config.set("DEFAULT", "hostname", socket.gethostname())
        self.trace(self.get_current_configuration())

        # verify minimal configuration
        if not self.config['DEFAULT'].getboolean('enable'):
            self.trace("Configuration file prevents the service from starting.")
            sys.exit(0)
        if self.config['DEFAULT']['name'] == "":
            self.trace("Configuration file holds no 'name'.")
            sys.exit(1)

        # zeroconf
        self.zeroconf = Zeroconf(ip_version=IPVersion.All)


        print(self.get_ip())


    def __del__(self):
        self.unpublish()

    def trace(self, message, level=None):
        """placeholder for the logging stuff."""
        print(message)

    def has_root_privileges():
        """Determine if we have root previleges"""

        if self.OS in ["Linux", "Darwin"]:
            test_file_name = "sks_test_file"
            test_file_dir = "/etc"
            test_file = os.path.join(test_file_dir, test_file_name)
            try:
                open(test_file, 'w').close()
            except Exception:
                if os.path.exists(test_file):
                    os.remove(test_file)
                return False
            else:
                if os.path.exists(test_file):
                    os.remove(test_file)
                return True
        elif self.OS == "Windows":
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            raise Exception(f"Unsupported OS : {OS}")

    def get_ip(self):
        ignore_list = ['lo', "lo0"]
        res = {}
        for iface in ifaddr.get_adapters():
            # ignore "lo" (the local loopback)
            if iface.ips and iface.name not in ignore_list:
                for addr in iface.ips:
                    if addr.is_IPv4:
                        res[iface.nice_name] = addr.ip
                        break
        if res.get("wlan"):
            return res.get("wlan")
        elif res.get("en0"):
            return res.get("en0")
        elif res.get("eth0"):
            return res.get("eth0")
        else:
            # We don't know which one. Return the first one.
            return list(res.values())[0]

    def write_default_config_file(self, path):
        """Write the default configuration file to path"""
        import jinja2

        file_loader = jinja2.FileSystemLoader(os.path.dirname(__file__))
        env = jinja2.Environment(loader=file_loader)

        template_file = os.path.join("sksd.jinja2")
        template = env.get_template(template_file)

        output = template.render(config=self.DEFAULT)
        with codecs.open(path, "w", "utf-8") as fd:
            fd.write(output)

    def get_current_configuration(self):
        """This method returns the current configuration as a single string"""
        retval = ""
        retval += "  [DEFAULT]\n"
        for key in self.config["DEFAULT"]:
            retval += f"    {key} = {self.config['DEFAULT'][key]}\n"

        for section in self.config.sections():
            retval += f"  [{section}]\n"
            for key in self.config[section]:
                retval += f"    {key} = {self.config[section][key]}\n"
        return retval

    def make_service_info():
        """This function creates a zeroconf.ServiceInfo object from 'self'."""
        retval = ServiceInfo(
            self.service_tag,
            f"{hostname}.{service}")
        return retval

    def publish(self):
        pass

    def unpublish(self):
        pass



    def run(self):
        """This is the service main loop"""


        # TODO: get a free port number !
        # publish
        # go in loop mode


if __name__ == "__main__":
    skss = SKSS()

