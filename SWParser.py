#!/usr/bin/python

from SWParser import parse_pcap
import sys

VERSION = "0.93"

if __name__ == "__main__":
    print "SWParser v%s - Summoners War Data Parser and Extractor" % VERSION
    print "\tWritten by KaKaRoTo\n\nLicensed under GPLv3 and available at : \n\thttps://github.com/kakaroto/SWParser"

    if len(sys.argv) != 2:
        print "Usage :\n\t%s input.pcap" % (sys.argv[0])
        sys.exit(-1)
    parse_pcap(sys.argv[1])
