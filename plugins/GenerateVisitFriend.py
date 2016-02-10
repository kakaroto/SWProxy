import SWPlugin
from SWParser import parse_visit_data
import logging

logger = logging.getLogger("SWProxy")

class GenerateVisitFriend(SWPlugin.SWPlugin):
    def process_request(self, req_json, resp_json):
        if resp_json.get('command') == 'VisitFriend':
            parse_visit_data(resp_json)
            logger.info("Visit Friend data generated")
