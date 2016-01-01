#!/usr/bin/python

from SWParser import parse_pcap, add_monster
import sys

if __name__ == "__main__":
    if len(sys.argv) == 3:
        add_monster.add_monster(sys.argv[1], sys.argv[2])
        sys.exit(0)
    if len(sys.argv) != 2:
        print "Usage :\n\t%s input.pcap" % (sys.argv[0])
        sys.exit(-1)
    parse_pcap(sys.argv[1])
