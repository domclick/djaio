#!/usr/bin/env python
import os
from setuptools import setup, find_packages

base = os.path.dirname(os.path.abspath(__file__))

install_requires = [
    'aiohttp',
    'aiohttp_jinja2',
    'asyncio',
    'aiohttp_debugtoolbar',
    'aiohttp_autoreload',
]

tests_require = [
    'pytest',
    'pytest-aiohttp'
]

setup(name='djaio',
      version='0.0.1',
      description='Djaio - Django-inspired AsyncIO web framework',
      long_description='',
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