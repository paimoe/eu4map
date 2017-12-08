#
"""
Usage
- python eu4map.py svg - convert exported svg from map_parser/ into a json array of paths
- python eu4map.py province - create json holding the province data, linked by province id
- python eu4map.py country - create json of countries, names/colors etc

TODO:
- make better duh
- classes, caches, etc
- timings
- document json formats
- able to target single/matched provinces/countries (100-200, all french, etc)
- combine eu4map.json (paths) and provdata.json?
"""

# convert eu4 stuff to svg
from xml.dom import minidom
import json, os, sys, itertools
import hashlib, datetime

import pandas as pd
import namedlist
import re

from parsers import *
import constants, renames

# Get path to Eu4 folder so we don't have to move anything
# auto-detect later
assert os.path.exists(EU4_PATH)
assert os.path.exists(os.path.join(EU4_PATH, 'eu4.exe'))

def rgb_to_hex(red, green, blue):
    """Return color as #rrggbb for the given color values."""
    return '%02x%02x%02x' % (red, green, blue)
def hex_to_rgb(hx):
    hx = hx.lstrip('#')
    return tuple(int(hx[i:i+2], 16) for i in (0, 2 ,4))

"""
class SVGParser(DataParser):

    src = 'map6.svg'
    dest = 'eu4map.json'

    def __init__(self):
        pass

    def parse(self):
        pass

    def save(self):
        pass
"""

def generate_svg_json():
    src = 'sources/output.svg'
    dest = 'output/eu4map.json'

    cs = Checksum()

    doc = minidom.parse(src)

    # load definitions, so we can also add the provid
    df = pd.read_csv('sources/definition.csv', sep=';', encoding='latin-1')

    ps = []
    for g in doc.getElementsByTagName('g'):
        if g.hasAttribute('fill'):
            fill = g.getAttribute('fill')[0:]
            rgb = hex_to_rgb(fill)
            prov = df[(df.red == rgb[0]) & (df.green == rgb[1]) & (df.blue == rgb[2])]

            if prov.empty:
                # Couldn't find it in definitions
                print('ERROR')
                print('Could not find hex {0} with rgb {1}'.format(fill, rgb))
                continue

            # Get paths this applies to
            for child in g.childNodes:
                if child.nodeName == 'path':
                    d = child.getAttribute('d')
                    # change the initial move to divide by 10 since its too big for some reason, work on the svg output @todo
                    """
                    m = d.split(' ')

                    if m[0][0] == 'M':
                        m[0] = 'M{0}'.format(int(m[0][1:]) / 10)
                        m[1] = str(int(m[1]) / 10)
                        d = ' '.join(m)

                        print(m, d)
                        #sys.exit()
                    else:
                        rel = list(map(lambda x: str(int(x)/10), m[1].split(',')))
                        #print(rel)
                        m[1] = ','.join(rel)
                        d = ' '.join(m)
                    """
                    ps.append({
                        'd': d,
                        'hex': fill,
                        'id': str(prov.iloc[0].province),
                        # maybe don't need yet
                        'n': prov.iloc[0].x,
                    })

    print('len', len(ps))

    print(ps[0])
    # save paths to hopefully cleaner json
    # fudge hash func, or it mixes up dict
    cs.save('map', ps)
    with open(dest, 'w') as f:
        f.write(json.dumps(ps))

def first_nums(x):
    return int("".join(itertools.takewhile(str.isdigit, x)))

