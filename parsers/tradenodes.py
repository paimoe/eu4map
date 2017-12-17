import json

from parsers.base import DataParser
import pprint
class TradenodeParser(DataParser):
    """
    
    """
    output = 'output/tradenodes.json'
    data = {}

    def __init__(self, test=False, **kwargs):
        super().__init__(test=test, **kwargs)
        #raise Exception('Dont use tradenodes yet, todo: finish the oneline(separate=[]) part')
        self.nodes = self.gamefilepath('common/tradenodes/00_tradenodes.txt')

        self.internal = kwargs.get('internal', False)

    def parse_all(self, one=None): 
        self.cs.start()

        with open(self.nodes, 'r') as fc:
            read = fc.read()
        self.data = self.oneline(read, makelistkeys=['path', 'color', 'control', 'members'], seperate={'outgoing': ['name', 'path', 'control']})

        if one is not None:
            return self.data[one]

        # Used in provinceparser to allocate each province to a trade node

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