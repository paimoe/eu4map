import unittest
import namedlist

from parsers import *

"""
todo
- different ideas, national/group/common
"""

class TestCountryParser(unittest.TestCase):
    def setUp(self):
        self.cp = CountryParser(test=True)

        self.austria = self.cp.parse_all(one='HAB')
        self.kilwa = self.cp.parse_all(one='ZAN')

    def test_load(self):
        self.assertIsNotNone(self.austria)
        self.assertIsInstance(self.austria, dict)
        # can't isinstance(self.austria, namedlist) so fudge it
        self.assertEqual(self.austria['HAB'].tag, 'HAB')
        self.assertEqual(len(self.austria), 1)

    def test_parser(self):
        a = self.austria['HAB']

        self.assertEqual(a.name, 'Austria')
        self.assertEqual(a.capital, 134)
        self.assertEqual(a.color, 'dcdcdc')
        self.assertEqual(a.culture, 'austrian')
        self.assertEqual(a.religion, 'catholic')
        self.assertEqual(a.techgroup, 'western')
        
    def test_ideas(self): 
        a = self.austria['HAB']
        self.assertEqual(a.ideastype, 'national')

        i = a.ideas
        self.assertIsInstance(i, dict)
        self.assertEqual(len(i), 11) # 7 nat ideas, free, start, bonus, trigger
        self.assertEqual(i['hofkriegsrat'], {'discipline': '0.03', 'reinforce_speed': '0.3'})
        self.assertTrue(i['free'])

    def test_renames(self): 
        z = self.kilwa['ZAN']
        self.assertEqual(z.name, 'Kilwa')
        self.assertNotEqual(z.name, 'Swahili')
        self.assertEqual(z.tag, 'ZAN')
        self.assertEqual(z.capital, 1196)

    def test_history(self): pass # when we implement history parse into history/countries

if __name__ == '__main__':
    # Has to be run on an installation with EU4 installed
    unittest.main()