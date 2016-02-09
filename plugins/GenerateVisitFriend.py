import SWPlugin
from SWParser import parse_visit_data


class GenerateVisitFriend(SWPlugin.SWPlugin):

    def process_request(self, req_json, resp_json, plugins):

        print resp_json

        if resp_json.get('command') == 'VisitFriend':
            parse_visit_data(resp_json, plugins)
            print "Visit Friend data generated"
        
         