import json

from parsers.base import DataParser

class ReligionParser(DataParser):
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
        self.save(parsed)

        return parsed