#!/usr/bin/env python

from SWParser.smon_decryptor import decrypt_request, decrypt_response
from yapsy.PluginManager import PluginManager
import json
import logging
import os
import proxy
import socket
import sys
import argparse

VERSION = "0.97"
GITHUB = 'https://github.com/kakaroto/SWParser'
logger = logging.getLogger(__name__)


def load_plugins():
    manager = PluginManager()
    manager.setPluginPlaces([os.path.join(os.getcwd(), "plugins/")])
    manager.collectPlugins()
    ret = manager.getAllPlugins()
    # logger.info('Loaded {} plugins'.format(len(ret)))
    return ret


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


class ProxyCallback(object):

    def __init__(self):
        self.host = None
        self.port = 0
        self.request = None

    def onRequest(self, proxy, host, port, request):
        self.host = host
        self.port = port

    def onResponse(self, proxy, response):
        pass 

    def onDone(self, proxy):
        pass


class SWProxyCallback(ProxyCallback):

    plugins = load_plugins()

    is_com2us_api = lambda self: all((
        self.host,
        self.host.startswith('summonerswar'),
        self.host.endswith('com2us.net'),
        self.request,
        self.request.url.path.startswith('/api/'),
    ))

    def onRequest(self, proxy, host, port, request):
        super(SWProxyCallback, self).onRequest(proxy, host, port, request)
        self.request = request  # store request for retrieval later

    def onResponse(self, proxy, response):
        
        try:
            if self.request and self.is_com2us_api():
                
                req_plain, req_json = self.parse_request(self.request)
                resp_plain, resp_json = self.parse_response(response)

                if 'command' not in resp_json:
                    return

                for plugin in SWProxyCallback.plugins:

                    try:
                        plugin.plugin_object.process_request(req_json, resp_json, SWProxyCallback.plugins)
                    except Exception as e:
                        logger.exception(
                            'Exception while executing plugin "{}": {}'.format(
                                plugin.plugin_object.__class__.__name__, e
                            )   
                        )

        except Exception as e:
            logger.debug('unknown exception: {}'.format(e))

    def parse_request(self, request):
        """ takes a request, returns the decrypted plain and json """
        plain = decrypt_request(request.body)
        return plain, json.loads(plain)

    def parse_response(self, response):
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


def start_proxy_server(args):

    authors_text = read_file_lines('AUTHORS')

    print "#"*40
    print "# SWParser v{} - Summoners War Proxy # ".format(VERSION)
    print "#"*40
    print "\tWritten by:\n\t\tKaKaRoTo\n"
    print "\tAuthors:"
    for author in authors_text:
        print "\t\t{}".format(author)

    print "\n\tPlugins:"
    for plugin in SWProxyCallback.plugins:
        print "\t\t{}".format(plugin.name)

    print "\nLicensed under LGPLv3 and available at: \n\t{}\n".format(GITHUB)

    level = "DEBUG" if args.debug else "ERROR"
    logging.basicConfig(level=level, format='%(levelname)s - %(message)s')


    my_ip = get_external_ip()

    try:
        print "Running Proxy server at {} on port {}".format(my_ip, args.port)
        p = HTTP(my_ip,  args.port)
        p.run()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='SWParser')
    parser.add_argument('-d', '--debug', action="store_true", default=False)
    parser.add_argument('-p', '--port', type=int, help='Port number', default=8080, nargs='+')
    args = parser.parse_args()
    start_proxy_server(args)
