import json

from parsers.base import DataParser

class ReligionParser(DataParser):
    """
    General purpose UI parser
    - Collect religions and cultures, organise into groups
    - Collect achievement filter from constants.py
    """
    output = 'output/_religions.json'
    data = {}

    def __init__(self, test=False):
        super().__init__(test=test)

        self.religions = self.gamefilepath('common/religions/00_religion.txt')

    def parse_all(self, one=None): 
        self.cs.start()

        

        # Parse formables
        #savedata = { x:d for x,d in self.data.items() }
        savedata = {}
        self.save(savedata)