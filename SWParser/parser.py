#!/usr/bin/env python

import csv
import json
import cStringIO
import sys
import struct
import numbers
import os
import codecs
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

def rune_effect_type(typ):
    if typ == 0:
        return ""
    elif typ == 1:
        return "HP flat"
    elif typ == 2:
        return "HP%"
    elif typ == 3:
        return "ATK flat"
    elif typ == 4:
        return "ATK%"
    elif typ == 5:
        return "DEF flat"
    elif typ == 6:
        return "DEF%"
    elif typ == 8:
        return "SPD"
    elif typ == 9:
        return "CRate"
    elif typ == 10:
        return "CDmg"
    elif typ == 11:
        return "RES"
    elif typ == 12:
        return "ACC"
    else:
        return "UNKNOWN"


def rune_effect(eff):
    typ = eff[0]
    value = eff[1]
    if len(eff) > 3:
        if eff[3] != 0:
            if typ == 1 or typ == 3 or typ == 5 or typ == 8:
                value = "%s -> +%s" % (value, str(int(value) + int(eff[3])))
            else:
                value = "%s%% -> %s" % (value, str(int(value) + int(eff[3])))
    if typ == 0:
        ret = ""
    elif typ == 1:
        ret = "HP +%s" % value
    elif typ == 2:
        ret = "HP %s%%" % value
    elif typ == 3:
        ret = "ATK +%s" % value
    elif typ == 4:
        ret = "ATK %s%%" % value
    elif typ == 5:
        ret = "DEF +%s" % value
    elif typ == 6:
        ret = "DEF %s%%" % value
    elif typ == 8:
        ret = "SPD +%s" % value
    elif typ == 9:
        ret = "CRI Rate %s%%" % value
    elif typ == 10:
        ret = "CRI Dmg %s%%" % value
    elif typ == 11:
        ret = "Resistance %s%%" % value
    elif typ == 12:
        ret = "Accuracy %s%%" % value
    else:
        ret = "UNK %s %s" % (typ, value)

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

def map_rune(rune, rune_id, monster_id=0, monster_uid=0):
    cvs_map ={
        'slot': rune['slot_no'],
        'rune_set': rune['set_id'],
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

    sub_atkf = "-"
    sub_atkp = "-"
    sub_hpf = "-"
    sub_hpp = "-"
    sub_deff = "-"
    sub_defp = "-"
    sub_res = "-"
    sub_acc = "-"
    sub_spd = "-"
    sub_cdmg = "-"
    sub_crate = "-"

    for sec_eff in rune['sec_eff']:
        if rune_effect_type(sec_eff[0]) == "ATK flat":
            sub_atkf = sec_eff[1] + sec_eff[3]
        elif rune_effect_type(sec_eff[0]) == "ATK%":
            sub_atkp = sec_eff[1] + sec_eff[3]
        elif rune_effect_type(sec_eff[0]) == "HP flat":
            sub_hpf = sec_eff[1] + sec_eff[3]
        elif rune_effect_type(sec_eff[0]) == "HP%":
            sub_hpp = sec_eff[1] + sec_eff[3]
        elif rune_effect_type(sec_eff[0]) == "DEF flat":
            sub_deff = sec_eff[1] + sec_eff[3]
        elif rune_effect_type(sec_eff[0]) == "DEF%":
            sub_defp = sec_eff[1] + sec_eff[3]
        elif rune_effect_type(sec_eff[0]) == "RES":
            sub_res = sec_eff[1] + sec_eff[3]
        elif rune_effect_type(sec_eff[0]) == "ACC":
            sub_acc = sec_eff[1] + sec_eff[3]
        elif rune_effect_type(sec_eff[0]) == "SPD":
            sub_spd = sec_eff[1] + sec_eff[3]
        elif rune_effect_type(sec_eff[0]) == "CDmg":
            sub_cdmg = sec_eff[1] + sec_eff[3]
        elif rune_effect_type(sec_eff[0]) == "CRate":
            sub_crate = sec_eff[1] + sec_eff[3]

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
            "s1_t": rune_effect_type(rune['sec_eff'][0][0]) if len(rune['sec_eff']) >= 1 else "",
            "s1_v": rune['sec_eff'][0][1] + rune['sec_eff'][0][3] if len(rune['sec_eff']) >= 1 else 0,
            "s2_t": rune_effect_type(rune['sec_eff'][1][0]) if len(rune['sec_eff']) >= 2 else "",
            "s2_v": rune['sec_eff'][1][1] + rune['sec_eff'][1][3] if len(rune['sec_eff']) >= 2 else 0,
            "s3_t": rune_effect_type(rune['sec_eff'][2][0]) if len(rune['sec_eff']) >= 3 else "",
            "s3_v": rune['sec_eff'][2][1] + rune['sec_eff'][2][3] if len(rune['sec_eff']) >= 3 else 0,
            "s4_t": rune_effect_type(rune['sec_eff'][3][0]) if len(rune['sec_eff']) >= 4 else "",
            "s4_v": rune['sec_eff'][3][1] + rune['sec_eff'][3][3] if len(rune['sec_eff']) >= 4 else 0,
            "locked":0,
            "sub_res":sub_res,
            "sub_cdmg":sub_cdmg,
            "sub_atkf": sub_atkf,
            "sub_acc": sub_acc,
            "sub_atkp": sub_atkp,
            "sub_defp": sub_defp,
            "sub_deff": sub_deff,
            "sub_hpp": sub_hpp,
            "sub_hpf": sub_hpf,
            "sub_spd": sub_spd,
            "sub_crate": sub_crate}

    return optimizer_map, cvs_map


