import json

from parsers.base import DataParser_save
from pprint import pprint

import renames

CUSTOM = {
    
}

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
        #pprint(data)

        # Specify ones we can filter
        prepare = {}

        # Format it better for the info i want, like sometimes the country is under possible.tag, others its in happened.OR.tag etc
        lang = self.langs['en']['achievements'] # should be encoded by the thingy
        for ach in data:
            #pprint(ach)
            name = ach.replace('achievement_', '')
            dset = data[ach]
            prepare[name] = dset

            prepare[name]['keyname'] = name
            if name in lang:
                langkey = name
            elif 'the_{}'.format(name) in lang:
                langkey = 'the_' + name
            else:
                # Triple check
                # lazy match
                lazyname = [ key for key, value in lang.items() if name in key.lower() ]
                if len(lazyname) == 1:
                    # probably use this
                    langkey = lazyname[0]
                else:
                    # OTHERWISE, we go with manual matches
                    if name in renames.ACHIEVEMENT_KEYS:
                        langkey = renames.ACHIEVEMENT_KEYS[name]
                    else:
                        raise Exception('Unknown achievement: {}'.format(name))

            prepare[name]['name'] = lang[langkey]['name']
            prepare[name]['desc'] = lang[langkey]['desc']

            prepare[name]['needs_cores'] = 'owns_core_province' in dset['happened']
            prepare[name]['needs_control'] = 'owns' in dset['happened']
            prepare[name]['tag_for'] = dset['happened'].get('tag', None) # make this  alist

            prepare[name]['allowed'] = {}
            prepare[name]['allowed']['switch_nation'] = dset['allowed'].get('switch_nation', False) is True or dset['happened'].get('has_switched_nation', False) == False # ffs check

        # Parse formables
        self.save(prepare)
        #print(self.langs['en']['achievements']['better_than_napoleon'])

        #print(prepare['better_than_napoleon'])
        #print('UNUSED', TEST)
        print(prepare['around_the_world_in_eighty_years'])