#!/usr/bin/env python
import os
from setuptools import setup, find_packages

base = os.path.dirname(os.path.abspath(__file__))

install_requires = [
    'aiohttp==1.0.5',
    'aiohttp_jinja2',
    'asyncio',
    'aiohttp_debugtoolbar',
    'aiohttp_autoreload',
    'schematics>=2.0.0.dev2',
    'aiopg==0.11.0',
]

tests_require = [
    'pytest',
    'pytest-aiohttp'
]

setup(name='djaio',
      version='0.0.11',
      description='Djaio - Django-inspired AsyncIO web framework',
      author='Vadim Tregubov',
      author_email='vatregubov@sberned.ru',
      url='https://github.com/Sberned/djaio',
      packages=find_packages(),
      install_requires=install_requires,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Operating System :: MacOS',
          'Operating System :: POSIX :: Linux',
          'Topic :: System :: Software Distribution',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
      ],
      tests_require=tests_require
)
