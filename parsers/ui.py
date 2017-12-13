import json

from parsers.base import DataParser

import mapfilters

class UIParser(DataParser):
    """
    General purpose UI parser
    - Collect religions and cultures, organise into groups
    - Collect achievement filter from constants.py
    """
    output = 'output/ui.json'
    data = {}

    def __init__(self):
        super().__init__()
        print('hello UIParser')

    def parse_all(self): 
        self.cs.start()

        # Parse religions
        rfile = self.gamefilepath('common/religions/00_religion.txt')

        # Parse cultures
        # ignore the names jesus
        cfile = self.gamefilepath('common/cultures/00_cultures.txt')

        # Parse trade nodes [or should that be under provinces?]

        # Parse map filters
        self.data['filters'] = mapfilters.FILTERS

        # Parse formables

        self.save()

    def save(self):
        #self.cs.save('ui', self.data)
            
        dump = { x: d for x, d in self.data.items() }
        
        # call _asdict()
        with open(self.output, 'w') as f:
            f.write(json.dumps(dump))