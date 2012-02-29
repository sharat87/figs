#!/usr/bin/env python
# encoding: utf-8

from distutils.core import setup
import figs

setup(
    name='figs',
    version=figs.__version__.encode(),
    description='A towel wrapped ConfigParser API.',
    long_description=open('README.rst').read(),
    author=figs.__author__.encode(),
    author_email='shrikantsharat.k@gmail.com',
    url='http://figs.sharats.me',
    py_modules=['figs', 'tests'],
    license='MIT - http://mit.sharats.me',
    platforms='any',
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Topic :: Text Processing :: Markup',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ),
)
