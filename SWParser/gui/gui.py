import sys
from PyQt4 import QtCore, QtGui
from MainWindow import Ui_MainWindow
import SWProxy
import threading
import logging

logger = logging.getLogger("SWProxy")

class ProxyThread(QtCore.QThread):
    def __init__(self, ip, port, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.ip = ip
        self.port = port

    def run(self):
        try:
            logger.info("Running Proxy server at %s on port %s" % (self.ip, self.port))
            p = SWProxy.HTTP(self.ip, self.port)
            p.run()
        except Exception as e:
            logger.info("Error running proxy server : %s" % e)
            print "Error running proxy server : %s" % e

class MainWindow(QtGui.QMainWindow):
    def __init__(self, ip, port=8080, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.ipAddress.setText(ip)
        self.ui.proxyPort.setValue(port)
        self.ui.startProxy.clicked.connect(self.startStopProxy)
        self.ui.actionQuit.triggered.connect(self.quit)
        self.ui.actionAbout.triggered.connect(self.about)
        self.ui.actionOpen_PCAP.triggered.connect(self.openPCAP)
        self.proxy = None

    def quit(self):
        if self.proxy:
            self.proxy.terminate()
            self.proxy = None
        self.close()

    def about(self):
        QtGui.QMessageBox.about(self, "About", "SWProxy: Summoners War Proxy Tool\nWritten by KaKaRoTo\n\nLicensed under LGPLv3 and available at : \n\thttps://github.com/kakaroto/SWParser\n")

    def openPCAP(self):
        pcap_file = QtGui.QFileDialog.getOpenFileName()
        SWProxy.parse_pcap(pcap_file)

    def log(self, str):
        self.ui.logWindow.addItem(str)

    def startStopProxy(self):
        self.ui.proxyPort.setReadOnly(True)
        if self.proxy:
            self.ui.startProxy.setText("Start Proxy Server")
            self.ui.startProxy.setEnabled(False)
            self.proxy.terminate()
        else:
            self.ui.startProxy.setText("Stop Proxy Server")
            self.proxy = ProxyThread(self.ui.ipAddress.text(), self.ui.proxyPort.value(), parent=self)
            self.proxy.finished.connect(self.proxyStopped)
            self.proxy.start()

    def proxyStopped(self):
        self.proxy = None
        self.ui.proxyPort.setReadOnly(False)
        self.ui.startProxy.setEnabled(True)


class GuiLogHandler(logging.Handler):
    def __init__(self, gui=None):
        logging.Handler.__init__(self)
        self.gui = gui

    def emit(self, record):
        msg = self.format(record)
        self.gui.log(msg)
