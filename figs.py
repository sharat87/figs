#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals

import ConfigParser as cp
from collections import OrderedDict as odict
import sys
from StringIO import StringIO
from textwrap import dedent

__version__ = '0.1'
__author__ = 'Shrikant Sharat'

__all__ = ['dump', 'dumps', 'load', 'loads']

def mkparser():
    return cp.SafeConfigParser(defaults=None, dict_type=odict,
            allow_no_value=True)

class Databox(object):

    def __getattr__(self, name):
        if name.startswith('_'):
            try:
                return object.__getattr__(self, name)
            except AttributeError:
                raise AttributeError(self.__class__.__name__ + ' object ' +
                        repr(name) + ' has no attribute ' + repr(name))
        else:
            return self[name]

    def __setattr__(self, name, value):
        if name.startswith('_'):
            object.__setattr__(self, name, value)
        else:
            self[name] = value

    def __delattr__(self, name):
        del self[name]


class Config(Databox):

    def __init__(self, fp):
        self._parser = mkparser()
        self._no_sections = False

        content = fp.read()
        try:
            self._parser.readfp(StringIO(content))
        except cp.MissingSectionHeaderError:
            self._parser.readfp(StringIO('[-dummy-]\n' + content))
            if len(self._parser.sections()) != 1:
                raise
            self._no_sections = True

        # Only one Section instance exists for each section.
        self._section_cache = {}

    def __contains__(self, section):
        return self._parser.has_section(section)

    def __getitem__(self, name):
        name = unicode(name)

        if name not in self._section_cache:
            self._section_cache[name] = Section(self, name)

        return self._section_cache[name]

    def __delitem__(self, section):
        self._parser.remove_section(section)

    def __iter__(self):
        for section_name in self.keys():
            yield section_name, self[section_name]

    # Calling ``dict()`` over a ``Config`` object will first do a ``.keys()``
    # and build a dict with those keys and items, obtained from ``[]`` syntax.
    # If ``.keys`` raises AttributeError, then ``iter()`` is used and 2-tuples
    # of key and value are expected to be yielded. When ``.keys()`` is called,
    # the Section object created for ``.keys`` name will call this method, from
    # its ``__call__``, so the ``dict()`` builtin won't know what hit it.
    # Similar thing is done for ``dict()`` a Section object.
    def _keys(self):
        return self._parser.sections()

    def _dump(self, f=sys.stdout):
        close = False
        if not hasattr(f, 'write'):
            f = open(f, 'w')
            close = True
        self._parser.write(f)
        if close:
            f.close()


class Section(Databox):

    def __init__(self, config, name):
        self._config = config
        self._parser = config._parser
        self._name = name

        # Only one TypableStr instance exists for each option.
        self._option_cache = {}

    def __contains__(self, key):
        return self._parser.has_option(self._name, key)

    def __getitem__(self, key):
        key = unicode(key)

        if key not in self._option_cache:
            self._option_cache[key] = TypableStr(self, key,
                    self._parser.get(self._name, key))

        return self._option_cache[key]

    def __setitem__(self, key, value):

        if not self._parser.has_section(self._name):
            self._parser.add_section(self._name)

        self._parser.set(self._name, key, unicode(value))
        self._option_cache.pop(key, None)

    def __delitem__(self, key):
        if self._parser.has_option(self._name, key):
            self._parser.remove_option(self._name, key)

    def __iter__(self):
        for key in self._parser.options(self._name):
            yield key, self[key]

    def _dump(self, f=sys.stdout):

        close = False
        if not hasattr(f, 'write'):
            f = open(f, 'w')
            close = True

        parser = mkparser()

        parser.add_section('-dummy-')
        for key, val in self._parser.items(self._name):
            parser.set('-dummy-', key, val)

        tmp = StringIO()
        parser.write(tmp)
        content = tmp.getvalue().split(None, 1)[-1]

        f.write(content)

        if close:
            f.close()

    def __call__(self, *args, **kwargs):
        """Sections are not callable. But attributes on config can be. So, this
        is a wild hack to allow calling ``conf.method()`` instead of
        ``conf._method()``. This is an effort to make both of the above work the
        same, but still allow ``conf.method`` to be the same as
        ``conf['method']``"""
        return getattr(Config, '_' + self._name)(self._config, *args, **kwargs)

    def _keys(self):
        return self._parser.options(self._name)


class TypableStr(unicode):

    def __new__(cls, _section, _name, string):
        self = super(TypableStr, cls).__new__(cls, string)
        self._section = _section
        self._name = _name
        return self

    @property
    def as_bool(self):
        l = self.lower()
        if l in ['1', 'on', 'yes', 'true']:
            return True
        elif l in ['0', 'off', 'no', 'false']:
            return False
        raise ValueError('Cannot read a boolean from ' + repr(self))

    @property
    def as_int(self):
        try:
            return int(self)
        except ValueError, e:
            try:
                return int(round(float(self)))
            except ValueError:
                raise e

    @property
    def as_float(self):
        return float(self)

    def __call__(self, *args, **kwargs):
        return getattr(Section, '_' + self._name)(self._section,
                *args, **kwargs)


def load(f, **kwargs):

    # Can't directly take in ``as_dict`` as that would shadow the module level
    # function, which is needed here.
    _as_dict = kwargs.pop('as_dict', False)

    if len(kwargs):
        raise TypeError('load() got an unexpected keyword argument ' +
                repr(kwargs.keys().pop()))

    close = False
    if not hasattr(f, 'readline'):
        f = open(f)
        close = True

    conf = Config(f)

    if close:
        f.close()

    if conf._no_sections:
        conf = conf['-dummy-']

    if _as_dict:
        return as_dict(conf)
    else:
        return conf

def loads(content, *args, **kwargs):
    return load(StringIO(dedent(content)), *args, **kwargs)

def dump(conf, f):
    return conf._dump(f)

def dumps(conf):
    sio = StringIO()
    dump(conf, sio)
    return sio.getvalue()

def as_dict(conf):
    if isinstance(conf, Config):
        return dict((section_name, dict(section))
                for section_name, section in conf)
    else:
        return dict(conf)
