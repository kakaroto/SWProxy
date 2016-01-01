#!/usr/bin/env python

from setuptools import setup, find_packages
try:
    import py2exe
except:
    pass


setup(name='SWParser',
      version='1.0',
      description='Summoners War Data Parser',
      author='Youness Alaoui',
      author_email='kakaroto@kakaroto.homelinux.net',
      url='https://github.com/kakaroto/SWParser',
      packages=find_packages(),
      console = ['parser.py']
     )
