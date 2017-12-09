from parsers.base import DataParser
import json, os, re, datetime
import namedlist

import pandas as pd

import constants, renames,sys

class ProvinceParser(DataParser):

    dest = 'output/provdata.json'
    namesrc = 'sources/definition.csv'

    def __init__(self):
        super().__init__()
        self.provinces = self.gamefilepath('history/provinces')
        self.provincesmore = self.gamefilepath('history/')
        
        # now acquiesce other parts
        if not os.path.exists(self.namesrc):
            raise FileNotFoundError('Could not find definition.csv, put it in sources/')

    @staticmethod
    def container():
        # Set up container
        fields = ('id', 'name', 'owner', 'controller', 'cores', 'culture', 'religion', 
            'tax', 'prod', 'man', 'trade', 'hre', 'claims', 'visible', 'area', 'sea', 'ocean', 'wasteland',
            'history')
        nlistfields = []
        # Set types of specifics
        for n in fields:
            # pick default
            if n in ('cores', 'claims', 'visible','history'):
                t = []
            elif n in ('id',):
                t = 0
            elif n in ('sea', 'ocean', 'wasteland'):
                t = False
            else:
                t = None
            nlistfields.append((n, t)) # Set up defaults for namedlist

        return namedlist.namedlist('Province', nlistfields)() # create

    def parse_all(self, from_fresh=False, one=False):
        self.allprovinces = {}
        self.areas = self.parse_areas()
        for root, dirs, files in os.walk(self.provinces):
            files = sorted(files, key=lambda x: self.first_nums(x))
            
            for f in files:
                if f.endswith('txt'):
                    if one is False or re.match('^{0}(\s|\-)+'.format(one), f) != None:
                        print('checking ', f)
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

    def parse_file_generator(self, fname):
        # open, create a generator
        with open(os.path.join(fname), 'r') as fc:
            # Get line
            braces = 0
            building = False
            build_multi = []
            for cnt, line in enumerate(fc):

                line = self.remove_comment_line(line.strip())
                
                # if we're building multiline, then just add this line and continue until we hit the last }
                # TODO: nested multi builds, basically just building a single line thing
                # TODO: quotes around some values, like dynasty = "von Habsburg"
                if building is True:
                    build_multi.append(line.replace(' = ', '='))
                    #print('BUILDING: ', build_multi)
                    if '}' not in line:
                        continue

                    if '}' in line:
                        braces -= line.count('}')
                        if braces == 0:
                            line = ' '.join(build_multi)
                            building = False
                            build_multi = []
                            braces = 0

                        else:
                            continue

                if line == '':
                    continue

                if '{' in line or line.endswith('}') or building is True:

                    # we opening a block
                    # check if its single line
                    if line.count('{') == line.count('}') and building is False:
                        # single line block
                        # Get first up to equals
                        d = line.split(' = ')
                        key = d.pop(0)
                        #print('ass',key, '='.join(d))
                        rest = '='.join(d)

                        # convert key to dt?
                        dtkey = re.search("(\d{4})\.(\d+)\.(\d+)", key)
                        if dtkey is not None:
                            key = datetime.datetime(*list(map(int, dtkey.groups())))


                        z = (key, self.parse_line_block(rest)['obj'])
                        #print('zzzzz', z)
                        yield z
                    else:
                        # begin mulitline
                        braces += line.count('{') - line.count('}')
                        #print('braces', braces)
                        building = True
                        build_multi.append(line)
                        continue
                else:
                    sp = line.split('=')
                    #print(sp)
                    try:
                        yield (sp[0].strip(), sp[1].strip())
                    except IndexError:
                        yield line

    def parse(self, fname):
        # pid 
        pid = self.first_nums(os.path.basename(fname))

        prov = self.container()
        prov.id = pid

        def set_val(prov, key, val):

            return prov

        for pline in self.parse_file_generator(fname):
            k, v = pline

            is_dt = isinstance(k, datetime.datetime)

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

            # Check through the history
            if is_dt:
                prov.history.append({ self.format_date(k): v })
                if k <= self.min_dt:
                    # Apply this
                    #print('Applying history ', v)
                    for act, val in v.items():
                        #print(act,val)
                        if act in ('owner', 'controller', 'culture', 'religion', 'hre',):
                            setattr(prov, act, val)

                        if act == 'add_core':
                            prov.cores.append(val)
                        if act == 'add_claim':
                            prov.claims.append(val)
                        if act == 'discovered_by':
                            prov.visible.append(val)
                        if act == 'hre':
                            prov.hre = True if val == 'yes' else False
                        if act == 'trade_goods':
                            prov.trade = val


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
        #print(json.dumps(dump))
        #return
        # call _asdict()
        with open(self.dest, 'w') as f:
            f.write(json.dumps(dump))