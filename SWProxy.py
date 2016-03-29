#!/usr/bin/env python

from SWParser.smon_decryptor import decrypt_request, decrypt_response
import json
import logging
import os
import proxy
from SWPlugin import *
import socket
import sys
import argparse
import struct

VERSION = "0.99"
GITHUB = 'https://github.com/kakaroto/SWProxy'
logger = logging.getLogger("SWProxy")

class HTTP(proxy.TCP):
    """
    HTTP proxy server implementation.
    Spawns new process to proxy accepted client connection.
    """

    def handle(self, client):
        callback = SWProxyCallback()
        proc = proxy.Proxy(client, callback)
        proc.daemon = True
        proc.start()
        logger.debug('Started process {} to handle connection {}'.format(proc, client.conn))


class SWProxyCallback(object):

    def __init__(self):
        self.request = None

    def onRequest(self, proxy, host, port, request):
        try:
            if host.startswith('summonerswar') and host.endswith('com2us.net') and request.url.path.startswith('/api/'):
                self.request = request  # if we care about this api call, store request for decryption later
        except AttributeError:
            pass

    def onResponse(self, proxy, response):

        if self.request is None:
            # we have not obtained a valid request yet
            return

        try:
            req_plain, req_json = self._parse_request(self.request)
            resp_plain, resp_json = self._parse_response(response)

            if 'command' not in resp_json:
                # we only want apis that are commands
                self.request = None
                return

            try:
                SWPlugin.call_plugins('process_request', (req_json, resp_json))
            except Exception as e:
                logger.exception('Exception while executing plugin : {}'.format(e))

        except Exception as e:
            logger.debug('unknown exception: {}'.format(e))

    def onDone(self, proxy):
        pass

    def _parse_request(self, request):
        """ takes a request, returns the decrypted plain and json """
        plain = decrypt_request(request.body, 2 if '_c2.php' in self.request.url.path else 1)
        return plain, json.loads(plain)

    def _parse_response(self, response):
        """ takes a response body, returns the decrypted plain and json """
        plain = decrypt_response(response.body, 2 if '_c2.php' in self.request.url.path else 1)
        return plain, json.loads(plain)


def get_external_ip():
    my_ip = [[(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]][0]
    return my_ip


def read_file_lines(fpath):
    try:
        fpath = resource_path(fpath)
        with open(fpath, 'r') as fh:
            return map(lambda x:x.strip(), fh.readlines())
    except Exception:
        logger.debug('Failed to read file at {}'.format(fpath))
        return ''


def get_usage_text():
    authors_text = read_file_lines('AUTHORS')

    lines = []
    lines.append("#"*40)
    lines.append("# SWParser v{} - Summoners War Proxy # ".format(VERSION))
    lines.append("#"*40)
    lines.append("\tWritten by:\n\t\tKaKaRoTo\n")
    lines.append("\tAuthors:")
    for author in authors_text:
        lines.append("\t\t{}".format(author))

    lines.append("\n\tPlugins:")
    for plugin in SWPlugin.plugins:
        lines.append("\t\t{}".format(plugin.name))

    lines.append("\nLicensed under LGPLv3 and available at: \n\t{}\n".format(GITHUB))
    return "\n".join(lines)


def resource_path(relative_path):
    # function to locate data files for pyinstaller single file executable
    # ref: http://stackoverflow.com/a/32048136
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)

    return os.path.join(os.path.abspath("."), relative_path)


def start_proxy_server(options):

    my_ip = get_external_ip()

    try:
        print "Running Proxy server at {} on port {}".format(my_ip, options.port)
        p = HTTP(my_ip,  options.port)
        p.run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='SWParser')
    parser.add_argument('-d', '--debug', action="store_true", default=False)
    parser.add_argument('-g', '--no-gui', action="store_true", default=False)
    parser.add_argument('-p', '--port', type=int, help='Port number', default=8080, nargs='+')
    options = parser.parse_args()

    # Set up logger
    level = "DEBUG" if options.debug else "INFO"
    logging.basicConfig(level=level, filename="proxy.log", format='%(asctime)s: %(name)s - %(levelname)s - %(message)s')
    logger.setLevel(logging.INFO)

    print get_usage_text()

    # attempt to load gui; fallback if import error
    if not options.no_gui:
        try:
            # Import here to avoid importing QT in CLI mode
            from SWParser.gui import gui
            from PyQt4.QtGui import QApplication, QIcon
            from PyQt4.QtCore import QSize
        except ImportError:
            print "Failed to load GUI dependencies. Switching to CLI mode"
            options.no_gui = True

    if options.no_gui:
        logger.addHandler(logging.StreamHandler())
        start_proxy_server(options)
    else:
        app = QApplication(sys.argv)
        # set the icon
        icons_path = os.path.join(os.getcwd(), resource_path("icons/"))
        app_icon = QIcon()
        app_icon.addFile(icons_path +'16x16.png', QSize(16,16))
        app_icon.addFile(icons_path + '24x24.png', QSize(24,24))
        app_icon.addFile(icons_path + '32x32.png', QSize(32,32))
        app_icon.addFile(icons_path + '48x48.png', QSize(48,48))
        app_icon.addFile(icons_path + '256x256.png', QSize(256,256))
        app.setWindowIcon(app_icon)
        win = gui.MainWindow(get_external_ip(), options.port)
        logger.addHandler(gui.GuiLogHandler(win))
        win.show()
        sys.exit(app.exec_())
