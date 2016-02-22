from SWParser import *
from SWPlugin import SWPlugin
import logging

logger = logging.getLogger("SWProxy")


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
        "Mystical Scrolls": (9, 2),
        "Light & Darkness Scrolls": (9, 3),
        "? Scrolls(maybe Legendary?)": (9, 7),
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

        SWPlugin.call_plugins('process_csv_row', ('wizard', 'header', (wizard_fields, wizard_headers)))

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

        SWPlugin.call_plugins('process_csv_row', ('wizard', 'wizard', (wizard, wizard_data)))
        SWPlugin.call_plugins('process_csv_row', ('wizard', 'footer', wizard_footer))

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

        SWPlugin.call_plugins('process_csv_row', ('runes', 'header', (rune_fieldnames, runes_header)))

        rune_writer = DictUnicodeWriter(rune_file, fieldnames=rune_fieldnames)
        rune_writer.writerow(runes_header)

        for rune in runes:
            optimizer_rune, csv_rune = map_rune(rune, rune_id_mapping[rune['rune_id']])

            SWPlugin.call_plugins('process_csv_row', ('runes', 'rune', (rune, csv_rune)))

            optimizer['runes'].append(optimizer_rune)
            rune_writer.writerow(csv_rune)

        with open(str(wizard['wizard_id']) +"-monsters.csv", "wb") as monster_file:

            monster_fieldnames = ['id','name','level','grade','attribute','in_storage','hp', 'atk', 'hp', 'def', 'spd',
                                  'crate', 'cdmg', 'res', 'acc']

            monster_header = {'id': 'Monster Id','name': 'Name','level': 'Level','grade': 'Stars',
                              'attribute': 'Attribute','in_storage': 'In Storage','hp' : 'hp', 'atk': 'atk',
                              'def': 'def', 'spd': 'spd', 'crate':'cri rate', 'cdmg': 'cri dmg', 'res': 'resistance',
                              'acc': 'accuracy'}

            SWPlugin.call_plugins('process_csv_row', ('monster', 'header', (monster_fieldnames, monster_header)))

            monster_writer = DictUnicodeWriter(monster_file, fieldnames=monster_fieldnames)
            monster_writer.writerow(monster_header)

            for monster in monsters:
                optimizer_monster, csv_monster = map_monster(monster, monster_id_mapping, storage_id)

                SWPlugin.call_plugins('process_csv_row', ('monster', 'monster', (monster, csv_monster)))

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

                    SWPlugin.call_plugins('process_csv_row', ('runes', 'rune', (rune, csv_rune)))

                    rune_writer.writerow(csv_rune)

            rune_footer = []
            monster_footer = []

            SWPlugin.call_plugins('process_csv_row', ('runes', 'footer', rune_footer))
            SWPlugin.call_plugins('process_csv_row', ('monster', 'footer', monster_footer))

            if len(rune_footer) > 0:
                rune_writer.writerows(rune_footer)

            if len(monster_footer) > 0:
                monster_writer.writerows(monster_footer)


    with open(str(wizard['wizard_id']) +"-optimizer.json", "w") as f:
        f.write(json.dumps(optimizer))


class GenerateRunes(SWPlugin):
    def process_request(self, req_json, resp_json):
       if resp_json.get('command') in ('HubUserLogin', 'GuestLogin'):
            parse_login_data(resp_json)
            logger.info("Monsters and Runes data generated")
