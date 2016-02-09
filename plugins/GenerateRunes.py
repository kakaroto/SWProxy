import SWPlugin
from SWParser import parse_login_data


class GenerateRunes(SWPlugin.SWPlugin):

    def process_request(self, req_json, resp_json, plugins):

       if resp_json.get('command') in ('HubUserLogin', 'GuestLogin'):
            parse_login_data(resp_json, plugins)
            print "Monsters and Runes data generated"
