#!/usr/bin/python

import json
import sys
import struct
import os
from collections import OrderedDict
from smon_decryptor import decrypt_request, decrypt_response
from monsters import monsters_name_map

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

def write_rune(f, rune, rune_id, monster_id=0, monster_uid=0):
    if rune_id == None:
        f.write("%s,%s,%s,%s,%s,%s" %
                (rune['slot_no'],
                 rune_set_id(rune['set_id']),
                 rune['class'],
                 rune['upgrade_curr'],
                 rune_effect(rune['pri_eff']),
                 rune_effect(rune['prefix_eff'])))
    else:
        f.write("%s,%s,%s,%s,%s,%s,%s,%s,%s" %
                (rune_id,
                 "%s (%s)" % (monster_id, monster_name(monster_uid)) if monster_id != 0 else '0',
                 rune_set_id(rune['set_id']),
                 rune['slot_no'],
                 rune['class'],
                 rune['upgrade_curr'],
                 rune['sell_value'],
                 rune_effect(rune['pri_eff']),
                 rune_effect(rune['prefix_eff'])))
    if len(rune['sec_eff']) >= 4:
        f.write(",%s,%s,%s,%s\n" %
                 (rune_effect(rune['sec_eff'][0]),
                  rune_effect(rune['sec_eff'][1]),
                  rune_effect(rune['sec_eff'][2]),
                  rune_effect(rune['sec_eff'][3])))
    elif len(rune['sec_eff']) == 3:
        f.write(",%s,%s,%s,\n" %
                 (rune_effect(rune['sec_eff'][0]),
                  rune_effect(rune['sec_eff'][1]),
                  rune_effect(rune['sec_eff'][2])))
    elif len(rune['sec_eff']) == 2:
        f.write(",%s,%s,,\n" %
                 (rune_effect(rune['sec_eff'][0]),
                  rune_effect(rune['sec_eff'][1])))
    elif len(rune['sec_eff']) == 1:
        f.write(",%s,,,\n" %
                 (rune_effect(rune['sec_eff'][0])))
    else:
        f.write(",,,,\n")

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
    return {"id": rune_id,
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

def parse_login_data(data):
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

    with open(str(wizard['wizard_id']) + "-info.csv", "w") as f:
        f.write("Wizard id,Wizard Name,Crystals,Mana,Arena score")
        for name in inventory_map.keys():
            f.write(",%s" % name)
        f.write("\n")
        try:
            f.write(u"%s,%s,%s,%s,%s" %
                    (wizard['wizard_id'],
                     wizard['wizard_name'].encode('ascii', 'replace'),
                     wizard['wizard_crystal'],
                     wizard['wizard_mana'],
                     data['pvp_info']['arena_score']));
        except:
            pass
        for i in inventory_map.keys():
            t = inventory_map[i]
            found = False
            for item in inventory:
                if item['item_master_type'] == t[0] and item['item_master_id'] == t[1]:
                    f.write(",%s" % item['item_quantity'])
                    found = True
                    break
            if not found:
                f.write(",")
        f.write("\n")

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
        rune_id = rune_id + 1

    monster_id = 1
    for monster in monsters:
        monster_id_mapping[monster['unit_id']] = monster_id
        monster_id = monster_id + 1
        monster_runes = monster['runes']
        if isinstance(monster_runes, dict):
            monster_runes = monster_runes.values()
        monster_runes.sort(key = lambda r: r['slot_no'])
        for rune in monster_runes:
            rune_id_mapping[rune['rune_id']] = rune_id
            rune_id = rune_id + 1

    with open(str(wizard['wizard_id']) + "-runes.csv", "w") as fr:
        fr.write("Rune id,Equipped to monster,Rune set,Slot No,Stars,level,Sell price,Primary effect,Prefix effect,First Substat,Second Substat,Third Substat,Fourth Substat\n")
        for rune in runes:
            optimizer_rune = write_rune(fr, rune, rune_id_mapping[rune['rune_id']])
            optimizer['runes'].append(optimizer_rune)

        with open(str(wizard['wizard_id']) +"-monsters.csv", "w") as fm:
            fm.write("Monster id,name,level,Stars,Attribute,In Storage,hp,atk,def,spd,cri rate, cri dmg, resistance, accuracy\n")
            for monster in monsters:
                fm.write("%s,%s,%s,%s,%s,%s,%d,%s,%s,%s,%s,%s,%s,%s\n" %
                         (monster_id_mapping[monster['unit_id']],
                          monster_name(monster['unit_master_id']),
                          monster['unit_level'],
                          monster['class'],
                          monster_attribute(monster['attribute']),
                          "Yes" if monster['building_id'] == storage_id else "No",
                          int(monster['con']) * 15,
                          monster['atk'],
                          monster['def'],
                          monster['spd'],
                          monster['critical_rate'],
                          monster['critical_damage'],
                          monster['resist'],
                          monster['accuracy']))
                optimizer_monster = {"id": monster_id_mapping[monster['unit_id']],
                                     "name":"%s%s" % (monster_name(monster['unit_master_id'], "Unknown name"),
                                                      " (In Storage)" if monster['building_id'] == storage_id else ""),
                                     "level":monster['unit_level'],
                                     "b_hp":int(monster['con']) * 15,
                                     "b_atk":monster['atk'],
                                     "b_def":monster['def'],
                                     "b_spd":monster['spd'],
                                     "b_crate":monster['critical_rate'],
                                     "b_cdmg":monster['critical_damage'],
                                     "b_res":monster['resist'],
                                     "b_acc":monster['accuracy']}
                optimizer['mons'].append(optimizer_monster)
                monster_runes = monster['runes']
                if isinstance(monster_runes, dict):
                    monster_runes = monster_runes.values()
                monster_runes.sort(key = lambda r: r['slot_no'])
                for rune in monster_runes:
                    optimizer_rune = write_rune(fr, rune, rune_id_mapping[rune['rune_id']],
                                                monster_id_mapping[monster['unit_id']], monster['unit_master_id'])
                    optimizer_rune["monster_n"] = "%s%s" % (monster_name(monster['unit_master_id'], "Unknown name"),
                                                            " (In Storage)" if monster['building_id'] == storage_id else "")
                    optimizer['runes'].append(optimizer_rune)

    with open(str(wizard['wizard_id']) +"-optimizer.json", "w") as f:
        f.write(json.dumps(optimizer))



def parse_visit_data(data):
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

    with open("visit-" + str(wizard_id) +"-monsters.csv", "w") as fm:
        fm.write("Wizard Name,name,Stars,Level,Attribute,In Storage,hp,atk,def,spd,cri rate, cri dmg, resistance, accuracy,Rune Slot No,Rune set,Stars,Level,Primary effect,Prefix effect,First Substat,Second Substat,Third Substat,Fourth Substat\n")
        for monster in monsters:
            fm.write(u"%s,%s,%s,%s,%s,%s,%d,%s,%s,%s,%s,%s,%s,%s,,,,,,,,,,\n" %
                     (friend['wizard_name'].encode('ascii', 'replace'),
                      monster_name(monster['unit_master_id']),
                      monster['class'],
                      monster['unit_level'],
                      monster_attribute(monster['attribute']),
                      "Yes" if monster['building_id'] == storage_id else "No",
                      int(monster['con']) * 15,
                      monster['atk'],
                      monster['def'],
                      monster['spd'],
                      monster['critical_rate'],
                      monster['critical_damage'],
                      monster['resist'],
                      monster['accuracy']))
            monster_runes = monster['runes']
            if isinstance(monster_runes, dict):
                monster_runes = monster_runes.values()
            monster_runes.sort(key = lambda r: r['slot_no'])
            for rune in monster_runes:
                fm.write(u",,,,,,,,,,,,,,")
                write_rune(fm, rune, None)
