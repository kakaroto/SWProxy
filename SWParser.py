#!/usr/bin/python

from SWParser import parse_login_data, parse_visit_data
from SWParser.smon_decryptor import decrypt_request, decrypt_response
import sys
import dpkt
import json

VERSION = "0.94"

def parse_pcap(filename):
    streams = dict() # Connections with current buffer
    with open(filename, "rb") as f:
        pcap = dpkt.pcap.Reader(f)
        for ts, buf in pcap:
            eth = dpkt.ethernet.Ethernet(buf)
            if eth.type != dpkt.ethernet.ETH_TYPE_IP:
                continue
            ip = eth.data
            if not isinstance(ip, dpkt.ip.IP):
                try:
                    ip = dpkt.ip.IP(ip)
                except:
                    continue
            if ip.p != dpkt.ip.IP_PROTO_TCP:
                continue
            tcp = ip.data

            if not isinstance(tcp, dpkt.tcp.TCP):
                try:
                    tcp = dpkt.tcp.TCP(tcp)
                except:
                    continue

            tupl = (ip.src, ip.dst, tcp.sport, tcp.dport)
            if tupl in streams:
                streams[tupl] = streams[tupl] + tcp.data
            else:
                streams[tupl] = tcp.data

            if (tcp.flags & dpkt.tcp.TH_FIN) != 0 and \
               (tcp.dport == 80 or tcp.sport == 80) and \
               len(streams[tupl]) > 0:
                other_tupl = (ip.dst, ip.src, tcp.dport, tcp.sport)
                stream1 = streams[tupl]
                del streams[tupl]
                try:
                    stream2 = streams[other_tupl]
                    del streams[other_tupl]
                except:
                    stream2 = ""
                if tcp.dport == 80:
                    requests = stream1
                    responses = stream2
                else:
                    requests = stream2
                    responses = stream1

                while len(requests):
                    try:
                        request = dpkt.http.Request(requests)
                        #print request.method, request.uri
                    except:
                        request = ''
                        requests = ''
                    try:
                        response = dpkt.http.Response(responses)
                        #print response.status
                    except:
                        response = ''
                        responses = ''
                    requests = requests[len(request):]
                    responses = requests[len(responses):]

                    if len(request) > 0 and len(response) > 0 and \
                       request.method == 'POST' and \
                       request.uri == '/api/gateway.php' and \
                       response.status == '200':
                        try:
                            req_plain = decrypt_request(request.body)
                            resp_plain = decrypt_response(response.body)
                            req_json = json.loads(req_plain)
                            resp_json = json.loads(resp_plain)
                            if resp_json['command'] == 'HubUserLogin':
                                parse_login_data(resp_json)
                            elif resp_json['command'] == 'VisitFriend':
                                parse_visit_data(resp_json)
                        except:
                            import traceback
                            e = sys.exc_info()[0]
                            traceback.print_exc()

            elif (tcp.flags & dpkt.tcp.TH_FIN) != 0:
                del streams[tupl]

if __name__ == "__main__":
    print "SWParser v%s - Summoners War Data Parser and Extractor" % VERSION
    print "\tWritten by KaKaRoTo\n\nLicensed under GPLv3 and available at : \n\thttps://github.com/kakaroto/SWParser"

    if len(sys.argv) != 2:
        print "Usage :\n\t%s input.pcap" % (sys.argv[0])
        sys.exit(-1)
    parse_pcap(sys.argv[1])
