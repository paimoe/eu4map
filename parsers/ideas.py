import json

from parsers.base import DataParser

class IdeaParser(DataParser):
    """
    Get Ideas

    Mainly just used in CountryParser to append

    @todo: probably need to keep the ideas in order
    @todo: finish (duh)
    """
    output = 'output/_ideas.json'
    data = {}

    def __init__(self, test=False, **kwargs):
        super().__init__(test=test, **kwargs)

        self.nationals = self.gamefilepath('common/ideas/00_country_ideas.txt')
        self.groups = self.gamefilepath('common/ideas/zz_group_ideas.txt')
        self.defaults = self.gamefilepath('common/ideas/zzz_default_idea.txt')

    def parse_all(self): 
        self.cs.start()

        # Get nats
        with open(self.nationals, 'r') as fc:
            read = fc.read()

        self.ideasnational = dict(self.oneline(read))
        #print(parsed['ENG_ideas'])

        # Group ideas, based on culture? I think
        with open(self.groups, 'r') as gc:
            read = gc.read()
        self.ideasgroup = dict(self.oneline(read))
        #self.get_ideas(1)
        #print(self.ideasgroup)
        with open(self.defaults, 'r') as dc:
            read = dc.read()
        self.ideasdefault = dict(self.oneline(read))
        
        #self.save()

    def get_ideas(self, c):
        # Passed in country, so check things like gov type, culture, to find the idea set
        # todo: check for religion in national idea set, under trigger{ tag = X and religion = X}
        #nattag = '{0}_ideas'.format(c.tag)
        for _, block in self.ideasnational.items():
            trig = block['trigger']
            #print(trig)
            if 'tag' in trig:
                if trig['tag'] == c.tag:
                    return ('national', block)
            if 'OR' in trig:
                #print(trig['OR'])
                try:
                    if c.tag in trig['OR']['tag']:
                        return ('national', block)
                except KeyError:
                    if c.tag in trig['OR']['TAG']:
                        return ('national', block)
        """
        groups
        - primary_culture, religion_group, religion, government, culture_group, tag
        """
        for _, block in self.ideasgroup.items():
            trig = block['trigger']
            #print(trig)

        # Check culture? or trigger
        # Parse generics
        return ('generic', self.ideasdefault['default_ideas'])
        #print(self.ideasdefault)

    def check_condition(self, c, key, value):

        if key == 'tag':
            check = c.tag
        elif key == 'primary_culture':
            check = c.culture
        elif key == 'culture_group':
            return True
            pass
        elif key == 'religion':
            check = c.religion
        elif key == 'religion_group':
            return True
            pass
        elif key == 'government':
            check = c.government
        
        if isinstance(value, list):
            return check in value
        else:
            return check == value

    def save(self):
        #self.cs.save('ideas', self.data)
            
        dump = { x: d for x, d in self.data.items() }
        
        # call _asdict()
        with open(self.output, 'w') as f:
            f.write(json.dumps(dump))