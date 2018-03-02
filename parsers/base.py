import json, hashlib, datetime, os, itertools, re, collections, pprint, sys
from timeit import default_timer as timer

from decimal import Decimal

import yaml

# Temp fix for broken pipe when running `pipenv run python eu4map.py save | head -n 50`
# https://stackoverflow.com/a/30091579
#from signal import signal, SIGPIPE, SIG_DFL
#signal(SIGPIPE, SIG_DFL) 

EU4_PATH = 'B:\SteamLibrary\steamapps\common\Europa Universalis IV'
EU4_PATH = '/media/paimoe/New Volume/BigSteamLibrary/steamapps/common/Europa Universalis IV'

class Checksum(object):

    cfile = 'checksum.json'
    start_time = None
    end_time = None

    def __init__(self): 
        # Load checksum file
        with open(self.cfile, 'r') as f:
            self.data = json.loads(f.read())

        self.countries = self.data.get('countries', {})
        self.provinces = self.data.get('provinces', {})
        self.map = self.data.get('map', {})
        self.ui = self.data.get('ui', {})

    def start(self):
        # 
        self.start_time = timer()

    def save(self, key, data):
        self.end_time = timer()


        jstr = json.dumps(data, sort_keys=True).encode('utf-8')

        h = hashlib.md5(jstr).hexdigest()

        set_dict = {
            'hash': h,
            'len': len(data),
            'when': str(datetime.datetime.now()),
            'time': self.end_time - self.start_time
            }
        self.data[key].update(set_dict)

        with open(self.cfile, 'w') as f:
            f.write(json.dumps(self.data))

        print(set_dict)

