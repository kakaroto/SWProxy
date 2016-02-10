from SWParser import *
from SWPlugin import SWPlugin
import logging

logger = logging.getLogger("SWProxy")


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

        SWPlugin.call_plugins('process_csv_row', ('visit', 'header', (visit_fieldnames, visit_header)))

        visit_writer = DictUnicodeWriter(visit_file, fieldnames=visit_fieldnames)
        visit_writer.writerow(visit_header)

        for monster in monsters:
            _, monster_csv = map_monster(monster, None, storage_id, friend['wizard_name'])

            SWPlugin.call_plugins('process_csv_row', ('visit', 'monster', (monster, monster_csv)))

            visit_writer.writerow(monster_csv)

            monster_runes = monster['runes']
            if isinstance(monster_runes, dict):
                monster_runes = monster_runes.values()
            monster_runes.sort(key = lambda r: r['slot_no'])
            for rune in monster_runes:
                _, rune_map = map_rune(rune, None)

                SWPlugin.call_plugins('process_csv_row', ('visit', 'rune', (rune, rune_map)))

                visit_writer.writerow(rune_map)

        visit_footer = []

        SWPlugin.call_plugins('process_csv_row', ('visit', 'footer', visit_footer))

        if len(visit_footer) > 0:
            visit_writer.writerows(visit_footer)

class GenerateVisitFriend(SWPlugin):
    def process_request(self, req_json, resp_json):
        if resp_json.get('command') == 'VisitFriend':
            parse_visit_data(resp_json)
            logger.info("Visit Friend data generated")
