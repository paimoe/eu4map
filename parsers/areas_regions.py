import json
import os, re

from parsers.base import DataParser_save

#from .provinces import ProvinceParser

class RegionsParser(DataParser_save):
    output = 'output/_regions.json'
    data = {}

    def __init__(self, test=False):
        super().__init__(test=test)

        self.superregion = self.gamefilepath('map/superregion.txt')
        self.region = self.gamefilepath('map/region.txt')
        self.continent = self.gamefilepath('map/continent.txt')
        self.terrain = self.gamefilepath('map/terrain.txt')

        # Get province ids
        self.provinces = self.gamefilepath('history/provinces')
        self.provids = []
        for root, dirs, files in os.walk(self.provinces):
            files = sorted(files, key=lambda x: self.first_nums(x))
            for f in files:
                if f.endswith('txt'):
                    self.provids.append(self.first_nums(f))

    def parse_areas(self):
        """Borrowed from province parser"""
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

    def parse_all(self, one=None, return_province_data=False): 
        self.cs.start()

        # Parse all
        s = self.oneline_path(self.superregion)
        #print(s)
        r = self.oneline_path(self.region)
        #print(r)
        c = self.oneline_path(self.continent)
        #print(c)
        t = self.oneline_path(self.terrain)['categories']
        #print(t)
        #print(self.provids)
        # compile supers
        ret_areas = {}
        for regname, areas in r.items():
            if 'areas' in areas:
                for a in areas['areas']:
                    ret_areas[a] = {
                        'r': regname
                    }
        for sname, sups in s.items():
            for sup in sups:
                for krets, loop_rets in ret_areas.items():
                    if loop_rets['r'] == sup:
                        # this is the thing? fuck
                        ret_areas[krets]['s'] = sname

        # cant get continent since its by province, same with terrain
        areas = self.parse_areas()
        #print(areas)
        ret_provs = {}
        for id in self.provids:
            ret_provs[id] = {}

            if id in areas:
                area = areas[id]
                ret_provs[id]['a'] = area
                ret_provs[id]['r'] = ret_areas[area]['r']
            else:
                area = None
                ret_provs[id]['a'] = None
                ret_provs[id]['r'] = None

            # Loop continents    
            ret_provs[id]['c'] = None
            for contname, contids in c.items():
                if id in contids:
                    ret_provs[id]['c'] = contname

            # Terrains (not all available)
            ret_provs[id]['t'] = None
            for tname, tobj in t.items():
                if 'terrain_override' in tobj:
                    if id in tobj['terrain_override']:
                        ret_provs[id]['t'] = tname
            #ret_provs[id]['t']

        # Return if return_province_data=True
        if return_province_data is True:
            return ret_provs

        """
        {
            'provid': {
                'c': continent,
                't': terrain,
                'a': area,
                'r': region
            }
        }
        """
        # Otherwise, save region info
        """
        { 
            'area': {
                'continent': x,
                'region': y,
                'superregion': z
                'color': a
            }
        }
        """
        self.save(ret_areas)

    def find_region(self, area): pass 
    def find_super(self, region): pass 
    #def find_continent(self, pid): pass