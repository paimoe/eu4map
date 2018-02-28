import json

from parsers.base import DataParser_save, DataParser

class ReligionParser(DataParser_save):
    """
    Parse religions, used for UI, Country, Province
    """
    output = 'output/_religions.json'
    data = {}

    def __init__(self, test=False):
        super().__init__(test=test)

        self.religions = self.gamefilepath('common/religions/00_religion.txt')

    def parse_all(self, one=None): 
        self.cs.start()

        with open(self.religions, 'r') as fc:
            read = fc.read()
        parsed = self.oneline(read, makelistkeys=['flag_emblem_index_range', 'color', 'heretic', 'aspects'])

        # Parse formables
        #savedata = { x:d for x,d in self.data.items() }

        # Ignore some keys for now, like papal actions/fervor etc

        self.save(parsed)

        # Group up
        ignore = ['religious_schools']
        compiled = {}
        for gname, rel in parsed.items():
            subkeys = [ (sub, sub) for sub in rel.keys() if isinstance(rel[sub], dict) and sub not in ignore ]
            subkeys = sorted(list(map(self.clean_name, subkeys)))

            compiled[ self.clean_name(gname) ] = subkeys

        self.save_data('religions', compiled)

        return parsed

    def clean_name(self, s):
        if isinstance(s, tuple):
            return (s[0].partition('_')[0].capitalize(), s[1])
        else:
            return s.partition('_')[0].capitalize()