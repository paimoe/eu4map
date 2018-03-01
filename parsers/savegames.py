import json, os, re

from collections import OrderedDict

from parsers.base import DataParser_save

from .units import UnitsParser

class SavegameParser(DataParser_save):
    """
    Parse save game files into a useable format
    """
    output = 'output/save.json'
    data = {}

    FULL = False

    def __init__(self, test=False):
        super().__init__(test=test)

        # Need some info
        self.units = UnitsParser(internal=True).parse_all()

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

            #print('COUNT BRACES')
            #print(savefile.count('}'))

            # All collectibles in a save file
            # should have discovered_by, but we also have like history { discovered_by=western, discovered_by=east }, so some history events have lost that
            # NEED: ability to set these listkeys as a child of something, so eg only 'X' if its inside a block of 'Y', rather than global
            #collect = ['dlc_enabled','setgameplayoptions', 'id_counters', 'institutions', 'institution_origins', 'friend_bools', 'produced_goods_value', 'num_of_goods_produced', 'traded',
            #'num_of_leaders', 'num_of_leaders_with_traits', 'num_of_free_leaders', 'border_provinces', 'neighbours', 'home_neighbours', 'core_neighbours', 'score_rating', 'score_rank', 'age_score',
            #'inflation_history', 'opinion_cache', 'under_construction', 'under_construction_queued', 'total_count', 'owned_provinces', 'controlled_provinces', 'core_provinces',
            #'idea_may_cache', 'income', 'expense', 'lastmonthincometable', 'lastmonthexpensetable', 'totalexpensetable', 'lastyearincome', 'lastyearexpense', 'active_loyalties', 'active_influences',
            #'changed_country_mapcolor_from', 'map_color', 'country_color', 'powers', 'members', 'mothballed_forts',
            #'electors'] + ['attackers', 'defenders', 'persistent_attackers', 'persistent_defenders']

            # Cleanup for mangled parts
            #fixparts = {'map_area_data {': 'map_area_data = {'}

            # Don't combine these
            #seperate = {
            #    'active_war': ['participants', 'attackers', 'history']
            #}

            #skip=['EU4txt', 'rebel_faction']

            #o = self.oneline(savefile, skip=['EU4txt'], makelistkeys=collect, fixparts=fixparts, seperate2=['active_war'])#, seperate=seperate)
            o = self.oneline(savefile)

            #pprint.pprint(aw)
            #print(o['b'])
        else:
            # Load from cache
            print('From cache')
            with open(self.output, 'r') as f:
                o = json.loads(f.read())
        
        # Optimize, remove bits we'll never use or don't use currently
        # Basically generate what we need via a whitelist
        data = self.apply_whitelist(o)

        #return o
        if self.FULL and not test_save_url.endswith('test.eu4'):
            self.save(o)

    def apply_whitelist(self, d):
        """
        Almost definitely don't want:
        - active_advisors
        """
        save = {}

        # Copy basic keys
        basic = ['current_age', 'player', 'date', 'checksum', 'speed', 'start_date', 'displayed_country_name', 'savegame_version', 'flags', 'empire', 'great_powers',
        'celestial_empire', 'active_war', 'institutions', 'institution_origin', 'campaign_id']
        for k in basic:
            save[k] = d[k]

        # Countries
        cnts = { k:v for k, v in d['countries'].items() if self.no_nums(k) } # Remove any rebel states

        clean_countries = {}
        easy_fields = ['treasury', 'realm_development=dev', 'legitimacy', 'capital', 'mercantilism', 'prestige','num_of_total_ports=ports','manpower',
            'enemy','neighbours','army_tradition','num_of_cities', 'stability','primary_culture','institutions','government','religion','colors',
            'active_idea_groups', 'rival','trade_port',]
        for tag, c in cnts.items():
            ap = {}

            # Copy over fields verbatim
            for field in easy_fields:
                sp = field.partition('=')
                kname = sp[0]
                if sp[1] == '=':
                    # Do we need to rename
                    kname = sp[2]

                try:
                    ap[kname] = c[sp[0]]
                except KeyError:
                    ap[kname] = None
            
            # Compile some
            tech = c['technology']
            ap['tech'] = {
                'adm': tech['adm_tech'],
                'dip': tech['dip_tech'],
                'mil': tech['mil_tech'],
                'sum': tech['adm_tech'] + tech['dip_tech'] + tech['mil_tech'],
                'group': c.get('technology_group', None),
                # Tech penalty? thought i saw it
                'penalty': c.get('technology_cost', 0)
            }
            ap['tech']['str'] = '{0} ({1}/{2}/{3})'.format(ap['tech']['sum'], ap['tech']['adm'], ap['tech']['dip'], ap['tech']['mil'])

            if isinstance(c.get('government'), dict):
                gov = c['government'].get('government', None)
            else:
                gov = None
            ap['government'] = {
                'name': gov,
                'rank': c.get('government_rank', None)
            }

            # Army
            units = {'inf': 0, 'cav': 0, 'art': 0}
            ap['army'] = {
                'total': units,
                'groups': c.get('army', []),
                'tradition': c.get('army_tradition', 0),
                'maintenance': c.get('land_maintenance', 0)
            }
            try:
                if not isinstance(c['army'], list):
                    c['army'] = [c['army']]
                for reg in c['army']:
                    #print('reg', reg)
                    for r in reg['regiment']:
                        if isinstance(r, dict):
                            # 
                            t = self.units['army'][ r['type'] ]['type'][0:3] # Get the type 'indian_footsoldier', ref the units array to get its type 'infantry'
                            units[t] += 1

                ap['army']['total'] = units
            except KeyError:
                # No army?
                pass

            # Navy

            # CBs
            ap['cbs'] = []
            for cb in d['diplomacy']['casus_belli']:
                if cb['first'] == tag:
                    ap['cbs'].append(cb)

            # Diplomacy/subjects
            ap['is_subject'] = False
            ap['subjects'] = []
            for dep in d['diplomacy']['dependency']:
                if dep['first'] == tag:
                    ap['subjects'].append(dep)
                if dep['second'] == tag:
                    ap['is_subject'] = dep

            ap['diplo'] = {}
            for t, obj in d['diplomacy'].items():
                if t not in ['dependency', 'casus_belli']:
                    for o in obj:
                        if o['first'] == tag:
                            ap['diplo'].setdefault(t, []).append(o)


            clean_countries[tag] = ap
        save['countries'] = clean_countries

        #print(save['countries']['VIJ'])
        #assert False
        # Diplomacy/alliances
        save['diplomacy'] = d['diplomacy']
        save['great_powers'] = d['great_powers']

        # Clean provinces
        """
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
        """
        # Fix active wars. Since the list is [a,b,c,[d,e,f],[g,h,i]] and we want to group the first/non-list elements
        """
        for i, war in enumerate(save['active_war']):
            members = war['participants']['losses']['members']
            firstgroup = [ x for x in members if not isinstance(x, list) ]
            alreadygrouped = list(filter(lambda x: isinstance(x, list), members))
            alreadygrouped.insert(0, firstgroup)
            members = alreadygrouped
            save['active_war'][i]['participants']['losses']['members'] = members
        """
        # zip institutions info together institions,inst_origin, inst_penalties
        save['institutions'] = list(zip(d['institutions'], d['institution_origin'], d['institutions_penalties'][0]))

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

    num_search = re.compile('\d')
    def no_nums(self, n):
        return not self.num_search.search(n)