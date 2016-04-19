#!/usr/bin/env python

import csv
import json
import cStringIO
import sys
import struct
import numbers
import os
import codecs
from SWPlugin import SWPlugin
from collections import OrderedDict
from smon_decryptor import decrypt_request, decrypt_response
from monsters import monsters_name_map

# ref: http://stackoverflow.com/a/5838817/1020222
class DictUnicodeWriter(object):
    def __init__(self, f, fieldnames, dialect=csv.excel, encoding="utf-8", newfile=True, **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.DictWriter(self.queue, fieldnames, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()
        if newfile:
            self.writebom()

    def writerow(self, D):
        self.writer.writerow({k:unicode(v).encode("utf-8") for k, v in D.items()})
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for D in rows:
            self.writerow(D)

    def writeheader(self):
        self.writer.writeheader()

    def writebom(self):
        """Write BOM, so excel can identify this as UTF8"""
        self.stream.write(u'\ufeff'.encode('utf8'))


def monster_name(uid, default_unknown="???", full=True):
    uid = str(uid)
    name_map = monsters_name_map

    if uid in name_map and len(name_map[uid]) > 0:
        return name_map[uid]
    else:
        if uid[0:3] in name_map and len(name_map[uid[0:3]]) > 0:
            attribute = int(uid[-1])
            awakened = int(uid[-2])
            if full:
                return "%s%s (%s)" % ("AWAKENED " if awakened else "", name_map[uid[0:3]], monster_attribute(attribute))
            elif not awakened:
                return name_map[uid[0:3]]
        return default_unknown

def monster_attribute(attribute):
    name_map = {
        1: "Water",
        2: "Fire",
        3: "Wind",
        4: "Light",
        5: "Dark"
    }

    if attribute in name_map:
        return name_map[attribute]
    else:
        return attribute


def rune_effect_type(id, mode=0):
    """mode 0 = rune optimizer, mode 1 = csv export"""

    if mode != 0 and mode != 1:
        raise ValueError('Should be 0 (optimizer) or 1 (csv)')

    effect_type_map = {
        0: ("",""),
        1: ("HP flat", "HP +%s"),
        2: ("HP%", "HP %s%%"),
        3: ("ATK flat", "ATK +%s"),
        4: ("ATK%", "ATK %s%%"),
        5: ("DEF flat", "DEF +%s"),
        6: ("DEF%", "DEF %s%%"),
        # 7: "UNKNOWN",  # ?
        8: ("SPD", "SPD +%s"),
        9: ("CRate", "CRI Rate %s%%"),
        10: ("CDmg", "CRI Dmg %s%%"),
        11: ("RES", "Resistance %s%%"),
        12: ("ACC", "Accuracy %s%%")
    }

    return effect_type_map[id][mode] if id in effect_type_map else "UNKNOWN"


def rune_effect(eff):
    typ = eff[0]
    value = eff[1]
    flats = [1,3,5,8]
    if len(eff) > 3:
        if eff[3] != 0:
            if typ in flats:
                value = "%s -> +%s" % (value, str(int(value) + int(eff[3])))
            else:
                value = "%s%% -> %s" % (value, str(int(value) + int(eff[3])))

    if typ == 0:
        ret = ""
    elif typ == 7 or typ > 12:
        ret = "UNK %s %s" % (typ, value)
    else:
        ret = rune_effect_type(typ,1) % value

    if len(eff) > 2:
        if eff[2] != 0:
            ret = "%s (Converted)" % ret
    return ret

def rune_set_id(id):
    name_map = {
        1: "Energy",
        2: "Guard",
        3: "Swift",
        4: "Blade",
        5: "Rage",
        6: "Focus",
        7: "Endure",
        8: "Fatal",
        10: "Despair",
        11: "Vampire",
        13: "Violent",
        14: "Nemesis",
        15: "Will",
        16: "Shield",
        17: "Revenge",
        18: "Destroy",
    }

    if id in name_map:
        return name_map[id]
    else:
        return "???"

def map_craft(craft, craft_id):
    type_str = str(craft['craft_type_id'])
    return  {
        'id': craft_id,
        'item_id': craft['craft_item_id'],
        'type': 'E' if craft['craft_type'] == 1 else 'G',
        'set':  rune_set_id(int(type_str[:-4])),
        'stat': rune_effect_type(int(type_str[-4:-2])),
        'grade': int(type_str[-1:])
    }

def map_rune(rune, rune_id, monster_id=0, monster_uid=0):
    cvs_map ={
        'slot': rune['slot_no'],
        'rune_set': rune_set_id(rune['set_id']),
        'rune_grade': rune['class'],
        'rune_level':  rune['upgrade_curr'],
        'pri_eff': rune_effect(rune['pri_eff']),
        'pre_eff': rune_effect(rune['prefix_eff'])
    }

    if rune_id != None:
        cvs_map.update({
            'sell_price': rune['sell_value'],
            'rune_id': rune_id,
            'monster_id': '%s (%s)' % (monster_id, monster_name(monster_uid)) if monster_id != 0 else '0',
        })

    for i in range(0, len(rune['sec_eff'])):
        cvs_map['sub' + str(i + 1)] = rune_effect(rune['sec_eff'][i])

    subs = {
        'ATK flat': '-',
        'ATK%': '-',
        'HP flat': '-',
        'HP%': '-',
        'DEF flat': '-',
        'DEF%': '-',
        'RES': '-',
        'ACC': '-',
        'SPD': '-',
        'CDmg': '-',
        'CRate': '-',
    }

    for sec_eff in rune['sec_eff']:
        subs[rune_effect_type(sec_eff[0])] = sec_eff[1] + (sec_eff[3] if len(sec_eff) > 2 else 0)

    optimizer_map = {"id": rune_id,
            "unique_id": rune['rune_id'],
            "monster": monster_id,
            "monster_n":monster_name(monster_uid, "Unknown name"),
            "set": rune_set_id(rune['set_id']),
            "slot": rune['slot_no'],
            "grade": rune['class'],
            "level": rune['upgrade_curr'],
            "m_t": rune_effect_type(rune['pri_eff'][0]),
            "m_v": rune['pri_eff'][1],
            "i_t": rune_effect_type(rune['prefix_eff'][0]),
            "i_v": rune['prefix_eff'][1],
            "locked":0,
            "sub_res": subs['RES'],
            "sub_cdmg": subs['CDmg'],
            "sub_atkf": subs['ATK flat'],
            "sub_acc": subs['ACC'],
            "sub_atkp": subs['ATK%'],
            "sub_defp": subs['DEF%'],
            "sub_deff": subs['DEF flat'],
            "sub_hpp": subs['HP%'],
            "sub_hpf": subs['HP flat'],
            "sub_spd": subs['SPD'],
            "sub_crate": subs['CRate']}

    for sub in range(0,4):
        optimizer_map['s%s_t' % (sub + 1)] = rune_effect_type(rune['sec_eff'][sub][0]) if len(rune['sec_eff']) >= sub + 1 else ""
        optimizer_map['s%s_v' % (sub + 1)] = rune['sec_eff'][sub][1] +\
                                             (rune['sec_eff'][sub][3] if len(rune['sec_eff'][sub]) > 2 else 0) \
            if len(rune['sec_eff']) >= sub + 1 else 0
        optimizer_map['s%s_data' % (sub + 1)] = {"enchanted":  rune['sec_eff'][sub][2] == 1,
                                           "gvalue": rune['sec_eff'][sub][3]} \
            if len(rune['sec_eff']) >= sub + 1 and len(rune['sec_eff'][sub]) > 2 else {}
    return optimizer_map, cvs_map

def map_monster(monster, monster_id_mapping, storage_id, wizard_name=None):
    csv_map = {
        'name': monster_name(monster['unit_master_id']),
        'level': monster['unit_level'],
        'grade': monster['class'],
        'attribute': monster_attribute(monster['attribute']),
        'in_storage': "Yes" if monster['building_id'] == storage_id else "No",
        'hp': int(monster['con']) * 15,
        'atk': monster['atk'],
        'def': monster['def'],
        'spd': monster['spd'],
        'crate': monster['critical_rate'],
        'cdmg': monster['critical_damage'],
        'res': monster['resist'],
        'acc': monster['accuracy']
    }

    if wizard_name is None:
        csv_map['id'] = monster_id_mapping[monster['unit_id']]
    else:
        csv_map.update({'wizard_name' : wizard_name}),

    if monster_id_mapping:
        optimizer_monster = {"id": monster_id_mapping[monster['unit_id']],
                             "name":"%s%s" % (monster_name(monster['unit_master_id'], "Unknown name"),
                                              " (In Storage)" if monster['building_id'] == storage_id else ""),
                             "level": monster['unit_level'],
                             "unit_id": monster['unit_id'],
                             "stars": monster['class'],
                             "attribute": monster_attribute(monster['attribute']),
                             "b_hp": int(monster['con']) * 15,
                             "b_atk": monster['atk'],
                             "b_def": monster['def'],
                             "b_spd": monster['spd'],
                             "b_crate": monster['critical_rate'],
                             "b_cdmg": monster['critical_damage'],
                             "b_res": monster['resist'],
                             "b_acc": monster['accuracy']}
    else:
        optimizer_monster = None

    return optimizer_monster, csv_map
