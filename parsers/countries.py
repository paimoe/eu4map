from parsers.base import DataParser, DataParser_save
import json, os, re
import namedlist

from .ideas import IdeaParser

import constants, renames

class CountryParser(DataParser_save):

    output = 'output/countries.json'

    def __init__(self, test=False):
        super().__init__(test=test)
        self.countries = self.gamefilepath('history/countries')
        self.colorsrc = self.gamefilepath('common/countries')

    @staticmethod
    def container():
        # Set up container
        fields = ('tag', 'name','capital', 'gov', 'govrank', 'ideas', 'color', 'culture', 'religion', 'techgroup', 'history', 'ideastype',
            'internal_name', 'provs', 'cores')
        nlistfields = []
        # Set types of specifics
        for n in fields:
            # pick default
            if n in ('history', 'provs', 'cores'):
                t = []
            elif n in ('capital',):
                t = 0
            elif n in ('ideas',):
                t = {}
            elif n in ('owns_land',):
                t = False
            else:
                t = None
            nlistfields.append((n, t)) # Set up defaults for namedlist

        return namedlist.namedlist('Country', nlistfields)() # create

    def parse_all(self, from_fresh=False, one=None):
        self.allcountries = {}

        # get national ideas
        ideas = IdeaParser(test=self.test)
        ideas.parse_all()

        # Check one

        for root, dirs, files in os.walk(self.countries):            
            for f in files:
                if f.endswith('txt'):
                    if one is not None:
                        # check tag
                        if not f.startswith(one):
                            continue

                    # Um try using the proper parser
                    with open(os.path.join(root, f), 'r', encoding='latin-1') as fopen:
                        fc = self.oneline(fopen.read())
                        c = self.parse(f, fc)

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
                        name = c.internal_name

                        # Checks for rename in other game files, but not the actual country
                        if name in renames.MAP['common/countries']:
                            name = renames.MAP['common/countries'][name]

                        if name == fname or c.name == fname:
                            # Edit this one
                            newcolor = self.parse_color(os.path.join(root, f))
                            c.color = newcolor

                        # Check user name of country, eg Zwahili - Swahili - Kilwa
                        if name in renames.NAMES:
                            c.internal_name = renames.NAMES[name] # hmmm

                        if c.religion in renames.RELIGIONS:
                            c.religion = renames.RELIGIONS[c.religion]

                        self.allcountries[tag] = c

        # Get national ideas
        # First, get generic
        # Then override with regional specifics
        # Then override with national ideas

        # Vassals/subjects are in history/diplomacy, just take the ones that start 1444.1.1
        # Copy subject stuff from savefile? nah can't idt
        # nah, should definitely make a save file day one, won't have all the info but should have at least diplomacy etc, existing alliances

        dump = { x: d._asdict() for x, d in self.allcountries.items() }

        self.save(dump)
        return self.allcountries

    def parse(self, fname, fdata):
        c = self.container()

        # split fname
        c.tag, c.internal_name = map(str.strip, os.path.basename(fname)[0:-4].split('-'))

        # Get country name based on tag
        try:
            c.name = self._('countries', c.tag, lang='en')
        except KeyError: 
            c.name = c.internal_name

        whitelist_starts = ('government', 'government_rank', 'primary_culture', 'religion', 'technology_group', 'capital')
        for key, v in fdata.items():
            if key in whitelist_starts:
                
                if key == 'government':
                    c.gov = v
                if key == 'government_rank':
                    c.govrank = v
                if key == 'primary_culture':
                    c.culture = v
                if key == 'religion':
                    c.religion = v
                if key == 'technology_group':
                    c.techgroup = v
                if key == 'capital':
                    c.capital = v
        return c

    def parse_color(self, fname):
        with open(fname, 'r', encoding='latin-1') as f:
            for cnt, line in enumerate(f):
                if line.startswith('color'):
                    match = list(map(int, re.findall("(\d+)", line)))
                    return self.rgb_to_hex(*match)
