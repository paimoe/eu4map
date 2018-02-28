import json

from parsers.base import DataParser_save
import pprint
class TradenodeParser(DataParser_save):
    """
    
    """
    output = 'output/tradenodes.json'
    data = {}

    def __init__(self, test=False, **kwargs):
        super().__init__(test=test, **kwargs)

        self.nodes = self.gamefilepath('common/tradenodes/00_tradenodes.txt')

        self.internal = kwargs.get('internal', False)

    def parse_all(self, one=None): 
        self.cs.start()

        with open(self.nodes, 'r') as fc:
            read = fc.read()
        self.data = self.oneline(read)

        if one is not None:
            return self.data[one]

        # Used in provinceparser to allocate each province to a trade node

        # replace some colors cause they don't exist in the thing
        # taken from: https://eu4.paradoxwikis.com/Trade_nodes
        # https://eu4.paradoxwikis.com/images/f/f7/Trade_nodes_with_arrows.png
        replacements = {
            'aleppo': [120,148,140]
        }

        # only save the name
        if not self.internal:
            self.save(self.data)

        return self.data

    def belongs_to(self, pid):
        for name, node in self.data.items():
            if pid in node['members']:
                return name

    def is_main(self, pid):
        for name, node in self.data.items():
            if pid == node['location']:
                return True
        return False