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
import json, os, sys, itertools, argparse
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
from pprint import pprint
class GeneralParser(DataParser):
    def __init__(self):
        super().__init__()
    def parse(self, fname):
        with open(self.gamefilepath(fname), 'r') as fc:
            read = fc.read()

        parsed = self.oneline(read, toplist=True)
        pprint(parsed)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='EU4 Map Generators', prog='eu4map')
    parser.add_argument('action', nargs='?', help='What action to perform (svg, province, country, ui, etc)')
    parser.add_argument('focus', nargs='?', help='Depends on action, province ID, country tag, to limit to test')

    parser.add_argument('--test', action='store_true', help='Don\'t save to file, just output')
    
    opts = parser.parse_args()

    # loaders
    loaders = ['province', 'country', 'religion', 'tradenode', 'achievement']

    if opts.action in loaders:
        p = eval("{0}Parser()".format(opts.action.capitalize()))
        p.test = opts.test
        p.parse_all(one=opts.focus)
    elif opts.action == 'svg':
        generate_svg_json()
    elif opts.action == 'ui':
        up = UIParser()
        up.parse_all()
    elif opts.action == 'css':
        print('CSS Parser')
    elif opts.action == 'all':
        pass
    elif opts.action == 'save':
        sp = SavegameParser()
        sp.parse()

    elif opts.action == 'check':
        print(os.path.exists(os.path.join(EU4_PATH, 'eu4.exe')))
        print(EU4_PATH)
    else:
        gp = GeneralParser()
        #gp.parse('history/diplomacy/British_alliances.txt')
        print('No choice selected')
    print('Done')