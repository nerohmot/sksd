#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 27 18:41:55 2020

@author: hoeren
"""

import os
import re
import time

import qtawesome as qta
from PyQt5 import QtCore, QtWidgets, uic


class ConnectionWizard(QtWidgets.QDialog):
    """Wizard to connect to a Spyder-Kernel."""

    def __init__(self, listener):
        super().__init__()

        self.listener = listener

        my_ui = __file__.replace('.py', '.ui')
        if not os.path.exists(my_ui):
            raise Exception(f"can not find {my_ui}")
        uic.loadUi(my_ui, self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle(' '.join(re.findall('.[^A-Z]*', os.path.basename(__file__).replace('.py', ''))))

        self.manageCondaEnvironment.setIcon(qta.icon('mdi.wrench', color='orange'))
        self.cancelButton.clicked.connect(self.CancelButtonPressed)
        self.connectButton.clicked.connect(self.ConnectButtonPressed)

        host_list = list(self.listener.get_hosts())
        local_host_list = sorted([host for host in host_list if 'localhost' in host], key=len)
        non_local_host_list = [host for host in host_list if 'localhost' not in host]
        host_list = local_host_list + non_local_host_list
        self.spyderKernelHosts.blockSignals(True)
        self.spyderKernelHosts.clear()
        if host_list != []:
            self.spyderKernelHosts.addItems(host_list)
            self.spyderKernelHosts.setCurrentText(host_list[0])  # = localhost if available
            self.spyderKernelHosts.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.spyderKernelHosts.setEnabled(True)
        self.spyderKernelHosts.blockSignals(False)

        self.show()

    def update_conda_environments(self):
        pass

    def CancelButtonPressed(self):
        self.reject()

    def ConnectButtonPressed(self):
        self.accept()


if __name__ == '__main__':
    import sys
    import qdarkstyle

    from zeroconf import Zeroconf
    from zeroconf import ServiceBrowser
    from discover import SpyderListener

    zeroconf = Zeroconf()
    spyderListener = SpyderListener()
    browser = ServiceBrowser(zeroconf, "_skd._tcp.local.", spyderListener)

    time.sleep(3)  # give the browser some time to discover

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    connectionWizard = ConnectionWizard(spyderListener)
    sys.exit(app.exec_())
