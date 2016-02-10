import SWPlugin


class PrintUnitCollection(SWPlugin.SWPlugin):

    def process_request(self, req_json, resp_json):

        if resp_json.get('command') == 'GetUnitCollection':
            collection = resp_json['collection']
            print "Your collection has {}/{} monsters".format(
                sum([y['open'] for y in collection]),
                len(collection),
            )
