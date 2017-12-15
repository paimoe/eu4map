import unittest
import namedlist

from parsers import *

"""
todo
- different ideas, national/group/common
"""
class EU4MapTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cp = CountryParser(test=True)
        pp = ProvinceParser(test=True)

        # Country files
        cls.austria = cp.parse_all(one='HAB')
        cls.kilwa = cp.parse_all(one='ZAN')    

        # province files
        cls.stockholm = pp.parse_all(one=1)
        cls.messina = pp.parse_all(one=124)

class TestCountryParser(EU4MapTest):

    def test_load(self):
        self.assertIsNotNone(self.austria)
        self.assertIsInstance(self.austria, dict)
        # can't isinstance(self.austria, namedlist) so fudge it
        self.assertEqual(self.austria['HAB'].tag, 'HAB')
        self.assertEqual(len(self.austria), 1)

    def test_parser(self):
        a = self.austria['HAB']

        self.assertEqual(a.name, 'Austria')
        self.assertEqual(a.capital, 134) # tests color
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

class TestProvinceParser(EU4MapTest): 
    def test_parse(self):
        s = self.stockholm[1]

        self.assertEqual(len(self.stockholm), 1)
        self.assertIsInstance(self.stockholm, dict)
        self.assertEqual(s.id, 1)
        self.assertEqual(s.name, 'Stockholm')
        self.assertEqual(s.owner, 'SWE')
        #self.assertEqual(s.controller, 'SWE')
        self.assertEqual(s.cores, ['SWE'])
        self.assertEqual(s.culture, 'swedish')
        self.assertEqual(s.religion, 'catholic')
        self.assertEqual(s.tax, 5)
        self.assertEqual(s.prod, 5)
        self.assertEqual(s.man, 3)
        self.assertEqual(s.trade, 'grain')
        self.assertFalse(s.hre)
        self.assertEqual(s.claims, [])
        self.assertEqual(s.visible, ['eastern', 'western', 'muslim', 'ottoman'])
        #print('stock', self.stockholm)

    def test_applied_history(self):
        pass
    def test_wasteland(self): pass
    def test_history(self): pass


if __name__ == '__main__':
    # Has to be run on an installation with EU4 installed
    unittest.main()