def parse_login_data(data, plugins=[]):
    try:
        wizard = data['wizard_info']
    except:
        wizard = {'wizard_id': 0}
    try:
        inventory = data['inventory_info']
    except:
        inventory = []
    try:
        monsters = data['unit_list']
    except:
        monsters = []
    try:
        runes = data['runes']
    except:
        runes = []

    if isinstance(runes, dict):
        runes = runes.values()

    inventory_map = {
        "Unknown Scrolls": (9, 1),
        "? Scrolls(maybe mystical?)": (9, 2),
        "? Scrolls(maybe legendary?)": (9, 3),
        "? Scrolls(maybe L&D?)": (9, 7),
        "Exclusive Summons": (9, 8),
        "Legendary Summoning Pieces": (9, 9),
        "Light & Dark Summoning Pieces": (9, 10),
        "Low Magic Essence": (11, 11006),
        "Mid Magic Essence": (11, 12006),
        "High Magic Essence": (11, 13006),
        "Low Water Essence": (11, 11001),
        "Mid Water Essence": (11, 12001),
        "High Water Essence": (11, 13001),
        "Low Fire Essence": (11, 11002),
        "Mid Fire Essence": (11, 12002),
        "High Fire Essence": (11, 13002),
        "Low Wind Essence": (11, 11003),
        "Mid Wind Essence": (11, 12003),
        "High Wind Essence": (11, 13003),
        "Low Light Essence": (11, 11004),
        "Mid Light Essence": (11, 12004),
        "High Light Essence": (11, 13004),
        "Low Dark Essence": (11, 11005),
        "Mid Dark Essence": (11, 12005),
        "High Dark Essence": (11, 13005),
    }
    inventory_map = OrderedDict(sorted(inventory_map.items(), key=lambda t: t[1][0] * t[1][1]))

    storage_id = None
    for building in data['building_list']:
        if building['building_master_id'] == 25:
            storage_id = building['building_id']
            break
    monsters.sort(key = lambda mon: (1 if mon['building_id'] == storage_id else 0,
                                     6 - mon['class'], 40 - mon['unit_level'], mon['attribute'],
                                     1 - ((mon['unit_master_id'] / 10) % 10), mon['unit_id']))

    runes.sort(key = lambda r: (r['set_id'], r['slot_no']))

    with open(str(wizard['wizard_id']) + ".json", "w") as f:
        f.write(json.dumps(data, indent=4))

    with open(str(wizard['wizard_id']) + "-swarfarm.json", "w") as f:
        f.write(json.dumps({
            'inventory_info': inventory,
            'unit_list': monsters,
            'runes': runes,
            'building_list': data['building_list'],
            'deco_list': data['deco_list'],
            'wizard': wizard,
            'unit_lock_list': data['unit_lock_list'],
            'helper_list': data['helper_list'],
        }))

    with open(str(wizard['wizard_id']) + "-info.csv", "wb") as wizard_file:
        wizard_fields = ['id','name','crystal','mana','arena']

        wizard_headers = {'id': 'Wizard id', 'name': 'Wizard Name', 'crystal': 'Crystals', 'mana': 'Mana',
                   'arena': 'Arena score'}

        for name in inventory_map.keys():
            wizard_fields.append(name)
            wizard_headers[name] = name

        for plugin in plugins:
            plugin.plugin_object.process_csv_row('wizard', 'header', (wizard_fields, wizard_headers))

        wizard_writter = DictUnicodeWriter(wizard_file, fieldnames=wizard_fields)
        wizard_writter.writerow(wizard_headers)

        wizard_data = {'id': wizard['wizard_id'],
                       'name': wizard['wizard_name'],
                       'crystal': wizard['wizard_crystal'],
                       'mana': wizard['wizard_mana'],
                       'arena': data['pvp_info']['arena_score']
                       }

        for i in inventory_map.keys():
            t = inventory_map[i]
            for item in inventory:
                if item['item_master_type'] == t[0] and item['item_master_id'] == t[1]:
                    wizard_data[i] = item['item_quantity']

        wizard_footer = []

        for plugin in plugins:
            plugin.plugin_object.process_csv_row('wizard', 'wizard', (wizard, wizard_data))
            plugin.plugin_object.process_csv_row('wizard', 'footer', wizard_footer)

        wizard_writter.writerow(wizard_data)

        if len(wizard_footer) > 0:
            wizard_writter.writerows(wizard_footer)

    optimizer = {
        "runes": [],
        "mons": [],
        "savedBuilds": [],
    }
    rune_id_mapping = {}
    monster_id_mapping = {}

    rune_id = 1
    for rune in runes:
        rune_id_mapping[rune['rune_id']] = rune_id
        rune_id += 1

    monster_id = 1
    for monster in monsters:
        monster_id_mapping[monster['unit_id']] = monster_id
        monster_id += 1
        monster_runes = monster['runes']
        if isinstance(monster_runes, dict):
            monster_runes = monster_runes.values()
        monster_runes.sort(key = lambda r: r['slot_no'])
        for rune in monster_runes:
            rune_id_mapping[rune['rune_id']] = rune_id
            rune_id += 1

    with open(str(wizard['wizard_id']) + "-runes.csv", "wb") as rune_file:
        rune_fieldnames = ['rune_id','monster_id','rune_set','slot','rune_grade','rune_level','sell_price','pri_eff'
            ,'pre_eff','sub1','sub2','sub3','sub4']

        runes_header = {'rune_id': 'Rune id','monster_id': 'Equipped to monster', 'rune_set': 'Rune set', 'slot': 'Slot No',
                  'rune_grade': 'Stars', 'rune_level': 'level', 'sell_price': 'Sell Price', 'pri_eff': 'Primary effect',
                  'pre_eff': 'Prefix effect', 'sub1': 'First Substat', 'sub2': 'Second Substat', 'sub3': 'Third Substat',
                  'sub4': 'Fourth Substat'
                  }

        for plugin in plugins:
            plugin.plugin_object.process_csv_row('runes', 'header', (rune_fieldnames, runes_header))

        rune_writer = DictUnicodeWriter(rune_file, fieldnames=rune_fieldnames)
        rune_writer.writerow(runes_header)

        for rune in runes:
            optimizer_rune, csv_rune = map_rune(rune, rune_id_mapping[rune['rune_id']])

            for plugin in plugins:
                plugin.plugin_object.process_csv_row('runes', 'rune', (rune, csv_rune))

            optimizer['runes'].append(optimizer_rune)
            rune_writer.writerow(csv_rune)

        with open(str(wizard['wizard_id']) +"-monsters.csv", "wb") as monster_file:

            monster_fieldnames = ['id','name','level','grade','attribute','in_storage','hp', 'atk', 'hp', 'def', 'spd',
                                  'crate', 'cdmg', 'res', 'acc']

            monster_header = {'id': 'Monster Id','name': 'Name','level': 'Level','grade': 'Stars',
                              'attribute': 'Attribute','in_storage': 'In Storage','hp' : 'hp', 'atk': 'atk',
                              'def': 'def', 'spd': 'spd', 'crate':'cri rate', 'cdmg': 'cri dmg', 'res': 'resistance',
                              'acc': 'accuracy'}

            for plugin in plugins:
                plugin.plugin_object.process_csv_row('monster', 'header', (monster_fieldnames, monster_header))

            monster_writer = DictUnicodeWriter(monster_file, fieldnames=monster_fieldnames)
            monster_writer.writerow(monster_header)

            for monster in monsters:
                optimizer_monster, csv_monster = map_monster(monster, monster_id_mapping, storage_id)

                for plugin in plugins:
                    plugin.plugin_object.process_csv_row('monster', 'monster', (monster, csv_monster))

                monster_writer.writerow(csv_monster)

                optimizer['mons'].append(optimizer_monster)
                monster_runes = monster['runes']
                if isinstance(monster_runes, dict):
                    monster_runes = monster_runes.values()
                monster_runes.sort(key = lambda r: r['slot_no'])
                for rune in monster_runes:
                    optimizer_rune, csv_rune = map_rune(rune, rune_id_mapping[rune['rune_id']],
                                                monster_id_mapping[monster['unit_id']], monster['unit_master_id'])
                    optimizer_rune["monster_n"] = "%s%s" % (monster_name(monster['unit_master_id'], "Unknown name"),
                                                            " (In Storage)" if monster['building_id'] == storage_id else "")
                    optimizer['runes'].append(optimizer_rune)

                    for plugin in plugins:
                        plugin.plugin_object.process_csv_row('runes', 'rune', (rune, csv_rune))

                    rune_writer.writerow(csv_rune)

            rune_footer = []
            monster_footer = []

            for plugin in plugins:
                plugin.plugin_object.process_csv_row('runes', 'footer', rune_footer)
                plugin.plugin_object.process_csv_row('monster', 'footer', monster_footer)

            if len(rune_footer) > 0:
                rune_writer.writerows(rune_footer)

            if len(monster_footer) > 0:
                monster_writer.writerows(monster_footer)


    with open(str(wizard['wizard_id']) +"-optimizer.json", "w") as f:
        f.write(json.dumps(optimizer))


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


