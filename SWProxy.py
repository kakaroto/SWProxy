#!/usr/bin/env python

from SWParser.smon_decryptor import decrypt_request, decrypt_response
import json
import logging
import os
import proxy
from SWPlugin import SWPlugin
import socket
import sys
import argparse

VERSION = "0.97"
GITHUB = 'https://github.com/kakaroto/SWParser'
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
        plain = decrypt_request(request.body)
        return plain, json.loads(plain)

    def _parse_response(self, response):
        """ takes a response body, returns the decrypted plain and json """
        plain = decrypt_response(response.body)
        return plain, json.loads(plain)


def get_external_ip():
    # ref: http://stackoverflow.com/a/1267524
    try:
        sockets = [[(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]
        ips = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], sockets) if l]
        return ips[0][0]
    except KeyError:
        # fallback on error
        return socket.gethostbyname(socket.gethostname())
    

def read_file_lines(fpath):
    try:
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
            from PyQt4.QtGui import QApplication
        except ImportError:
            print "Failed to load GUI dependencies. Switching to CLI mode"
            options.no_gui = True

    if options.no_gui:
        logger.addHandler(logging.StreamHandler())
        start_proxy_server(options)
    else:
        app = QApplication(sys.argv)
        win = gui.MainWindow(get_external_ip(), options.port)
        logger.addHandler(gui.GuiLogHandler(win))
        win.show()
        sys.exit(app.exec_())
