#!/usr/bin/env python

from distutils.core import setup
import glob
try:
    import py2exe
except:
    pass

plugin_patterns = ('plugins/*.py', 'plugins/*.yapsy-plugin')
plugins = []
for pattern in plugin_patterns:
    plugins.extend(glob.glob(pattern))

setup(name='SWParser',
      version='1.0',
      description='Summoners War Data Parser',
      author='Youness Alaoui',
      author_email='kakaroto@kakaroto.homelinux.net',
      url='https://github.com/kakaroto/SWParser',
      packages = ['SWParser', 'SWParser.gui'],
      options={"py2exe":{"optimize":2,"includes":["sip"], "dll_excludes": ["MSVCP90.dll"]}},
      console = ['SWParser.py', 'SWProxy.py'],
      data_files=[('plugins', plugins)],
     )
