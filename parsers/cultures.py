import json

from parsers.base import DataParser_save

class CultureParser(DataParser_save):
    """
    Just some uh in the data files
    """
    output = 'output/cultures.json'
    data = {}

    def __init__(self, test=False):
        super().__init__(test=test)

        self.cultures = self.gamefilepath('common/cultures/00_cultures.txt')

    def parse_all(self, one=None): 
        self.cs.start()

        with open(self.cultures, 'r', encoding='latin-1') as f:
            o = self.oneline(f.read())
        
        allgroups = {}
        for cgroup, c in o.items():
            cgroup = cgroup.replace('_', ' ').title()
            cultures = []
            for name, data in c.items():
                if name not in ['dynasty_names', 'graphical_culture', 'male_names', 'female_names']:
                    cultures.append(name)

            allgroups[cgroup] = cultures

        self.save_data('cultures', allgroups)