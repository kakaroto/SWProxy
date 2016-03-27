import SWPlugin
import logging
import json

logger = logging.getLogger("SWProxy")


class SwarfarmExportPlugin(SWPlugin.SWPlugin):
    def process_request(self, req_json, resp_json):
        if resp_json.get('command') == 'HubUserLogin':
            wizard_id = resp_json.get('wizard_id')
            filename = str(wizard_id) + "-swarfarm.json"

            with open(filename, "w") as f:
                data = {
                    'inventory_info': resp_json['inventory_info'],
                    'unit_list': resp_json['unit_list'],
                    'runes': resp_json['runes'],
                    'building_list': resp_json['building_list'],
                    'deco_list': resp_json['deco_list'],
                    'wizard_info': resp_json['wizard_info'],
                    'unit_lock_list': resp_json['unit_lock_list'],
                    'helper_list': resp_json['helper_list'],
                    'rune_craft_item_list': resp_json['rune_craft_item_list'],
                }

                f.write(json.dumps(data))

            print "Created SWARFARM import file " + filename
