from yapsy.IPlugin import IPlugin


class DemoPlugin(IPlugin):
    def process_request(self, req_json, resp_json):
        print "Found Summoners War API request : %s" % req_json['command']