class Builder(object):

    build_list_of_objects = False
    build_list_depth = 0
    build_list_key_template = None

    def __init__(self, seperate=None, **kwargs):
        self.keys = []
        self.depth = 0
        self.tree = []
        self.data = collections.defaultdict()

        self.splitter = 'xx__xx' # random value to split the string since we can't really use space, _ or .
        self.dtre = re.compile("(\d{4})\.(\d+)\.(\d+)")

        self.increments = {}
        sep2 = kwargs.get('seperate2', [])
        for s in sep2:
            self.increments[s] = collections.defaultdict()
        self.tmp_dic = collections.defaultdict()

        # Check for flags
        self.seperate = None
        self.sepname = ''
        self.sepvals = []
        if seperate is not None:
            self.seperate = seperate
            self.sepname = list(seperate.keys())[0] # get first key, we'll recombine on this [todo: allow for multiple if needed]
            self.sepvals = seperate[self.sepname]

    def nest(self, keys, value):
        dic = self.data
        lastkey = keys[-1]

        if self.build_list_key_template is not None:
            tkey = self.build_list_key_template

            if tkey not in self.increments:
                self.increments[tkey] = collections.defaultdict()

            #zz = None
            if keys[0] == tkey:
                zz = keys.pop(0)
            else:
                zz = tkey

            #print('new dic', self.tmp_dic, keys, value)
            #print('zz', tkey)
            dic = self.tmp_dic
            #if tkey.endswith('ers'):
            #    print('tkey', dic, value)
            #keys.insert(0, self.build_list_key_template.format(self.increments))
            #print(self.tmp_dic)
        #print('are we building?', self.build_list_of_objects)

        
        #print(keys[0], self.increments, keys[0] in self.increments)
        for key in keys[:-1]:
            #print('kkk',key)
            dic = dic.setdefault(key, {})

        try:
            # see if it exists, and convert to list if it does
            # if it doesn't exist, dic[lastkey] will hit exception
            if not isinstance(dic[lastkey], list):
                #print('setting ', dic[lastkey], ' to list')
                dic[lastkey] = [dic[lastkey]]

            dic[lastkey].append(value)

        except KeyError:
            # doesn't exist, so add it on
            # if we seperate, then yeah
            if lastkey in self.sepvals:
                # Check to ensure we don't combine these. they'll be split up in finalize()
                # make sure we make these lists of lists
                dic[lastkey] = [value]
            else:
                dic[lastkey] = value

    def add(self, k, v):
        # check if its a control block

        key = self.splitter.join(self.tree) + self.splitter + k
        if self.depth == 0:
            key = k

        """
        TODO: wtfffff
        maybe when we open a list, we just collect the str, then run self.oneline() on the accumulated when it ends?
        almost has to be a recursive function
        """

        #print('BUILDER:ADD', k, v)
        #print('depth', self.depth, self.build_list_depth, self.build_list_depth == self.depth)
        if self.build_list_of_objects is True and self.build_list_depth == self.depth:
            # Stop that
            #print('ENDING LIST OF OBJECTS', k, v)
            x = self.build_list_key_template
            self.build_list_of_objects = False
            self.build_list_key_template = None

            # Add our tmp_dic to self.increments?
            #print('tmp dic', self.increments[x])
            self.nest([x], self.tmp_dic)
            #self.nest([x], self.increments[x])

            self.tmp_dic = collections.defaultdict()
            #self.increments[x] = collections.defaultdict()
            self.build_list_of_objects = False
            self.build_list_key_template = None
        if k in self.increments:
            self.build_list_of_objects = True
            #print('BUILDING LIST OF OBJECTS', k, v)
            self.build_list_depth = self.depth
            self.build_list_key_template = key

        if isinstance(v, str):
            if v.startswith('CONTROL'):
                if v.endswith('CLOSEBLOCK'):
                    self.shallow()
                elif v.endswith('OPENBLOCK'):
                    self.deeper(k)
                return
        
        # convert value
        if not isinstance(v, list):
            dtkey = self.dtre.search(v)
            if dtkey is not None:
                v = datetime.datetime(*list(map(int, dtkey.groups())))
            elif v.isdigit():
                v = int(v)
            elif v in ['yes', 'no']:
                v = v == 'yes'

        # set nested dict
        b = self.nest(key.split(self.splitter), v)

    def deeper(self, k):
        self.tree.append(k)
        self.depth += 1

    def shallow(self):
        self.tree.pop()
        self.depth -= 1

    def finalize(self):
        #print(self.data)
        # if we're meant to seperate any, then loop through and split
        # we can assume the lists are in the correct order since we read the page vertically

        """
        - split into total blocks
        - find the key(s) that should be seperated. it'll be a dict with each key, and a list of values (including lists of lists)


        @todo: still bad, have to find a way to parse the blocks with multiple keys of the same name cleanly, since we rely on lu ck to match it up
        """
        #print('finalize', self.build_list_of_objects)
        if self.build_list_of_objects is True:
            # Wrap up this if it ends in a list building
            # ez
            self.add('__dummy__', '')

        #pprint.pprint(self.data)
        if self.seperate is not None:
            for _, block in self.data.items(): # eg for each trade node, split it out
                i = 0
                #print(block)
                newlist = []
                try:
                    obj = block[self.sepname]
                    #rint('LEN', obj['_len'])
                    #print('blockobj', obj, obj.items())
                    # loop through all items of this obj, and get the length, aka how many groups to split it into
                    seplen = 0
                    for _, x in obj.items():
                        if seplen == 0:
                            seplen = len(x)
                        else:
                            assert seplen == len(x)

                    while i < seplen:
                        newobj = {}
                        #k = self.sepvals[i]
                        #print(obj[k])

                        for k in self.sepvals:
                            #print('setting newobj[{0}] to obj[{0}][{1}]'.format(k, i))
                            newobj[k] = obj[k][i]
                        #print('our new obj', newobj)

                        i += 1
                        newlist.append(newobj)
                except KeyError: # some won't exist. eg tradenodes with no outgoing
                    pass
                except TypeError:
                    #print(_, block)
                    pass

                #print('new', newlist)

                # unset the big long lists, and set the new thing
                block[self.sepname] = newlist



        return self.data

class EU4JSON(json.JSONEncoder):
    def default(self, o):
        #print('oooo', o, type(o))
        if isinstance(o, Decimal):
            return str(o)

        if isinstance(o, (datetime.datetime, datetime.date)):
            #print('returning isoformat: ', o.isoformat())
            return o.isoformat()
        return super().default(o)

