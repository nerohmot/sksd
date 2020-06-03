# -*- coding: utf-8 -*-
"""
Created on Fri May 29 13:43:52 2020

@author: hoeren
"""

import os
import re
import time
import socket
import numpy as np
import qtawesome as qta

from PyQt5 import QtCore, QtWidgets, uic
from zeroconf import IPVersion, ServiceInfo, Zeroconf
from publish import find_free_port


class PublishKernelsWizard(QtWidgets.QDialog):
    """Wizard to publish Spyder-Kernels."""

    def __init__(self):
        super().__init__()

        my_ui = __file__.replace('.py', '.ui')
        if not os.path.exists(my_ui):
            raise Exception(f"can not find {my_ui}")
        uic.loadUi(my_ui, self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle(' '.join(re.findall('.[^A-Z]*', os.path.basename(__file__).replace('.py', ''))))

        self.zeroconf = Zeroconf()

        # self.spyderKernelHosts.blockSignals(True)
        # self.spyderKernelHosts.clear()
        # if host_list != []:
        #     self.spyderKernelHosts.addItems(host_list)
        #     self.spyderKernelHosts.setCurrentText(host_list[0])  # = localhost if available
        #     self.spyderKernelHosts.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        # self.spyderKernelHosts.setEnabled(True)
        # self.spyderKernelHosts.blockSignals(False)

        self.show()


    def get_configuration(self):
        """This methode grabs the configuration from the UI and returns it as a ServiceInfo object."""
        service = "_skd._tcp.local."

        if serviceName.text() == '':
            service_name = hostName.text()
        else:
            service_name = serviceName.text()

        if hostAddress.text() == '':
            ip_address = [socket.inet_aton("127.0.0.1")]
        else:
            ip_address = [socket.inet_aton(hostAddress.text())]

        if port.value == 0:
            ip_port = np.random.randint(1, 65535)
        else:
            ip_port = port.value

        if guestAccount == '':
            guest_account = True
        else:
            guest_account = False

        retval = ServiceInfo(
            service,
            f"{service_name}.{service}",
            addresses=ip_address,
            port=ip_port,
            server=hostName.text(),
            properties={
                "guest_account" : guest_account,


                },
            )
    return retval


if __name__ == '__main__':
    import sys
    import qdarkstyle



    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    connectionWizard = ConnectionWizard(spyderListener)
    sys.exit(app.exec_())
