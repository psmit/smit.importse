#!/usr/bin/env python

from setuptools import setup

setup(name='smit.importse',
      version='0.0.1dev',
      description='Tool for importing SE dump to database',
      author='Peter Smit',
      author_email='peter@smitmail.eu',
      packages=['smit'],
      package_dir={'': 'src'},
      install_requires=[],
      entry_points = dict(console_scripts=[
        'import_se = smit.importse.importer:run',
        ])
      )