class DataParser_save(object): 

    cs = None
    test = False

    langs = {'en': {'countries': {}, 'provinces': {}}}

    def __init__(self, test=False, internal=False, **kwargs): 
        self.min_dt = datetime.datetime(1444, 11, 11)
        self.cs = Checksum()
        self.test = test
        self.internal = internal

        self.match_date = re.compile('(\d{4})\.(\d+)\.(\d+)')
        # Should match a list of numbers, including decimals and negatives
        self.match_num_list = re.compile('^[\s\d\.\-]+$')

        self.load_language('english')

    def load_language(self, l):
        # Probably just l for now
        if l != 'english':
            raise ValueError('Only english for now')

        def load_yaml(name):
            ldir = os.path.join(EU4_PATH, 'localisation')

            fullpath = os.path.join(ldir, name)
            if os.path.exists(fullpath):
                with open(fullpath, 'r') as f:
                    try:
                        langfile = yaml.load(f)
                        return langfile
                    except yaml.YAMLError as exc:
                        raise
                        print(exc)

        def grouper(n, iterable, fillvalue=None):
            args = [iter(iterable)] * n
            print('args', args)
            return itertools.zip_longest(fillvalue=fillvalue, *args)

        # split on spaces that aren't in quotes
        # Any not-: or space, up to a :, then \d, then \s, then quote, then anything that isn't a quote, up to the next quote
        country_splitter = re.compile('(?P<tag>[^:\s]+):\d\s"(?P<name>[^"]+)"')
        province_splitter = country_splitter
        #Countries
        cdata = load_yaml('countries_l_english.yml')
        citems = country_splitter.findall(cdata['l_english'])
        self.langs['en']['countries'] = dict(citems)
        
        # Provinces
        pdata = load_yaml('prov_names_l_english.yml')
        pitems = province_splitter.findall(pdata['l_english'])
        pitems = { int(k.replace('PROV', '')): v for k,v in pitems if 'PROV' in k}
        self.langs['en']['provinces'] = pitems

    def _(self, subject, key, lang=None):
        if lang is None:
            # Return object with all languages
            raise NotImplementedError()

        try:
            return self.langs[lang][subject][key]
        except KeyError:
            raise

    def save(self, data, stats=False):
        if self.internal is True:
            # Don't save 
            return

        if self.output is None:
            raise('No self.output set when calling save()')

        if stats is True and self.test is False:
            key = self.output.partition('.')[0]
            self.cs.save(key, data)
 
        if self.test is False:
            dump = json.dumps(data, cls=EU4JSON)
            with open(self.output, 'w') as f:
                f.write(dump)
        else:
            # Don't print debug/anything if we're running tests
            if sys.argv[0] != 'tests/test.py':
                print("#" * 5)
                print('Displaying generated data; not saving to file')
                print("#" * 5)
                print(data)

    def save_data(self, key, data):
        """
        Save small datapoint into output/data/x (for example, grouped list of religions) and re-compiled
        """
        dest = 'output/data/{0}.json'.format(key)
        compile_dest = 'output/data/_all.json'

        if self.test is False:
            dump = json.dumps(data, cls=EU4JSON)

            with open(dest, 'w') as f:
                f.write(dump)

            # Rebuild  
            print('Re-compiling data files')
            compiled = {}          
            for root, dirs, files in os.walk('output/data'):
                for f in files:
                    if f.endswith('.json') and f != '_all.json':
                        with open(os.path.join(root, f), 'r') as reader:
                            fname = f.partition('.')[0]
                            compiled[fname] = json.loads(reader.read())

            with open(compile_dest, 'w') as f:
                f.write(json.dumps(compiled, cls=EU4JSON))

    def gamefilepath(self, path):
        fp = os.path.join(EU4_PATH, *path.split(os.path.sep))
        assert os.path.exists(fp), "File {0} does not exist in EU4 directory".format(path)
        return fp 

    def walk_and_load_and_parse(self, directory): # maybe
        pass
    def load_and_parse(self, path):
        if not os.path.exists(path):
            raise IOError('Invalid path: {0}'.format(path))
        pass

    def first_nums(self, x):
        return int("".join(itertools.takewhile(str.isdigit, x)))
    def rgb_to_hex(self, red, green, blue):
        """Return color as #rrggbb for the given color values."""
        return '%02x%02x%02x' % (red, green, blue)
    def hex_to_rgb(self, hx):
        hx = hx.lstrip('#')
        return tuple(int(hx[i:i+2], 16) for i in (0, 2 ,4))

    def format_date(self, dt):
        return dt.strftime('%Y-%m-%d')

    def remove_comment_line(self, l):
        if '#' in l:
            l = l.partition('#')[0]
        l = l.strip()
        return l
    
    rdepth = 0
    placeholders = {}

    def set_placeholder(self, txt):
        self.rdepth += 1
        key = 'placeholder{0}'.format(self.rdepth)
        self.placeholders[key] = txt

        return key

    def gen2(self, s):
        """
        Split into first encountered }, then match to opening {
        Replace with a placeholder value
        """

        if '}' not in s:
            return s

        # Split string on first close brace, then backtrack
        sp = s.split('}', maxsplit=1)

        init = sp[0]

        block = init.rsplit('{', maxsplit=1)

        innermost = block[1]

        remainder_left = block[0]

        phkey = self.set_placeholder(innermost)

        remainder_right = sp[1]

        return remainder_left + phkey + remainder_right

    def gen(self, s):
        # Run through string per character
        # Generator
        """
        
        """
        k = None
        v = None

        reserved = ['{', '}', '=', '"', '']
        ignore = ['EU4txt', '}']

        subblock = False
        collect = []

        in_quote = False
        quoted = []

        for chars in s.split(' '):
            # Skip ones we're filtering out
            if chars.startswith('placeholder'):
                v = self.resolve_placeholder(chars)

            # Skip these
            if chars in ignore or chars in reserved:
                continue

            # We have no key, so probably need it
            if k is None:
                #print('chars for key', chars)
                k = self.clean_value(chars)
            # We have a key, but no value, and this isn't a random thing
            elif k is not None and v is None and chars not in reserved:
                # Check if we're in a quote
                if not in_quote and chars.startswith('"') and not chars.endswith('"'):
                    #print('starting quote', chars)
                    in_quote = not in_quote
                    quoted.append(chars[1:])
                    continue
                elif in_quote and not chars.endswith('"'):
                    #print('continueing quote', chars)
                    quoted.append(chars)
                    continue
                elif in_quote and chars.endswith('"'):
                    quoted.append(chars[0:-1])
                    chars = ' '.join(quoted)
                    #print('ending quote', chars)
                    quoted = []
                    in_quote = False

                v = self.clean_value(chars)
            
            if k is not None and v is not None:

                # Cast
                v = self.clean_value(v)

                # Dictify if necessary
                if isinstance(v, (list, tuple)):
                    v = self.dictify(v)

                if isinstance(k, (datetime.datetime, datetime.date)):
                    # Cast keys that are datetimes to string, so our json encode works (plus we don't need them as dts really)
                    k = k.isoformat()

                yield (k, v)

                k = None
                v = None

    def oneline(self, t, **kwargs):
        """
        """
        skip = kwargs.get('skip', [])
        fixparts = kwargs.get('fixparts', {})

        # Remove comments
        cleaned = []
        for line in t.split("\n"):
            if '#' in line:
                p = line.partition('#')
                cleaned.append(p[0])
            else:
                cleaned.append(line)
        t = "\n".join(cleaned)

        t = t.replace('}', ' } ').replace('{', ' { ').replace('=', ' = ').replace("\n", " ")

        # Remove multiple spaces
        t = ' '.join(t.split())

        # Quick regexp for easy blocks. Add in \= to also match k,v but can be annoying
        def magic_replace(matchobj):
            #print(matchobj.group(0))
            g = matchobj.group(0).strip().replace('{', '').replace('}', '')
            new_ph_key = self.set_placeholder(g)
            return new_ph_key

        # Replace easily matched braces with placeholders
        # Match braces that contain these values: whitespace, string, quotes, periods (for decimals), = (for k/v (OPTIONAL)), negative signs
        # single quotes (for peoples names: Kai-Ka'us)
        simple_braces = re.compile('\{([\w\s\"\.\=\-\']*?)\}')
        # Replace each match with a built in placeholder
        # Loop until we have no more matches
        while '{' in t:
            nt = simple_braces.sub(magic_replace, t)

            if nt == t:
                break

            t = nt

        #print('COUNT BRACES AFTER REGEX')
        #print(t.count('}'), t.count('{'))
        # Reduce it to placeholders

        # Use string manipulation for the remainder
        while '{' in t:
            #print('len', len(t))
            t = self.gen2(t)

        # Now parse through t, while replacing the placeholders
        comp = {}
        used_keys = []
        for k, char in self.gen(t):

            # Sometimes we awesomely use the same key name
            if k in used_keys:
                if isinstance(comp[k], list):
                    comp[k].append(char)
                else:
                    comp[k] = [comp[k], char]
            else:
                comp[k] = char

            used_keys.append(k)

        # Convert list of tuples into dictionary
        return comp

    def resolve_placeholder(self, phkey):
        """
        Resolve recursively
        """
        if phkey not in self.placeholders:
            raise KeyError('Unknown placeholder: {0}'.format(phkey))

        ph = self.placeholders[phkey]

        if '=' in ph:
            # Normal
            #print('normal', ph)
            v = self.gen(ph)
            v = list(map(self.clean_value, v))
        elif ph.replace(" ", "").isdigit():
            # Contains only numbers or spaces or decimals (just numbers for now, parse decimals later)
            v = self.parse_number_list(ph)
        elif ph.replace(" ", "").isalnum():
            # Probably a list of say tags, just straight text
            # But might also be placeholders
            stack = []

            for val in filter(lambda x: len(x) > 0, ph.split(' ')):
                if val.startswith('placeholder'):
                    val = self.resolve_placeholder(val)

                #print('VAL VAL VAL', val)
                # todo: possibly don't want to clean_val, or if a list is like [a b c no] it'll try to cast it to bool
                # so just keep as strings/ints
                stack.append(val)

            v = stack
        elif ph.count('"') % 2 == 0:
            # If an even number of quotes
            v = self.parse_str_list(ph)

        # Does this contain more placeholders?
        return v

    def dictify(self, obj):
        comp = {}
        if len(obj) == 0:
            # Could be an empty list for some stupid reason
            return obj

        test = obj[0]
        #print('OBJ', type(test), obj)

        if isinstance(test, (str, int)):
            # Don't dictify list of items. Pray there aren't lists of numbers with internal dicts, seems like they're mostly
            # k=v, k2=v2, k3={ a=1 } which would work anyway
            return obj

        if isinstance(test, list):
            # Keep going deeper

            mklist = []
            for _, item in enumerate(obj):
                #print('zbop')
                vals = self.dictify(item)
                mklist.append(vals)

            return mklist

        #for _, item in enumerate(obj):
        if isinstance(test, tuple):
            # List of tuples, hopefully. squash into dict
            comp = { k:None for k, v in obj }
            #print('testcomp', comp)
            for _, item in enumerate(obj):
                #print('type', item, type(item))
                if comp[item[0]] is None:
                    comp[item[0]] = item[1]
                elif not isinstance(comp[item[0]], list):
                    comp[item[0]] = [comp[item[0]]]
                    comp[item[0]].append(item[1])
                else:
                    comp[item[0]].append(item[1])
                if item[0] == 'ledger_data':
                    #print(comp)
                    pass

        return comp if comp != {} else obj

    re_quote_splitter = re.compile('("[^"]+")')
    def parse_str_list(self, s):
        """
        Contains an even number of quotes, and no equals sign. Split on quotes, remove any empty elements

        eg:
        "Conquest of Paradise" "Wealth of Nations" "Res Publica" "Art of War" "Rights of Man" "Mandate of Heaven" "Third Rome"
        """
        # SomETIMES WE HAVE QUOTES MIXED WITH NO QUOTES :D
        stack = []
        for item in self.re_quote_splitter.split(s):
            # Split out the items that are quoted
            if '"' not in item:
                # now just a normal string with n items
                listed = filter(lambda x: len(x.strip()) > 0, item.split(' '))
                stack.extend(list(map(self.clean_value, listed)))
            else:
                # Quoted part, so use the whole thing
                stack.append(self.clean_value(item))

        return stack

    def parse_number_list(self, s):
        """
        List of either ints or decimals
        """
        #print('NUMBER LIST', s)
        flist = map(int, filter(lambda x: len(x) > 0, s.split(' ')))
        return list(flist)

    def parse_number(self, s):
        """
        '0.0000' -> 0
        '-1.000' -> -1
        '-5.124' -> Decimal('-5.124')
        '1.1.12' -> '1.1.12'
        """
        num = s

        if num.count('.') == 1:
            # Check if we can round it
            p = num.partition('.')
            if int(p[2]) == 0:
                num = int(p[0])
            else:
                num = Decimal(num)
        elif num.count('.') > 1:
            # Possibly a dummy date like 1.1.1, just return
            pass
        else:
            try:
                num = int(num)
            except ValueError:
                num = s
        return num

    def clean_value(self, val): 
        #print('cleaning ', val)
        if isinstance(val, str):
            if val.startswith('"') and val.endswith('"'): # Remove unnecessary quotes
                val = val[1:-1]
            elif val.isdigit(): # If it's all integers
                val = int(val)
            elif val == 'no': # Bool casting
                val = False
            elif val == 'yes':
                val = True
            else:
                # If it looks like a date
                datesearch = self.match_date.search(val)
                if datesearch is not None:
                    val = datetime.datetime(*list(map(int, datesearch.groups())))
                # If it looks like a decimal, or list of them
                elif self.match_num_list.match(val):
                    mklist = []
                    for num in val.split():

                        v = self.parse_number(num)

                        mklist.append(v)

                    # Switch back to single if possible
                    if len(mklist) == 1:
                        val = mklist[0]
                    else:
                        val = mklist
                    #print('MATCHED LIST THANG:', val, type(val))

        if isinstance(val, list):
            if len(val) == 0:
                return val

            if str(val[0]).isdigit():
                val = list(map(int, val))
            elif isinstance(val[0], str):
                # Probably str, remove quotes
                val = list(map(lambda x: x.strip('"'), val))
        return val

