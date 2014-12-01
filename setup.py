#!/usr/bin/env python

from distutils.core import setup

# TO DO: figure out how to import version number automatically from code!

readme = open('README.txt', 'r')
README_TEXT = readme.read()
readme.close()

setup(name='jprofile',
      packages=['jprofile'],
      version='0.5.0',
      license='LGPL',
      platforms=['POSIX', 'Windows'],
      description=' Automated JP2 profiling for digitisation batches',
      long_description=README_TEXT,
      author='Johan van der Knijff',
      author_email='johan.vanderknijff@kb.nl',
      maintainer='Johan van der Knijff',
      maintainer_email='johan.vanderknijff@kb.nl',
      url='https://github.com/bitsgalore/jprofile'
      )
