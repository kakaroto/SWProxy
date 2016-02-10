import SWPlugin
from SWParser import parse_login_data
import logging

logger = logging.getLogger("SWProxy")

class GenerateRunes(SWPlugin.SWPlugin):
    def process_request(self, req_json, resp_json):
       if resp_json.get('command') in ('HubUserLogin', 'GuestLogin'):
            parse_login_data(resp_json)
            logger.info("Monsters and Runes data generated")