class DataParser(object): 

    cs = None
    test = False

    def __init__(self, test=False, **kwargs): 
        self.min_dt = datetime.datetime(1444, 11, 11)
        self.cs = Checksum()
        self.dtre = re.compile("(\d{4})\.(\d+)\.(\d+)")
        self.test = test

    def checksum(self): pass
    def load_file(self, fname, type='json'): pass # type = json/csv/custom?

    def save(self, data, stats=False):
        def json_serial(obj):
            """JSON serializer for objects not serializable by default json code"""

            if isinstance(obj, (datetime.datetime, datetime.date)):
                return obj.isoformat()
            raise TypeError ("Type %s not serializable" % type(obj))

        if self.output is None:
            raise('No self.output set when calling save()')

        if stats is True and self.test is False:
            key = self.output.partition('.')[0]
            self.cs.save(key, data)

        if self.test is False:
            dump = json.dumps(data, default=json_serial)
            with open(self.output, 'w') as f:
                f.write(dump)
        else:
            pass
            #print("#" * 5)
            print('Displaying generated data; not saving to file')
            #print("#" * 5)
            #print(data)

    def gamefilepath(self, path):
        fp = os.path.join(EU4_PATH, *path.split(os.path.sep))
        assert os.path.exists(fp), "File {0} does not exist in EU4 directory".format(path)
        return fp 

    def first_nums(self, x):
        return int("".join(itertools.takewhile(str.isdigit, x)))
    def rgb_to_hex(self, red, green, blue):
        """Return color as #rrggbb for the given color values."""
        return '%02x%02x%02x' % (red, green, blue)
    def hex_to_rgb(self, hx):
        hx = hx.lstrip('#')
        return tuple(int(hx[i:i+2], 16) for i in (0, 2 ,4))

    def format_date(self, dt):
        return dt.strftime('%Y-%m-%d')

    def remove_comment_line(self, l):
        if '#' in l:
            l = l.partition('#')[0]
        l = l.strip()
        return l

    # split the file into parts
    def combine_eq(self, t, makelistkeys=[], toplist=False, seperate=[], *args, **kwargs):
        """
        makelistkeys: if any of these keys are encountered, compile into a list, will cast to int if isdigit() succeeds
        toplist: combine multiple blocks into one, based on key. sometimes (ex history/diplomacy) we just need a top level list of everything
        seperate: OBJ similar to toplist, don't combine these into one, trade nodes can have multiple outgoing={}

        seperate2: if we have say multiple active_war, then calc them seperately and turn it into a list of them
        """
        has_key = None
        use_val = False
        group = {}
        val = None

        # accumulate quoted strings
        quoted = []
        makelist = None
        makelistmulti = []

        # combine into groups, surrounding the = sign
        for part in t.split():
            #print('=' * 30)
            #print('PART', part)
            if has_key is None and part not in ['=', '}'] and (part not in makelistkeys and makelist is None):
                has_key = part
                #print('setting key to ', has_key)
                continue
            elif has_key is not None and part == '=' and makelist is None:
                #print('changing to set value')
                use_val = True
                continue            
            elif part in makelistkeys or makelist is not None:
                # for these keys, accumulate the numbers between the blocks
                #print('makelistkey')
                if makelist is None:
                    has_key = part
                    makelist = part # our future key
                    continue
                elif part == '}':
                    use_val = True
                    val = makelistmulti
                    # probably cast to int?
                    #print('close our makelistkey, with val', val)
                elif part not in ['{', '=']:
                    #print('appending ', part)
                    if part.isdigit():
                        part = int(part)
                    makelistmulti.append(part)
                    continue            
            elif part == '}':
                yield ('}', 'CONTROL_CLOSEBLOCK')
                continue

            if use_val:
                #print('-' * 20)
                # Check for quotes
                if val is None:
                    val = part
                #print('val', part, part[0] == '"', part[-1:])
                if '"' in part or len(quoted) > 0:
                    # Deal with quoted strings
                    if (part[0] == '"' and part[-1:] != '"') or (len(quoted) > 0 and part[-1:] != '"'):
                        # Keep looping until we find the end of this string
                        quoted.append(part)
                        continue
                    if part[-1:] == '"':
                        # end of quoted string
                        quoted.append(part)
                        val = ' '.join(quoted)[1:-1].strip('"')
                        quoted = []
                # are we opening a block?
                if val == '{' or has_key == '{':
                    val = 'CONTROL_OPENBLOCK'

                group[has_key] = val

                val = self.clean_value(val)
                #print('found val', has_key, val)

                yield (has_key, val)
                use_val = False
                has_key = None
                group = {}
                makelist = None
                makelistmulti = []
                val = None

    def oneline(self, t, **kwargs):
        # convert it to one line
        # remove comments since they mess with me
        nocomments = []

        skip = kwargs.get('skip', [])
        fixparts = kwargs.get('fixparts', {})

        # ensure braces are spaced right
        t = t.replace('}', ' } ').replace('{', ' { ').replace('=', ' = ')

        for l in t.split("\n"):
            if '#' in l:
                l = l.partition('#')[0]
            l = l.strip()

            #
            if l in skip:
                continue

            if l in fixparts:
                #print(fixparts)
                l = fixparts[l]

            nocomments.append(l)
        #print(nocomments[0:200])
        back = "\n".join(nocomments)

        builder = Builder(**kwargs)
        #print(back)
        for k,v in self.combine_eq(back, **kwargs):
            builder.add(k, v)
        #print(builder.data)
        return builder.finalize()

    def clean_value(self, val): 
        if isinstance(val, str):
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]

        if isinstance(val, list):
            if str(val[0]).isdigit():
                val = list(map(int, val))
            else:
                # Probably str, remove quotes
                val = list(map(lambda x: x.strip('"'), val))
        return val

