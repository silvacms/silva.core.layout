# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from setuptools import setup, find_packages
import os

version = '2.1a1'

setup(name='silva.core.layout',
      version=version,
      description="Layout for Silva",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='layout silva core',
      author='Infrae',
      author_email='info@infrae.com',
      url='http://infrae.com/products/silva',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['silva', 'silva.core'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'silva.resourceinclude',
          'five.grok',
          'silva.core.views > 2.0.999, < 2.1.999',
          'silva.core.conf > 2.0.999, < 2.1.999',
          ],
      )
