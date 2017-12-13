from parsers.base import DataParser
import json, os, re
import namedlist

from .ideas import IdeaParser

import constants, renames

class CountryParser(DataParser):

    dest = 'output/countries.json'

    def __init__(self):
        super().__init__()
        self.countries = self.gamefilepath('history/countries')
        self.colorsrc = self.gamefilepath('common/countries')

    @staticmethod
    def container():
        # Set up container
        fields = ('tag', 'name','capital', 'gov', 'govrank', 'ideas', 'color', 'culture', 'religion', 'techgroup', 'history', 'ideastype')
        nlistfields = []
        # Set types of specifics
        for n in fields:
            # pick default
            if n in ('history',):
                t = []
            elif n in ('capital',):
                t = 0
            elif n in ('ideas',):
                t = {}
            else:
                t = None
            nlistfields.append((n, t)) # Set up defaults for namedlist

        return namedlist.namedlist('Country', nlistfields)() # create

    def parse_all(self, from_fresh=False):
        self.allcountries = {}

        # get national ideas
        ideas = IdeaParser()
        ideas.parse_all()

        for root, dirs, files in os.walk(self.countries):            
            for f in files:
                if f.endswith('txt'):
                    c = self.parse(os.path.join(root, f))

                    i = ideas.get_ideas(c)
                    c.ideas = i[1]
                    c.ideastype = i[0]

                    self.allcountries[c.tag] = c

        # Also get other parts
        for root, dirs, files in os.walk(self.colorsrc):
            for f in files:
                if f.endswith('txt'):
                    # Match to current allcountries
                    fname = f[:-4]
                    # Fix up fucked up tags
                    for tag, c in self.allcountries.items():
                        name = c.name

                        if name in renames.MAP['common/countries']:
                            print('Renaming ', name)
                            name = renames.MAP['common/countries'][name]

                        if name == fname:
                            # Edit this one
                            newcolor = self.parse_color(os.path.join(root, f))
                            c.color = newcolor
                            self.allcountries[tag] = c

        # Get national ideas
        # First, get generic
        # Then override with regional specifics
        # Then override with national ideas

        # Vassals/subjects are in history/diplomacy, just take the ones that start 1444.1.1


        self.save()                    

    def parse(self, fname):
        c = self.container()

        # split fname
        c.tag, c.name = map(str.strip, os.path.basename(fname)[0:-4].split('-'))

        whitelist_starts = ('government', 'government_rank', 'primary_culture', 'religion', 'technology_group', 'capital')

        def parse_line(line):
            sp = line.split('=')
            try:
                return (sp[0].strip(), sp[1].strip())
            except IndexError:
                print(line, sp)
                raise

        with open(os.path.join(fname), 'r') as fc:
            for cnt, line in enumerate(fc):
                # 
                if line.startswith(whitelist_starts):
                    k, v = parse_line(line)
                    
                    if k == 'government':
                        c.gov = v
                    if k == 'government_rank':
                        c.govrank = v
                    if k == 'primary_culture':
                        c.culture = v
                    if k == 'religion':
                        c.religion = v
                    if k == 'technology_group':
                        c.techgroup = v
                    if k == 'capital':
                        c.capital = self.first_nums(v)
        return c

    def parse_color(self, fname):
        with open(fname, 'r') as f:
            for cnt, line in enumerate(f):
                if line.startswith('color'):
                    match = list(map(int, re.findall("(\d+)", line)))
                    return self.rgb_to_hex(*match)

    def save(self):
        dump = { x: d._asdict() for x, d in self.allcountries.items() }
        
        # call _asdict()
        #print(dump)
        #return
        with open(self.dest, 'w') as f:
            f.write(json.dumps(dump))