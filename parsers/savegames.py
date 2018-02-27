import json, os

from collections import OrderedDict

from parsers.base import DataParser_save

class SavegameParser(DataParser_save):
    """
    Parse save game files into a useable format
    """
    output = 'output/save.json'
    data = {}

    FULL = True

    def __init__(self, test=False):
        super().__init__(test=test)

    # From REPL, to flatten dict
    def keyfinder(d):
        keylist = []
        for i, x in d.items():
            keylist.append(i)
            if isinstance(x, dict):
                keylist.append(keyfinder(x))
        return keylist

    def parse(self, one=None): 
        self.cs.start()

        if self.FULL:
            DIR = '/media/paimoe/3E3E95043E94B5FD/Documents and Settings/paimoe/Documents/Paradox Interactive/Europa Universalis IV/save games'
            test_save_url = os.path.join('sources', 'France1445_09_09.eu4') # Add browser maybe
            #test_save_url = os.path.join('sources', 'test.eu4') # Add browser maybe

            with open(test_save_url, 'r', encoding='latin-1') as f:
                savefile = f.read()

            print('COUNT BRACES')
            print(savefile.count('}'))

            # All collectibles in a save file
            # should have discovered_by, but we also have like history { discovered_by=western, discovered_by=east }, so some history events have lost that
            # NEED: ability to set these listkeys as a child of something, so eg only 'X' if its inside a block of 'Y', rather than global
            collect = ['dlc_enabled','setgameplayoptions', 'id_counters', 'institutions', 'institution_origins', 'friend_bools', 'produced_goods_value', 'num_of_goods_produced', 'traded',
            'num_of_leaders', 'num_of_leaders_with_traits', 'num_of_free_leaders', 'border_provinces', 'neighbours', 'home_neighbours', 'core_neighbours', 'score_rating', 'score_rank', 'age_score',
            'inflation_history', 'opinion_cache', 'under_construction', 'under_construction_queued', 'total_count', 'owned_provinces', 'controlled_provinces', 'core_provinces',
            'idea_may_cache', 'income', 'expense', 'lastmonthincometable', 'lastmonthexpensetable', 'totalexpensetable', 'lastyearincome', 'lastyearexpense', 'active_loyalties', 'active_influences',
            'changed_country_mapcolor_from', 'map_color', 'country_color', 'powers', 'members', 'mothballed_forts',
            'electors'] + ['attackers', 'defenders', 'persistent_attackers', 'persistent_defenders']

            # Cleanup for mangled parts
            fixparts = {'map_area_data {': 'map_area_data = {'}

            # Don't combine these
            seperate = {
                'active_war': ['participants', 'attackers', 'history']
            }

            skip=['EU4txt', 'rebel_faction']

            o = self.oneline(savefile, skip=['EU4txt'], makelistkeys=collect, fixparts=fixparts, seperate2=['active_war'])#, seperate=seperate)

            #pprint.pprint(aw)
            #print(o['b'])
        else:
            # Load from cache
            print('From cache')
            with open(self.output, 'r') as f:
                o = json.loads(f.read())

        # Optimize, remove bits we'll never use or don't use currently
        # Basically generate what we need via a whitelist
        #data = self.apply_whitelist(o)
        #return o
        if self.FULL and not test_save_url.endswith('test.eu4'):
            self.save(o)

    def select(self, d):
        save = {}

        # Copy basic keys
        basic = ['current_age', 'player', 'date', 'checksum', 'speed', 'start_date', 'displayed_country_name', 'savegame_version', 'flags', 'empire', 'great_powers',
        'celestial_empire', 'active_war']
        for k in basic:
            save[k] = d[k]

        # Player country

        # Diplomacy/alliances
        save['diplomacy'] = self.zip(d['diplomacy'])
        save['great_powers'] = self.zip(d['great_powers'])

        # Clean provinces
        provs = d['provinces']
        save['provinces'] = {}
        # Remove these. original_tax = dev, old base tax. Deal with history later since the parsing is whack anyway
        removals = ['history', 'patrol', 'original_tax', 'discovery_dates2', 'discovery_religion_dates2']
        for p in d['provinces']:
            pitem = d['provinces'][p]

            for r in removals:
                pitem.pop(r, None)

            save['provinces'][p[1:]] = pitem

        # Clean countries
        cnts = d['countries']
        save['countries'] = {}

        # Fix active wars. Since the list is [a,b,c,[d,e,f],[g,h,i]] and we want to group the first/non-list elements
        # Can't do fuckin previous_wars until we fix the parser UGH
        for i, war in enumerate(save['active_war']):
            members = war['participants']['losses']['members']
            firstgroup = [ x for x in members if not isinstance(x, list) ]
            alreadygrouped = list(filter(lambda x: isinstance(x, list), members))
            alreadygrouped.insert(0, firstgroup)
            members = alreadygrouped
            save['active_war'][i]['participants']['losses']['members'] = members

        if not self.FULL:
            with open('output/save_whitelisted.json', 'w') as f:
                f.write(json.dumps(save))

    def zip(self, obj):
        r = {}
        for key in obj.keys():
            sobj = sorted(obj[key].items())
            od = OrderedDict(sobj)
            r[key] = list(zip(*list(od.values())))
        return r
