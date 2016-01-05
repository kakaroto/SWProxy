#!/usr/bin/python

import logging
from SWParser import parse_pcap, parse_login_data, parse_visit_data
from SWParser.smon_decryptor import decrypt_request, decrypt_response
import json
import proxy
import socket
import sys

VERSION = "0.94"
logger = logging.getLogger(__name__)

my_ip = [[(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]][0]


class ProxyCallback(object):
    def __init__(self):
        self.host = None
        self.port = 0
        self.method = None
        self.request = None
        self.response = None

    def onRequest(self, proxy, host, port, request):
        self.host = host
        self.port = port
        self.request = request
        self.method = request.method
        if host.startswith("summonerswar") and \
           host.endswith("com2us.net") and \
           request.url.path.startswith("/api/"):
            try:
                req_plain = decrypt_request(request.body)
                req_json = json.loads(req_plain)
                print "Found Summoners War API request : %s" % req_json['command']
            except:
                pass

    def onResponse(self, proxy, response):
        self.response = response
        if self.host and self.host.startswith("summonerswar") and \
           self.host.endswith("com2us.net") and \
           self.request and self.request.url.path.startswith("/api/"):
            try:
                resp_plain = decrypt_response(response.body)
                resp_json = json.loads(resp_plain)
                if resp_json['command'] == 'HubUserLogin':
                    print "Monsters and Runes data generated"
                    parse_login_data(resp_json)
                elif resp_json['command'] == 'VisitFriend':
                    print "Visit Friend data generated"
                    parse_visit_data(resp_json)
                elif resp_json['command'] == 'GetUnitCollection':
                    collection = resp_json['collection']
                    print "Your collection has %d/%d monsters" % (sum([y['open'] for y in collection]), len(collection))

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
    print "\tWritten by KaKaRoTo\n\nLicensed under GPLv3 and available at : \n\thttps://github.com/kakaroto/SWParser\n"

    logging.basicConfig(level="ERROR", format='%(levelname)s - %(message)s')
    try:
        print "Running Proxy server at %s on port %s" % (my_ip, 8080)
        p = HTTP(my_ip, 8080)
        p.run()
    except KeyboardInterrupt:
        pass