class ProvinceParser(DataParser):

    dest = 'output/provdata.json'
    namesrc = 'sources/definition.csv'

    def __init__(self):
        self.provinces = gamefilepath('history/provinces')
        self.provincesmore = gamefilepath('history/')
        
        # now acquiesce other parts
        if not os.path.exists(self.namesrc):
            raise FileNotFoundError('Could not find definition.csv, put it in sources/')

    @staticmethod
    def container():
        # Set up container
        fields = ('id', 'name', 'owner', 'controller', 'cores', 'culture', 'religion', 
            'tax', 'prod', 'man', 'trade', 'hre', 'claims', 'visible', 'area', 'sea', 'ocean', 'wasteland')
        nlistfields = []
        # Set types of specifics
        for n in fields:
            # pick default
            if n in ('cores', 'claims', 'visible'):
                t = []
            elif n in ('id',):
                t = 0
            elif n in ('sea', 'ocean', 'wasteland'):
                t = False
            else:
                t = None
            nlistfields.append((n, t)) # Set up defaults for namedlist

        return namedlist.namedlist('Province', nlistfields)() # create

    def parse_all(self, from_fresh=False):
        self.allprovinces = {}
        self.areas = self.parse_areas()
        for root, dirs, files in os.walk(self.provinces):
            files = sorted(files, key=lambda x: first_nums(x))
            
            for f in files:
                if f.endswith('txt'):
                    c = self.parse(os.path.join(root, f))

                    c = self.set_special(c)

                    self.allprovinces[int(c.id)] = c

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

        self.save()  

    def remove_comment_line(self, l):
        if '#' in l:
            l = l.partition('#')[0]
        l = l.strip()
        return l

    def parse(self, fname):
        # pid 
        pid = first_nums(os.path.basename(fname))

        prov = self.container()
        prov.id = pid

        def parse_line(line):
            sp = line.split('=')
            try:
                return (sp[0].strip(), sp[1].strip())
            except IndexError:
                print(line, sp)
                raise

        with open(os.path.join(fname), 'r') as fc:
            #skip = False
            for cnt, line in enumerate(fc):
                fullline = line

                # for now, ignore the date lines
                line = self.remove_comment_line(line)
                if line.strip() == '' or line.strip().startswith(('#', "\t", "}")):
                    continue

                """
                # when do we end skip
                if skip is True:
                    print('skip is true')
                if line.strip() == '}':
                    skip = False
                    continue
                """
                line = line.strip()
                k, v = parse_line(line)
                """
                #print(k)
                if re.match('^[\d+\.]+\s?={1}\s?{', line) != None:
                    # Start of a dateline
                    if line.strip() == fullline.strip() and not line.strip().endswith('}'):
                        print('only a date opener, skipping')
                        skip = True
                        continue
                """
                # Ignore until we make a general file parser
                if re.match('^[\d+\.]+\s?={1}\s?{', line) != None:
                    break

                # Get ones that match the container field names
                if k in ('owner', 'controller', 'culture', 'religion', 'hre',):
                    setattr(prov, k, v)

                if k == 'add_core':
                    prov.cores.append(v)
                if k == 'add_claim':
                    prov.claims.append(v)
                if k == 'discovered_by':
                    prov.visible.append(v)
                if k == 'hre':
                    prov.hre = True if v == 'yes' else False
                if k.startswith('base_'):
                    if k == 'base_tax':
                        prov.tax = v
                    if k == 'base_production':
                        prov.prod = v
                    if k == 'base_manpower':
                        prov.man = v
                if k == 'trade_goods':
                    prov.trade = v

        return prov

    def parse_areas(self):
        fname = gamefilepath('map/area.txt')

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
        match = list(re.findall("(\w+)\s?\=\s?{\s?(.+)\s?}", lines))

        allareas = {}
        for m in match:
            # m is tuple (area_name, str_of_ids)
            area = m[0]
            ids = filter(None, m[1].split(' '))
            allareas.update({ int(a): area for a in ids })

        return allareas

    def set_special(self, c):
        """
        Set ocean/sea/wasteland
        """
        if c.id in self.areas:
            c.area = self.areas[c.id]

        if c.id in constants.WASTELANDS:
            c.wasteland = True
        if c.area in constants.SEAS:
            c.ocean = True
        return c
    
    def save(self):
        # sort allprovinces by id for convenience
        provs = self.allprovinces

        dump = { d.id: d._asdict() for x, d in provs.items() }
        
        # call _asdict()
        with open(self.dest, 'w') as f:
            f.write(json.dumps(dump))

class UIParser(DataParser):
    """
    General purpose UI parser
    - Collect religions and cultures, organise into groups
    - Collect achievement filter from constants.py
    """
    def __init__(self):
        pass
    def parse_all(self): pass
    def save(self):
        pass

if __name__ == '__main__':
    choice = sys.argv[1]
    if choice == 'svg':
        generate_svg_json()
    elif choice == 'province':
        pp = ProvinceParser()
        pp.parse_all()
    elif choice == 'country':
        cp = CountryParser()
        cp.parse_all()
    elif choice == 'check':
        print(os.path.exists(os.path.join(EU4_PATH, 'eu4.exe')))
        print(EU4_PATH)
    else:
        print('No choice selected')
    print('Done')