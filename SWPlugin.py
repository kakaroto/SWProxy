from yapsy import IPlugin

class SWPlugin(IPlugin.IPlugin):
    def process_request(self, req_json, resp_json, plugins):
        pass

    def process_csv_row(self, csv_type, data_type, data):
        pass