def parse_visit_data(data, plugins=[]):
    friend = data['friend']
    monsters = friend['unit_list']

    storage_id = None
    wizard_id = 'unknown'
    for building in friend['building_list']:
        wizard_id = building['wizard_id']
        if building['building_master_id'] == 25:
            storage_id = building['building_id']
            break
    monsters.sort(key = lambda mon: (1 if mon['building_id'] == storage_id else 0,
                                     6 - mon['class'], 40 - mon['unit_level'],
                                     mon['attribute'], mon['unit_id']))

    with open("visit-" + str(wizard_id) + ".json", "w") as f:
        f.write(json.dumps(data, indent=4))

    with open("visit-" + str(wizard_id) + "-monsters.csv", "wb") as visit_file:
        visit_fieldnames = ['wizard_name', 'name', 'grade', 'level', 'attribute', 'in_storage', 'hp', 'atk', 'hp',
                            'def', 'spd', 'crate', 'cdmg', 'res', 'acc', 'slot', 'rune_set','rune_grade','rune_level',
                            'pri_eff','pre_eff','sub1','sub2','sub3','sub4']

        visit_header = {'wizard_name': 'Wizard Name','name': 'Name','level': 'Level','grade': 'Stars',
                        'attribute': 'Attribute','in_storage': 'In Storage','hp' : 'hp', 'atk': 'atk', 'def': 'def',
                        'spd': 'spd', 'crate':'cri rate', 'cdmg': 'cri dmg', 'res': 'resistance', 'acc': 'accuracy',
                        'rune_set': 'Rune set', 'slot': 'Slot No', 'rune_grade': 'Stars', 'rune_level': 'level',
                        'pri_eff': 'Primary effect', 'pre_eff': 'Prefix effect', 'sub1': 'First Substat',
                        'sub2': 'Second Substat', 'sub3': 'Third Substat', 'sub4': 'Fourth Substat',
                        }

        for plugin in plugins:
            plugin.plugin_object.process_csv_row('visit', 'header', (visit_fieldnames, visit_header))

        visit_writer = DictUnicodeWriter(visit_file, fieldnames=visit_fieldnames)
        visit_writer.writerow(visit_header)

        for monster in monsters:
            _, monster_csv = map_monster(monster, None, storage_id, friend['wizard_name'])

            for plugin in plugins:
                plugin.plugin_object.process_csv_row('visit', 'monster', (monster, monster_csv))

            visit_writer.writerow(monster_csv)

            monster_runes = monster['runes']
            if isinstance(monster_runes, dict):
                monster_runes = monster_runes.values()
            monster_runes.sort(key = lambda r: r['slot_no'])
            for rune in monster_runes:
                _, rune_map = map_rune(rune, None)

                for plugin in plugins:
                    plugin.plugin_object.process_csv_row('visit', 'rune', (rune, rune_map))

                visit_writer.writerow(rune_map)

        visit_footer = []

        for plugin in plugins:
            plugin.plugin_object.process_csv_row('visit', 'footer', visit_footer)

        if len(visit_footer) > 0:
            visit_writer.writerows(visit_footer)
