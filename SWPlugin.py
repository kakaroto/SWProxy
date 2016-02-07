from yapsy import IPlugin
import logging

class SWPlugin(IPlugin.IPlugin):
    def process_request(self, req_json, resp_json, plugins):
        pass

    def process_csv_row(self, csv_type, data_type, data):
        pass


def call_plugins(plugins, func_name, args):
    for plugin in plugins:
        try:
            getattr(plugin.plugin_object, func_name)(*args)
        except Exception as e:
            print e
            logging.exception('Exception while executing plugin "%s": %s' \
                             % (plugin.plugin_object.__class__.__name__, e))
