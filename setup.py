#!/usr/bin/env python

from distutils.core import setup
try:
    import py2exe
except:
    pass

plugins = [('plugins', ['plugins/DemoPlugin.py', 'plugins/DemoPlugin.yapsy-plugin'])]

setup(name='SWParser',
      version='1.0',
      description='Summoners War Data Parser',
      author='Youness Alaoui',
      author_email='kakaroto@kakaroto.homelinux.net',
      url='https://github.com/kakaroto/SWParser',
      packages = ['SWParser'],
      options={"py2exe":{"optimize":2}},
      console = ['SWParser.py', 'SWProxy.py'],
      data_files=plugins,
     )
