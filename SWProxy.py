#!/usr/bin/env python

import logging
from SWParser import parse_login_data, parse_visit_data
from SWParser.smon_decryptor import decrypt_request, decrypt_response
from yapsy.PluginManager import PluginManager
import json
import os
import proxy
import socket
import sys

VERSION = "0.97"
logger = logging.getLogger("SWProxy")


def initialize_yapsy_plugins():
    manager = PluginManager()
    manager.setPluginPlaces([os.getcwd() + os.sep + "plugins"])
    manager.collectPlugins()
    return manager.getAllPlugins()


class ProxyCallback(object):
    plugins = initialize_yapsy_plugins()

    def __init__(self):
        self.host = None
        self.port = 0
        self.request = None
        self.response = None

    def onRequest(self, proxy, host, port, request):
        self.host = host
        self.port = port
        self.request = request

    def onResponse(self, proxy, response):
        self.response = response
        if self.host and self.host.startswith("summonerswar") and \
           self.host.endswith("com2us.net") and \
           self.request and self.request.url.path.startswith("/api/"):
            try:
                req_plain = decrypt_request(self.request.body)
                req_json = json.loads(req_plain)
                resp_plain = decrypt_response(response.body)
                resp_json = json.loads(resp_plain)

                if 'command' not in resp_json:
                    return

                for plugin in ProxyCallback.plugins:
                    try:
                        plugin.plugin_object.process_request(req_json, resp_json, ProxyCallback.plugins)
                    except Exception as e:
                        logger.exception('Exception while executing plugin "%s": %s' \
                                         % (plugin.plugin_object.__class__.__name__, e))
                if resp_json['command'] == 'HubUserLogin' or resp_json['command'] == 'GuestLogin':
                    parse_login_data(resp_json, ProxyCallback.plugins)
                    logger.info("Monsters and Runes data generated")
                elif resp_json['command'] == 'VisitFriend':
                    parse_visit_data(resp_json, ProxyCallback.plugins)
                    logger.info("Visit Friend data generated")
                elif resp_json['command'] == 'GetUnitCollection':
                    collection = resp_json['collection']
                    logger.info("Your collection has %d/%d monsters" % (sum([y['open'] for y in collection]), len(collection)))
            except:
                pass
    def onDone(self, proxy):
        pass

class HTTP(proxy.TCP):
    """HTTP proxy server implementation.

    Spawns new process to proxy accepted client connection.
    """

    def handle(self, client):
        callback = ProxyCallback()
        proc = proxy.Proxy(client, callback)
        proc.daemon = True
        proc.start()
        logger.debug('Started process %r to handle connection %r' % (proc, client.conn))

if __name__ == "__main__":
    print "SWParser v%s - Summoners War Proxy" % VERSION
    print "\tWritten by KaKaRoTo\n\nLicensed under LGPLv3 and available at : \n\thttps://github.com/kakaroto/SWParser\n"

    logging.basicConfig(level="DEBUG", filename="proxy.log", format='%(levelname)s - %(message)s')
    logger.setLevel(logging.INFO)

    no_gui = False
    if len(sys.argv) > 1 and sys.argv[1] == '--no-gui':
        no_gui = True
        port = 8080 if len(sys.argv) < 3 else int(sys.argv[2])
    else:
        port = 8080 if len(sys.argv) < 2 else int(sys.argv[1])

    my_ip = [[(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]][0]

    if no_gui:
        logger.addHandler(logging.StreamHandler())
        try:
            print "Running Proxy server at %s on port %s" % (my_ip, port)
            p = HTTP(my_ip,  port)
            p.run()
        except KeyboardInterrupt:
            pass
    else:
        # Import here to avoid importing QT in CLI mode
        from SWParser.gui import gui
        from PyQt4.QtGui import QApplication

        app = QApplication(sys.argv)
        win = gui.MainWindow(my_ip, port)
        logger.addHandler(gui.GuiLogHandler(win))
        win.show()
        sys.exit(app.exec_())
