import SWPlugin
import logging

logger = logging.getLogger("SWProxy")

class DemoPlugin(SWPlugin.SWPlugin):
    def process_request(self, req_json, resp_json):
        logger.info("Found Summoners War API request (wizard_id: %(wizard_id)s) : %(command)s " % req_json)
