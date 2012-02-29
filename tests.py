#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals

import figs
from unittest import TestCase
from ConfigParser import NoOptionError, MissingSectionHeaderError
from StringIO import StringIO
import tempfile as tmp
import os
from textwrap import dedent

class TestLoad(TestCase):

    def setUp(self):
        tmp_file = tmp.NamedTemporaryFile(prefix='figs-test-',
                delete=False)
        tmp_file.write(dedent('''\
                [default]
                key = val
                '''))
        tmp_file.close()
        self.target_filename = tmp_file.name

    def tearDown(self):
        os.remove(self.target_filename)

    def test_filename(self):
        figs.load(self.target_filename)

    def test_file(self):
        f = open(self.target_filename)
        figs.load(f)
        self.assertFalse(f.closed)
        f.close()

    def test_string(self):
        conf = figs.loads('[default]\na = 1\n')
        self.assertEqual(conf.default.a, '1')

    def test_indented_string(self):
        conf = figs.loads('''\
            [default]
            a = 1
            ''')
        self.assertEqual(conf.default.a, '1')

    def test_as_dict(self):
        conf = figs.loads('''\
            [default]
            a = 1
            ''', as_dict=True)

        self.assertIsInstance(conf, dict)
        self.assertEqual(conf.viewkeys(), {'default'})
        self.assertEqual(conf['default'].viewkeys(), {'a'})

    def test_no_sections(self):
        conf = figs.loads('key1 = val1\nkey2 = val2\n')
        self.assertEqual(conf.key1, 'val1')
        self.assertEqual(conf.key2, 'val2')

    def test_no_first_section(self):
        self.assertRaises(MissingSectionHeaderError, lambda: figs.loads('''\
                key = val
                [section1]
                name = me
                '''))

    def test_no_sections_as_dict(self):
        conf = figs.loads('key1 = val1\nkey2 = val2\n', as_dict=True)

        self.assertIsInstance(conf, dict)
        self.assertEqual(conf.viewkeys(), {'key1', 'key2'})


class TestDump(TestCase):

    def setUp(self):
        self.conf_content = '[default]\nname = myself\n\n'
        self.conf = figs.loads(self.conf_content)

        tmp_file = tmp.NamedTemporaryFile(prefix='figs-test-',
                delete=False)
        tmp_file.close()
        self.target_filename = tmp_file.name

    def tearDown(self):
        os.remove(self.target_filename)

    def test_filename(self):
        figs.dump(self.conf, self.target_filename)
        with open(self.target_filename) as f:
            self.assertEqual(f.read(), self.conf_content)

    def test_file(self):
        sio = StringIO()
        figs.dump(self.conf, sio)
        self.assertEqual(sio.getvalue(), self.conf_content)
        self.assertFalse(sio.closed)

    def test_string(self):
        self.assertEqual(figs.dumps(self.conf), self.conf_content)

    def test_section(self):
        self.assertEqual(figs.dumps(self.conf.default),
                self.conf_content.split(None, 1)[-1])

    def test_no_sections(self):
        content = 'key1 = val1\nkey2 = val2\n\n'
        conf = figs.loads(content)
        self.assertEqual(figs.dumps(conf), content)

    def test_section_filename(self):
        figs.dump(self.conf.default, self.target_filename)
        with open(self.target_filename) as f:
            self.assertEqual(f.read(), self.conf_content.split(None, 1)[-1])


class TestAccesses(TestCase):

    def setUp(self):
        self.conf = figs.loads('''\
                [default]
                name = myself
                count = 1
                keys = 10
                [onemore]
                key = val
                ''')

    def test_access(self):
        # The following also checks that accessing a section/option multiple
        # times gives us the *same* object.

        # Existing section
        self.assertIs(self.conf['default'], self.conf.default)

        # Non-existent section
        self.assertIs(self.conf['defaulty'], self.conf.defaulty)

        # Existing option
        self.assertIs(self.conf.default['name'], self.conf.default.name)
        self.assertIs(self.conf.default['keys'], self.conf.default.keys)

        # Non-existing option
        self.assertRaises(NoOptionError, lambda: self.conf.default.namey)

    def test_contains(self):
        self.assertIn('default', self.conf)
        self.assertNotIn('defaulty', self.conf)
        self.assertIn('name', self.conf.default)
        self.assertNotIn('namey', self.conf.default)

    def test_section_list(self):
        sections = ['default', 'onemore']

        # Should be able to iterate any number of times.
        for sname, section in self.conf:
            self.assertIn(sname, sections)
            self.assertEqual(sname, section._name)

        self.assertEqual(list(s[0] for s in self.conf), sections)

    def test_section_dict(self):
        sections = dict(self.conf)

        self.assertEqual(sections.viewkeys(), {'default', 'onemore'})
        self.assertEqual(sections['default'], self.conf.default)

    def test_option_list(self):
        options = ['name', 'count', 'keys']

        for key, value in self.conf.default:
            self.assertIn(key, options)

        self.assertEqual(list(o[0] for o in self.conf.default), options)

    def test_option_dict(self):
        options = dict(self.conf.default)

        self.assertEqual(options.viewkeys(), {'name', 'count', 'keys'})
        self.assertEqual(options['name'], self.conf.default.name)


