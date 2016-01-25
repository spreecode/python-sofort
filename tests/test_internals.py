# -*- coding: utf-8 -*-

import unittest

from sofort.internals import Config, strip_reason

class TestSofortConfig(unittest.TestCase):
    def test_init(self):
        c = Config(a=1, b='2', c=True)
        self.assertEqual(1, c.a)
        self.assertEqual('2', c.b)
        self.assertTrue(c.c)

    def test_clone(self):
        a = Config(bunny='hope', white='stripes')
        b = a.clone()
        self.assertIsNot(a, b)
        self.assertEqual(a.bunny, b.bunny)
        self.assertEqual(a.white, b.white)
        b.bunny = 'bugz'
        self.assertNotEqual(a.bunny, b.bunny)

    def test_deep_clone(self):
        a = Config(chips={
            'Lays': 'tasty',
            'Pringles': 'tasty',
            'Estrella': 'tasty'
        });
        b = a.clone()
        b.chips['Lays'] = 'salt'
        self.assertNotEqual(a.chips['Lays'], b.chips['Lays'])

    def test_update(self):
        c = Config(bunny='hope', white='stripes')

        c.update({'genre':'classical', 'era':'medieval'})\
         .update({'value':'priceless', 'weight': 12.4})\
         .update({'genre':'Heavy Metal'})

        self.assertEqual('Heavy Metal', c.genre)
        self.assertEqual(12.4, c.weight)
        self.assertEqual('medieval', c.era)
        self.assertEqual('stripes', c.white)

    def test_prepare_reason(self):
        self.assertEqual(u'Invoice 001', strip_reason(u'Invoice (:#001:)'))
        self.assertEqual(u'aezAEZ091+-.,', strip_reason(u'aezAEZ091+-.,'))
        self.assertEqual(u'üöäÄÜÖß', strip_reason(u'|üöäÄÜÖß|'))
