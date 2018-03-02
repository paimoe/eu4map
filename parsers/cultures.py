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
        
        for cgroup, c in o.items():
            print(cgroup)
        # Parse formables
        #savedata = { x:d for x,d in self.data.items() }
        savedata = {}
        #self.save(savedata)