class TestChanges(TestCase):

    def setUp(self):
        self.conf = figs.loads('''\
                [default]
                name = myself
                count = 1
                [onemore]
                key = val
                ''')

    def test_set_option(self):
        self.conf.default.count = 10
        self.assertEqual(self.conf.default.count.as_int, 10)

        # Accessing it puts it in the cache.
        self.conf.default.count

        # Test if change updates cache.
        self.conf.default.count = 100
        self.assertEqual(self.conf.default.count.as_int, 100)

        self.conf.default.new = 1
        self.assertEqual(self.conf.default.new.as_int, 1)
        self.assertIn('new', self.conf.default)

    def test_set_option_as_item(self):
        self.conf.default['count'] = 10
        self.assertEqual(self.conf.default.count.as_int, 10)

    def test_new_section(self):
        self.assertIs(self.conf.universe, self.conf['universe'])

        self.conf.universe.answer = 42
        self.assertEqual(self.conf.universe.answer.as_int, 42)

        self.assertIn('universe', self.conf)

    def test_del_option(self):
        del self.conf.default.name
        self.assertNotIn('name', self.conf.default)

    def test_del_section(self):
        del self.conf.default
        self.assertNotIn('default', self.conf)


class TestTypability(TestCase):

    def test_unknown(self):
        unknowns = figs.loads('''\
                [unknowns]
                o1 = hohoho
                ''').unknowns

        self.assertRaises(ValueError, lambda: unknowns.o1.as_bool)
        self.assertRaises(ValueError, lambda: unknowns.o1.as_int)
        self.assertRaises(ValueError, lambda: unknowns.o1.as_float)

    def test_trues(self):
        conf = figs.loads('''\
                [trues]
                o1 = 1
                o2 = on
                o3 = yes
                o4 = true
                o5 = ON
                o6 = Yes
                o7 = True
                ''')
        map(lambda (key, val): self.assertIs(val, True,
                        msg=key + ' is not True'),
                ((o[0], o[1].as_bool) for o in conf.trues))

    def test_falses(self):
        conf = figs.loads('''\
                [falses]
                o1 = 0
                o2 = off
                o3 = no
                o4 = false
                o5 = OFF
                o6 = No
                o7 = False
                ''')
        map(lambda (key, val): self.assertIs(val, False,
                        msg=key + ' is not False'),
                ((o[0], o[1].as_bool) for o in conf.falses))

    def test_ints(self):
        ints = figs.loads('''\
                [ints]
                o1 = 1
                o2 = 10.1
                o3 = 10.8
                o4 = 1e2
                o5 = 1.2e2
                ''').ints

        # All values should be of type `int`.
        map(lambda (key, val): self.assertIsInstance(val, int,
                        msg=key + ' is not an int (' + repr(val) + ')'),
                ((o[0], o[1].as_int) for o in ints))

        self.assertEqual(ints.o1.as_int, 1)
        self.assertEqual(ints.o2.as_int, 10)
        self.assertEqual(ints.o3.as_int, 11)
        self.assertEqual(ints.o4.as_int, 100)
        self.assertEqual(ints.o5.as_int, 120)

    def test_floats(self):
        floats = figs.loads('''\
                [floats]
                o1 = 1
                o2 = 1.
                o3 = 1.0
                o4 = 1.1e1
                ''').floats

        # All values should be of type `int`.
        map(lambda (key, val): self.assertIsInstance(val, float,
                        msg=key + ' is not an int (' + repr(val) + ')'),
                ((o[0], o[1].as_float) for o in floats))

        self.assertEqual(floats.o1.as_float, 1)
        self.assertEqual(floats.o2.as_float, 1)
        self.assertEqual(floats.o3.as_float, 1)
        self.assertEqual(floats.o4.as_float, 11)


class TestErrors(TestCase):

    def test_databox_attr_access(self):
        db = figs.Databox()
        self.assertRaises(AttributeError, lambda: db._non_existent)
        self.assertRaisesRegexp(AttributeError, r'^Databox ',
                lambda: db._non_existent)

    def test_unknown_args_to_load(self):
        self.assertRaises(TypeError, figs.load, None,
                nonexistent_keyword_argument=1)
