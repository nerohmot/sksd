#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 26 23:27:34 2020

@author: tom
"""

from zeroconf import ServiceBrowser, Zeroconf


class SpyderListener:
    """This is a listener implemented as according to
    https://github.com/jstasiak/python-zeroconf/blob/master/zeroconf/__init__.py#L1448
    """

    def __init__(self):
        self.verbose = False
        self.hosts = {}

    def remove_service(self, zeroconf, type, name):
        host = name.replace(type, '')[:-1]
        del self.hosts[host]
        if self.verbose:
            print(f"Host '{host}' removed.")

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        host = name.replace(type, '')[:-1]
        self.hosts[host] = info
        if self.verbose:
            print(f"Host '{host}' added.")

    def update_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        host = name.replace(type, '')[:-1]
        self.hosts[host] = info
        if self.verbose:
            print(f"Host '{host}' updated.")

    def get_hosts(self):
        """Return a dictionary with the host name as key, and the info associated with it as value.

        It is **not** simply a copy of self.hosts, we need to replace the local host with 'localhost' (and the interface)
        """
        import psutil
        import socket

        retval = {}

        my_addresses = {}
        my_interfaces = psutil.net_if_addrs()
        for interface in my_interfaces:
            for nic in my_interfaces[interface]:
                if nic.family in [socket.AF_INET, socket.AF_INET6]:
                    my_addresses[nic.address] = interface
        for host in self.hosts:
            if len(self.hosts[host].addresses) != 1:
                raise Exception(f"Yup, not yet implemented ... {self.hosts[host]}")
            host_address = socket.inet_ntoa(self.hosts[host].addresses[0])
            if host_address in my_addresses:
                retval[f"localhost ({my_addresses[host_address]})"] = self.hosts[host]
            else:
                retval[host] = self.hosts[host]
        return retval


if __name__ == '__main__':
    zeroconf = Zeroconf()
    spyderListener = SpyderListener()
    try:
        while True:
            key = input(">>>")
            if key == '':
                break
            elif key in ['h', 'help']:
                print("help⏎ = this help")
                print("list⏎ = list spyder-hostsd's")
                print("⏎ = exit (note: it can take a while)")
            elif key in ['l', 'list']:
                detected_hosts = spyderListener.get_hosts()
                for host in detected_hosts:
                    print(f"{host} -> {detected_hosts[host]}")
    finally:
        zeroconf.close()
