import SWPlugin

class DemoPlugin(SWPlugin.SWPlugin):
    def process_request(self, req_json, resp_json, plugins):
        print "Found Summoners War API request : %s" % req_json['command']
