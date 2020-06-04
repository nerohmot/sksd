# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 16:28:25 2020

@author: hoeren
"""

import os
import configparser

from pprint import PrettyPrinter


config_file = os.path.join(os.path.dirname(__file__), 'sksd.conf')

print(f"configuration file = '{config_file}'")

if not os.path.exists(config_file):
    print(f"'{config_file}' is not available")
else:
    configuration = configparser.ConfigParser()
    configuration.read(config_file)

    for section in configuration.sections():
        print(f"[{section}]")
        for option in configuration.options(section):
            value = configuration.get(section, option)
            print(f"   {option} : {value} ({type(value)})")
