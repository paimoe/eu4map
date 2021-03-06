from parsers.base import DataParser_save, DataParser
import json, os, re, datetime,pprint
import namedlist

import pandas as pd

from .tradenodes import TradenodeParser
from .areas_regions import RegionsParser

import constants, renames,sys

class ProvinceParser(DataParser_save):

    output = 'output/provdata.json'
    namesrc = 'sources/definition.csv'

    def __init__(self, test=False):
        super().__init__(test=test)
        self.provinces = self.gamefilepath('history/provinces')
        self.provincesmore = self.gamefilepath('history/')
        #self.terrain = self.gamefilepath('map/terrain.txt') Get terrain and add to province info
        
        # now acquiesce other parts
        if not os.path.exists(self.namesrc):
            raise FileNotFoundError('Could not find definition.csv, put it in sources/')

    @staticmethod
    def container():
        # Set up container
        fields = ('id', 'name', 'owner', 'controller', 'cores', 'culture', 'religion', 
            'tax', 'prod', 'man', 'trade', 'hre', 'claims', 'visible', 'area', 'sea', 'ocean', 'lake', 'wasteland',
            'history', 'tradenode', 'tile')
        nlistfields = []
        # Set types of specifics
        for n in fields:
            # pick default
            if n in ('cores', 'claims', 'visible','history'):
                t = []
            elif n in ('id',):
                t = 0
            elif n in ('sea', 'ocean', 'wasteland', 'lake'):
                t = False
            elif n in ('tradenode','tile'):
                t = {}
            else:
                t = None
            nlistfields.append((n, t)) # Set up defaults for namedlist

        return namedlist.namedlist('Province', nlistfields)() # create

    def parse_all(self, from_fresh=False, one=None, internal=False):
        tp = TradenodeParser(test=True, internal=True)
        tp.parse_all()

        areasParser = RegionsParser()
        areas = areasParser.parse_all(return_province_data=True)

        if one is not None:
            if not isinstance(one, list):
                one = [int(one)]

        self.allprovinces = {}
        self.areas = self.parse_areas()
        self.lakes = self.parse_water()

        keep_copy = None

        for root, dirs, files in os.walk(self.provinces):
            files = sorted(files, key=lambda x: self.first_nums(x))
            for f in files:
                if f.endswith('txt'):
                    if one is None or (one is not None and self.first_nums(f) in one):
                        #print('checking ', f)

                        # Hold onto this to mirror it below
                        if self.first_nums(f) == 1797:
                            keep_copy = os.path.join(root, f)

                        c = self.parse(os.path.join(root, f))
                        c = self.set_special(c)

                        # Get trade node
                        c.tradenode['name'] = tp.belongs_to(c.id) # color is in the tradenodes datafile
                        c.tradenode['main'] = tp.is_main(c.id)

                        if c.id in areas:
                            c.tile = areas[c.id]

                        self.allprovinces[int(c.id)] = c

        # Nothing for: Central Africa [1796], Western Australia [1790], Central Australia [1791]
        # So just copy from another wasteland?
        if one is None:
            fake_names = {1796: 'Central Africa', 1790: 'Western Australia', 1791: 'Central Australia'}
            for i, name in fake_names.items():
                c = self.parse(keep_copy)
                c.id = i
                c.name = name
                c = self.set_special(c)
                # wasteland so ignore trade node
                self.allprovinces[i] = c

        # Also get other parts
        # Get province name
        df = pd.read_csv(self.namesrc, sep=';', encoding='latin-1')

        for index, row in df.iterrows():
            try:
                c = self.allprovinces[row['province']]
            except KeyError:
                continue

            c.name = str(row['x'])

            self.allprovinces[row['province']] = c
        
        dump = { d.id: d._asdict() for x, d in self.allprovinces.items() }

        self.save(dump)  

        return self.allprovinces

    def parse(self, fname):
        # pid 
        pid = self.first_nums(os.path.basename(fname))

        prov = self.container()
        prov.id = pid

        with open(fname, 'r', encoding='latin-1') as fc:
            read = fc.read()

        parsed = self.oneline(read)
        
        for pline in parsed.items():
            k, v = pline
            #print(pline)

            #convert lastkey to datetime if needed
            dtkey = self.match_date.search(k)
            #dtkey = self.dtre.search(k)
            if dtkey is not None:
                k = datetime.datetime(*list(map(int, dtkey.groups())))

            is_dt = isinstance(k, datetime.datetime)

            # Get ones that match the container field names
            if k in ('owner', 'controller', 'culture', 'hre',):
                setattr(prov, k, v)

            if k == 'add_core':
                if isinstance(v, list):
                    prov.cores.extend(v)
                else:
                    prov.cores.append(v)
            if k == 'add_claim':
                prov.claims.append(v)
            if k == 'discovered_by':
                if isinstance(v, list):
                    prov.visible = v
                else:
                    prov.visible.append(v)
            if k == 'hre':
                prov.hre = v
            if not is_dt:
                if k.startswith('base_'):
                    if k == 'base_tax':
                        prov.tax = v
                    if k == 'base_production':
                        prov.prod = v
                    if k == 'base_manpower':
                        prov.man = v
            if k == 'trade_goods':
                prov.trade = v
            if k == 'religion':
                if v in renames.RELIGIONS:
                    v = renames.RELIGIONS[v]
                prov.religion = v

            # Check through the history, apply any before our start date
            if is_dt:
                prov.history.append({ self.format_date(k): v })

        # sort history by datetime key
        prov.history.sort(key=lambda x: list(x.keys())[0])

        # Apply history
        for h in prov.history:
            k = list(h.keys())[0]
            v = h[k]
            if datetime.datetime.strptime(k, "%Y-%m-%d") <= self.min_dt:
                # Apply this
                #print('Applying history ', v)
                try:
                    v.items()
                except AttributeError:
                    # Fuck it
                    continue
                for act, val in v.items():
                    #print('av',act,val)
                    if act in ('owner', 'controller', 'culture', 'hre',):
                        setattr(prov, act, val)

                    if act == 'add_core':
                        prov.cores.append(val)
                        pass
                    if act == 'add_claim':
                        prov.claims.append(val)
                    if act == 'discovered_by':
                        prov.visible.append(val)
                    if act == 'hre':
                        prov.hre = val
                    if act == 'trade_goods':
                        prov.trade = val
                    if act == 'religion':
                        if val in renames.RELIGIONS:
                            val = renames.RELIGIONS[val]
                        prov.religion = val

        return prov

    def parse_areas(self):
        fname = self.gamefilepath('map/area.txt')

        with open(fname, 'r') as f:
            lines = f.readlines()

        # Remove comments to the end of the line or they mess with the regex
        noco = []
        for l in lines:
            if '#' in l:
                l = l.partition('#')[0]
            l = l.strip()
            if len(l) == 0 or l.startswith('color'):
                continue
            noco.append(l)

        # Removed all comments
        lines = "\n".join(noco)
        match = list(re.findall("(\w+)\s?\=\s?{\s?([\d\s]*?)\s?}", lines))

        # Breaks with newlines in the areas :(
        allareas = {}
        for m in match:
            # m is tuple (area_name, str_of_ids)
            area = m[0]
            ids = filter(None, m[1].split())
            allareas.update({ int(a): area for a in ids })

        return allareas

    def parse_water(self):
        fname = self.gamefilepath('map/default.map')
        with open(fname, 'r') as f:
            water = self.oneline(f.read())

        return {
            'lakes': water['lakes'],
            'seas': water['sea_starts']
        }

    def set_special(self, c):
        """
        Set ocean/sea/wasteland
        """
        if c.id in self.areas:
            c.area = self.areas[c.id]
        if c.id in constants.WASTELANDS:
            c.wasteland = True
        if c.id in self.lakes['seas']:
            c.ocean = True
        if c.id in self.lakes['lakes']:
            c.lake = True
        return c

    def terrain_type():
        pass