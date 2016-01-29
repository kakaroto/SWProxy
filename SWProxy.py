#!/usr/bin/python

import logging
from SWParser import parse_login_data, parse_visit_data, rune_set_id, rune_effect, monster_name
from SWParser.smon_decryptor import decrypt_request, decrypt_response
import json
import proxy
import socket
import sys
import time, datetime
import threading
import os

VERSION = "0.96"
logger = logging.getLogger(__name__)

def runeClass(n):
    if n == 0:
        return 'Common'
    if n == 1:
        return 'Magic'
    if n == 2:
        return 'Rare'
    if n == 3:
        return 'Hero'
    if n == 4:
        return 'Legendary'

class ProxyCallback(object):
    def __init__(self):
        self.host = None
        self.port = 0
        self.request = None
        self.response = None

    def onRequest(self, proxy, host, port, request):
        self.host = host
        self.port = port
        self.request = request

    def getItemName(self, crate):
        if 'random_scroll' in crate and crate['random_scroll']['item_master_id'] == 1:
            return "Unknown Scroll x%s" % crate['random_scroll']['item_quantity']
        if 'random_scroll' in crate and crate['random_scroll']['item_master_id'] == 8:
            return "Summoning Stones x%s" % crate['random_scroll']['item_quantity']
        if 'random_scroll' in crate and crate['random_scroll']['item_master_id'] == 2:
            return "Mystical Scroll"
        if 'costume_point' in crate:
            return "Shapeshift Stone x%s" % crate['costume_point']
        if 'unit_info' in crate:
            return '%s %s*' % (monster_name(crate['unit_info']['unit_master_id']), crate['unit_info']['class'])
        return 'Unknown drop'

    def get_dungeon_name(self, id):
        if id == 8001:
            return 'Giant''s Keep'
        if id == 9001:
            return 'Dragon''s Lair'
        if id == 6001:
            return 'Necropolis'
        return str(id)

    def get_scenario_name(self, id):
        if id == 1:
            return 'Garen Forest'
        if id == 2:
            return 'Mt. Siz'
        if id == 3:
            return 'Kabir Ruins'
        if id == 4:
            return 'Mt. White Ragon'
        if id == 5:
            return 'Telain Forest'
        if id == 6:
            return 'Hydeni Ruins'
        if id == 7:
            return 'Tamor Desert'
        if id == 8:
            return 'Vrofagus Ruins'
        if id == 9:
            return 'Faimon Volcano'
        if id == 10:
            return 'Aiden Forest'
        if id == 11:
            return 'Ferun Castle'
        if id == 12:
            return 'Mt Runar'
        if id == 13:
            return 'Chiruka Remains'
        return 'Unknown'

    def get_difficulty(self, id):
        if id == 1:
            return 'normal'
        if id == 2:
            return 'hard'
        return 'hell'

    def log_event(self, req_json, resp_json):
        command = req_json['command']
        if command == 'BattleScenarioResult' or command == 'BattleDungeonResult':
            return self.log_end_battle(req_json, resp_json)

        if command == 'BattleDungeonStart' or command == 'BattleScenarioStart':
            self.config['start'] = int(time.time())
        if command == 'BattleDungeonStart':
            self.config['stage'] = '%s b%s' % (self.get_dungeon_name(req_json['dungeon_id']), req_json['stage_id'])
        if command == 'BattleScenarioStart':
            self.config['stage'] = '%s %s - %s' % (self.get_scenario_name(req_json['region_id']),
                                                   self.get_difficulty(req_json['difficulty']), req_json['stage_no'])

    def log_end_battle(self, req_json, resp_json):
        if not self.config["log_runs"]:
            return

        if resp_json["win_lose"] == 1:
            win_lost = "Win"
        else:
            win_lost = "Lost"

        if 'start' in self.config:
            delta = int(time.time()) - self.config['start']
            m = divmod(delta,60)
            s = m[1]  # seconds
            elapsed_time = '%s:%s' % (m[0],s)
        else:
            elapsed_time = 'N/A'

        reward = resp_json['reward']
        log_entry = "%s,%s,%s,%s,%s,%s,%s," % (time.strftime("%Y-%m-%d %H:%M"), self.config['stage'], win_lost,
                                               elapsed_time, reward['mana'], reward['crystal'], reward['energy'])

        if 'rune' in reward['crate']:
            rune = reward['crate']['rune']
            runeSet = rune_set_id(rune['set_id'])
            slot = rune['slot_no']
            grade = rune['class']
            rank = runeClass(len(rune['sec_eff']))

            log_entry += "rune,%s*,%s,%s,%s,%s,%s,%s" % (grade,  rune['sell_value'], runeSet, slot, rank,rune_effect(rune['pri_eff']),
                rune_effect(rune['prefix_eff']))

            for se in rune['sec_eff']:
                log_entry += ",%s" % rune_effect(se)
        else:
            other_item = self.getItemName(reward['crate'])
            log_entry += other_item

        filename = self.config['log_filename']
        if not os.path.exists(filename):
            log_entry = 'date, dungeon, result, clear time, mana, crystal, energy, drop, rune grade, sell value, rune set,' \
                    + 'slot, rune rarity, main stat, prefix stat, secondary stat 1, secondary stat 2, secondary stat 3,' \
                    + 'secondary stat 4\n' \
                + log_entry

        with open(filename, "a") as fr:
            fr.write(log_entry)
            fr.write('\n')
        return

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

                if self.config['log_runs']:
                    t = threading.Thread(target=self.log_event, args = (req_json,resp_json))
                    t.daemon = True
                    t.start()

                print "Found Summoners War API request : %s" % req_json['command']
                if resp_json['command'] == 'HubUserLogin' or resp_json['command'] == 'GuestLogin':
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
    config = None
    """HTTP proxy server implementation.

    Spawns new process to proxy accepted client connection.
    """
    def handle(self, client):
        callback = ProxyCallback()
        callback.config = config
        proc = proxy.Proxy(client, callback)
        proc.daemon = True
        proc.start()
        logger.debug('Started process %r to handle connection %r' % (proc, client.conn))

if __name__ == "__main__":
    print "SWParser v%s - Summoners War Proxy" % VERSION
    print "\tWritten by KaKaRoTo\n\nLicensed under GPLv3 and available at : \n\thttps://github.com/kakaroto/SWParser\n"

    logging.basicConfig(level="ERROR", format='%(levelname)s - %(message)s')
    port = 8080 if len(sys.argv) < 2 else int(sys.argv[1])
    my_ip = [[(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]][0]

    fileReader = open('swproxy.config')
    jsonText = fileReader.read()
    config = json.loads(jsonText)
    config["refills"] = 0
    config["runs"] = 0

    try:
        print "Running Proxy server at %s on port %s" % (my_ip, port)
        p = HTTP(my_ip,  port)
        p.run()
    except KeyboardInterrupt:
        pass
