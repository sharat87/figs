Figs
====

Figs is a library for reading *ini* like configuration files easily. Figs
leverages the ``ConfigParser`` module from python's standard libraries.

I personally don't like the ``ConfigParser`` API very much, so I wrote this. The
idea is that the developer should have little overhead in thinking when using
this library, i.e., an intuitive API.

Usage
=====

If you are familiar with ``PyYaml`` or the standard library's ``json`` modules,
the following should be quite familiar to you.

To load a configuration, use the ``load``/``loads`` functions. The following
return the same::

    >>> # Takes a filename
    >>> conf = figs.load('config.ini')

    >>> # or a file-like object
    >>> conf = figs.load(open('config.ini'))

    >>> # Takes a string to be parsed
    >>> conf = figs.loads('''\
            [universe]
            answer = 42
            is_active = yes
            status = expanding
            ''')

And, to *dump* configuration::

    >>> # Takes a filename
    >>> figs.dump(conf, 'config.ini')

    >>> # or a file-like object
    >>> figs.dump(conf, open('config.ini'))

    >>> # Dump to string
    >>> figs.dumps(conf)
    [universe]
    answer = 42
    is_active = yes
    status = expanding

    >>> # You can also dump just a section
    >>> figs.dumps(conf.universe)
    answer = 42
    is_active = yes
    status = expanding

Those are the only functions in the figs module that you should be concerned
with.

Once you have the config object, how'd you use it? Surprise surprise! Anyway you
feel comfortable :)

Dictification
-------------

I know, you just want a dict of properties from the config file and be done with
it. Lets see if you can guess how this can be done?::

    >>> # Returns a dict like {'section-name': <Section object>}
    >>> dict(conf)

    >>> # Returns a dict like {'key': <TypeableStr object>}
    >>> dict(conf.universe)

You should keep in mind that ``dict`` on does *not* automatically do a ``dict``
on its Section objects. The ``TypeableStr`` class is a subclass of ``unicode``
with a few methods added (``as_bool``, ``as_int`` and ``as_float``).

If you want a dict of dicts, though, you can get that too.::

    >>> figs.as_dict(conf)

    >>> # or when loading
    >>> conf = figs.load('config.ini', as_dict=True)

The ``loads`` method also takes the ``as_dict`` argument. Note that the
``as_dict`` *has* to be a keyword argument.

Accesses
--------

::

    >>> conf.universe.answer
    u'42'
    >>> conf.universe.answer.as_int
    42
    >>> conf.universe.is_active
    u'yes'
    >>> conf.universe.is_active.as_bool
    True
    >>> conf.universe.status
    u'expanding'
    >>> conf.universe['status']
    u'expanding'

Similary to ``as_int`` as shown above, there are also ``as_bool`` (boolean
conversion done similar to how ``ConfigParser.getboolean`` does) and
``as_float``.

Check for presence
------------------

::

    >>> 'universe' in conf
    True
    >>> 'multiverse' in conf
    False
    >>> 'answer' in conf.universe
    True
    >>> 'is_active' in conf.universe
    True
    >>> 'is-active' in conf.universe
    False

Modifying configs
-----------------

Set new options...::

    >>> conf.universe.is_active = False
    >>> conf.universe.planet_maker = 'Magrathea'
    >>> conf.universe['earth-owners'] = 'mice'
    >>> figs.dumps(conf)
    [universe]
    answer = 42
    is_active = false
    status = expanding
    planet_maker = Magrathea
    earth-owners = mice

...on new sections::

    >>> conf.multiverse.is_active = True
    >>> figs.dumps(conf)
    [universe]
    answer = 42
    is_active = false
    status = expanding

    [multiverse]
    is_active = true

Deleting
--------

The API is very boring isn't it?::

    >>> del conf.universe.answer
    >>> del conf.multiverse

Now what?
=========

Well, if you have a life, get on with it. Seriously, there's nothing else to
reading config files here.

Meta
====

Author
------

Shrikant Sharat (http://sharats.me). `@sharat87`_ on twitter.

.. _@sharat87: http://twitter.com/sharat87

License
-------

MIT License (http://mit.sharats.me).

Contributing
------------

Code is available at the `github repository`_. Clone. Modify. Send pull request.
If the modification is fairly large, I prefer you open a `github issue`_ first
to discuss it.

.. _github repository: https://github.com/sharat87/figs
.. _github issue: https://github.com/sharat87/figs/issues

Changelog
---------

0.1.2
    Move to github.
