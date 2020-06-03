#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import time
import sched
from zeroconf import ServiceBrowser, ServiceStateChange, Zeroconf, ServiceInfo, ZeroconfServiceTypes


# https://stackoverflow.com/questions/1916017/simplest-way-to-publish-over-zeroconf-bonjour
# class WebSocketManager(service.Service, object):
#     ws_service_name = 'Verasonics WebSocket'
#     wsPort = None
#     wsInfo = None

#     def __init__(self, factory, portCallback):
#         factory.protocol = BroadcastServerProtocol
#         self.factory = factory
#         self.portCallback = portCallback
#         self.zeroconf = Zeroconf()

#     def privilegedStartService(self):
#         self.wsPort = reactor.listenTCP(0, self.factory)
#         port = self.wsPort.getHost().port

#         fqdn = socket.gethostname()
#         ip_addr = socket.gethostbyname(fqdn)
#         hostname = fqdn.split('.')[0]

#         wsDesc = {'service': 'Verasonics Frame', 'version': '1.0.0'}
#         self.wsInfo = ServiceInfo('_verasonics-ws._tcp.local.',
#                                   hostname + ' ' + self.ws_service_name + '._verasonics-ws._tcp.local.',
#                                   socket.inet_aton(ip_addr), port, 0, 0,
#                                   wsDesc, hostname + '.local.')
#         self.zeroconf.register_service(self.wsInfo)
#         self.portCallback(port)

#         return super(WebSocketManager, self).privilegedStartService()

#     def stopService(self):
#         self.zeroconf.unregister_service(self.wsInfo)

#         self.wsPort.stopListening()
#         return super(WebSocketManager , self).stopService()


# # https://stackoverflow.com/questions/474528/what-is-the-best-way-to-repeatedly-execute-a-function-every-x-seconds
# # https://docs.python.org/3/library/sched.html
# s = sched.scheduler(time.time, time.sleep)


# def do_something(sc):
#     print("Doing stuff...")
#     # do your stuff
#     s.enter(60, 1, do_something, (sc,))


# s.enter(60, 1, do_something, (s,))
# s.run()


# def announce_spyder_kernels_daemon():
#     from ZeroconfService import ZeroconfService
# import time

# service = ZeroconfService(name="Joe's awesome FTP server",
#                           port=3000,  stype="_ftp._tcp")
# service.publish()


def find_spyder_kernels_daemons(service='_skd._tcp.local.', timeout=10):
    """This function will collect all 'service'-es from the zeroconf network in 'timeout' seconds.

    Parameters
    ----------
    service : str
        The service to browse for, needs to end with either '_tcp.local.' or '_udp.local.'
        by default this would be 'skd._tpc.local.' for us (skd = Spyder Kernels Daemon)
    timeout : int, optional
        The number of seconds to wait for the discovery. (default=10)

    Returns
    -------
    a dictionary of dictionaries, key is a 'device' (in "ipaddress:port" format)
    and the value holds the dictionary with the details.

    example:
        {"10.92.48.5:4578" : {
             "name" : "APEX",
             "address" : "10.92.48.5",
             "port" : 4578,
             "weight" : "whatever",
             "priority" : "whatever",
             "server" : "whatever",
             "properties" : {whatever}}, <-- probably includes the 'pretty' name
         "10.92.48.100:5509" : {
             "name" : "Beowulf",
             "address" : "10.92.48.5",
             "port" : 4578,
             ...
        }
    """

    if not(service.endswith("._tcp.local.") or service.endswith("._udp.local.")):
        raise ValueError("service should end with '._tcp.local.' or '._udp.local.'")

    devices = {}

    # zeroconf will call this method when a device is found
    def on_service_state_change(zeroconf, service_type, name, state_change):
        info = zeroconf.get_service_info(service_type, name)
        if info is None:
            return

        device = ":".join([socket.inet_ntoa(info.address), str(info.port)])

        if state_change is ServiceStateChange.Added:
            devices[device] = {
                "name": name,
                "address": socket.inet_ntoa(info.address),
                "port": info.port,
                "weight": info.weight,
                "priority": info.priority,
                "server": info.server,
                "properties": info.properties}
        elif state_change is ServiceStateChange.Removed :
            if device in devices:
                del(devices[device])

    zeroconf = Zeroconf()
    browser = ServiceBrowser(zeroconf, service, handlers=[on_service_state_change])
    time.sleep(timeout)
    zeroconf.close()
    return devices


if __name__ == "__main__":
    devices = find_spyder_kernels_daemons()
    for device in devices:
        print(f"{device} : {devices[device]}")
