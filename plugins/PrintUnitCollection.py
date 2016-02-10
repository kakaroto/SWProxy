import SWPlugin
from SWParser.parser import monster_attribute

logger = logging.getLogger("SWProxy")

class PrintUnitCollection(SWPlugin.SWPlugin):

    def process_request(self, req_json, resp_json):
        if resp_json.get('command') == 'GetUnitCollection':
            collection = resp_json['collection']
            logger.info("Your collection has {}/{} monsters".format(
                sum([y['open'] for y in collection]),
                len(collection),
            ))
            for i in xrange(1, 6):
                logger.info("You found {}/{} {} monsters".format(
                    sum([y['open'] if str(y['unit_master_id'])[-1] == str(i) else 0 for y in collection]),
                    sum([1 if str(y['unit_master_id'])[-1] == str(i) else 0 for y in collection]),
                    monster_attribute(i)
                ))
