# -*- coding: utf-8 -*-
"""
Created on Tue May 26 18:24:07 2020

@author: hoeren
"""

import time


class publish_spyder_kernels_daemon:
    def __init__(self, interval):
        print("__init__")
        self.interval = interval
        self.run()

    def run(self):
        while True:
            print("heartbeat ...")
            time.sleep(self.interval)

    def __del__(self):
        print("un-publish ...")


if __name__ == "__main__":
    import sched

    publisher = None

    def stop():
        del publisher

    print("1")
    schedule = sched.scheduler()
    schedule.enter(10, 1, stop)
    schedule.run()
    print("2")

    publisher = publish_spyder_kernels_daemon(1)
    print("3")
