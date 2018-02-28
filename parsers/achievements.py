import json

from parsers.base import DataParser_save

class AchievementParser(DataParser_save):
    """
    General purpose UI parser
    - Collect religions and cultures, organise into groups
    - Collect achievement filter from constants.py
    """
    output = 'output/achievements.json'
    data = {}

    def __init__(self, test=False):
        super().__init__(test=test)

        self.afile = self.gamefilepath('common/achievements.txt')

    def parse_all(self, one=None): 
        self.cs.start()

        with open(self.afile, 'r') as f:
            achdata = f.read()

        data = self.oneline(achdata)
        print(data)

        # Parse formables
        #savedata = { x:d for x,d in self.data.items() }
        savedata = {}
        self.save(data)