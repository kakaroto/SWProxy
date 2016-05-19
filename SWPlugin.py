from yapsy import IPlugin
from yapsy.PluginManager import PluginManager
import os
import logging
import sys

logger = logging.getLogger(__name__)

class classproperty(object):
    def __init__(self, getter):
        self.getter= getter
    def __get__(self, instance, owner):
        return self.getter(owner)

class SWPlugin(IPlugin.IPlugin):
    _plugins = None

    @classmethod
    def load_plugins(cls):
        basepath = os.path.dirname(os.path.realpath(__file__))

        # if frozen (i.e. running from pyinstaller binary)
        # grab path from sys.executable.  Else use the path of this file
        if getattr(sys, 'frozen', False):
            basepath = os.path.dirname(os.path.realpath(sys.executable))

        manager = PluginManager()
        manager.setPluginPlaces([os.path.join(basepath, "plugins/")])
        manager.collectPlugins()
        ret = manager.getAllPlugins()
        logger.info('Loaded {} plugins'.format(len(ret)))
        return ret

    @classproperty
    def plugins(cls):
        if cls._plugins is None:
            cls._plugins = cls.load_plugins()
        return cls._plugins

    def process_request(self, req_json, resp_json):
        pass

    def process_csv_row(self, csv_type, data_type, data):
        pass

    @classmethod
    def call_plugins(cls, func_name, args):
        for plugin in cls.plugins:
            try:
                getattr(plugin.plugin_object, func_name)(*args)
            except Exception as e:
                logging.exception('Exception while executing plugin "%s": %s' \
                                  % (plugin.name, e))
