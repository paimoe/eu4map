import json, os

from parsers.base import DataParser_save

class UnitsParser(DataParser_save):
    """
    General purpose UI parser
    """
    output = 'output/units.json'
    data = {}

    def __init__(self, test=False, **kwargs):
        super().__init__(test=test, **kwargs)

        self.unitspath = self.gamefilepath('common/units')

    def parse_all(self, one=None): 
        """
        self.units = {
            'infantry':
        }
        """
        self.cs.start()

        self.units = {'army': {}, 'navy': {}}
        for root, dirs, files in os.walk(self.unitspath):
            for f in files:
                if f.endswith('txt'):
                    #print('checking ', f)
                    with open(os.path.join(root, f), 'r', encoding='latin-1') as file:
                        c = self.oneline(file.read())

                    fname = f.partition('.')[0]
                    if c['type'] in ['infantry', 'cavalry', 'artillery']:
                        self.units['army'][fname] = {
                            'type': c['type'], # infantry, cavalry, artillery
                            'unit_type': c.get('unit_type', None),
                            'stats': {
                                'm': c['maneuver'],
                                'om': c['offensive_morale'], 'dm': c['defensive_morale'],
                                'of': c['offensive_fire'], 'df': c['defensive_fire'],
                                'os': c['offensive_shock'], 'ds': c['defensive_shock']
                            }
                        }
                    else:
                        self.units['navy'][fname] = c        

        self.save(self.units)

        return self.units