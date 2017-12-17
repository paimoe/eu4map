import json, hashlib, datetime, os, itertools, re, collections, pprint
from timeit import default_timer as timer

"""
TODO
- map/terrain.txt, allow for { 1 2 3 4 5 etc}
"""

EU4_PATH = 'B:\SteamLibrary\steamapps\common\Europa Universalis IV'

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
    def __init__(self, seperate=None, **kwargs):
        self.keys = []
        self.depth = 0
        self.tree = []
        self.data = collections.defaultdict()

        self.splitter = 'xx__xx' # random value to split the string since we can't really use space, _ or .
        self.dtre = re.compile("(\d{4})\.(\d+)\.(\d+)")

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

        for key in keys[:-1]:
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
        if isinstance(v, str):
            if v.startswith('CONTROL'):
                if v.endswith('CLOSEBLOCK'):
                    self.shallow()
                elif v.endswith('OPENBLOCK'):
                    self.deeper(k)
                return

        key = self.splitter.join(self.tree) + self.splitter + k
        if self.depth == 0:
            key = k
        
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
        # if we're meant to seperate any, then loop through and split
        # we can assume the lists are in the correct order since we read the page vertically

        """
        - split into total blocks
        - find the key(s) that should be seperated. it'll be a dict with each key, and a list of values (including lists of lists)
        """
        if self.seperate is not None:
            for _, block in self.data.items(): # eg for each trade node, split it out
                i = 0
                #print(block)
                newlist = []
                try:
                    obj = block[self.sepname]
                    #rint('LEN', obj['_len'])

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

                #print('new', newlist)

                # unset the big long lists, and set the new thing
                block[self.sepname] = newlist



        return self.data

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
            print(data)

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
    def combine_eq(self, t, makelistkeys=[], toplist=False, seperate=[]):
        """
        makelistkeys: if any of these keys are encountered, compile into a list, will cast to int if isdigit() succeeds
        toplist: combine multiple blocks into one, based on key. sometimes (ex history/diplomacy) we just need a top level list of everything
        seperate: similar to toplist, don't combine these into one, trade nodes can have multiple outgoing={}
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
                #print('found val', val)
                # are we opening a block?
                if val == '{':
                    val = 'CONTROL_OPENBLOCK'

                group[has_key] = val
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

        # ensure braces are spaced right
        t = t.replace('}', ' } ').replace('{', ' { ').replace('=', ' = ')

        for l in t.split("\n"):
            if '#' in l:
                l = l.partition('#')[0]
            l = l.strip()

            nocomments.append(l)

        back = "\n".join(nocomments)

        builder = Builder(**kwargs)
        #print(back)
        for k,v in self.combine_eq(back, **kwargs):
            builder.add(k, v)
        #print(builder.data)
        return builder.finalize()

class DataParser_old(object): 

    cs = None

    def __init__(self): 
        self.min_dt = datetime.datetime(1444, 11, 11)
        self.cs = Checksum()

    def checksum(self): pass
    def load_file(self, fname, type='json'): pass # type = json/csv/custom?
    def save(self): pass

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

    def parse_file_generator(self, fname):
        # open, create a generator
        with open(os.path.join(fname), 'r') as fc:
            # Get line
            braces = 0
            building = False
            build_multi = []
            for cnt, line in enumerate(fc):

                line = self.remove_comment_line(line.strip())
                if line == '':
                    continue

                # normalize whitespace
                line = ' '.join(line.replace('{', ' { ').replace('}', ' } ').split())
                print('new line', braces,  line)
                
                # if we're building multiline, then just add this line and continue until we hit the last }
                # TODO: nested multi builds, basically just building a single line thing
                # TODO: quotes around some values, like dynasty = "von Habsburg"
                if building is True:
                    if '{' in line:
                        braces += line.count('{')
                        continue
                        
                    build_multi.append(line.replace(' = ', '='))
                    print('BUILDING: ', braces, build_multi)
                    braces += line.count('{')
                    if '}' not in line:
                        continue

                    if '}' in line:
                        braces -= line.count('}')
                        if braces == 0:
                            line = ' '.join(build_multi)
                            building = False
                            build_multi = []
                            braces = 0
                            yield self.parse_line_block(line)
                        else:
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
                        print('braces', braces, line)
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

    # brutal
    def parse_line_block(self, line):
        """
        if is char:
            appendnewkey_or_value, continue

        if is = 
            closekey, open value, continue

        if is space
            close value, continue, open key

        if is {
            open block

        if is }
            close block
        """
        ourobj = {}
        n = ['',''] # temp k,v store
        setting_which = 0 # position in tuple `n` that we're setting, flip when we go from key to val
        line = line.strip().lstrip('{')

        skip_until = 0
        len_used = 0
        for pos, v in enumerate(line.strip()):
            #print(pos,v)
            len_used += 1
            if pos < skip_until:
                continue

            if v.isalpha() or v.isdigit() or v == '_':
                n[setting_which] += v
                #print('adding to ', setting_which, v)
                continue

            if v == '=':
                setting_which = 1 - setting_which
                #print('changing setting to ', setting_which)
                continue

            if v == ' ':
                setting_which = 0
                ourobj[n[0]] = n[1]
                #print('ourobj', ourobj)
                n = ['', '']
                continue

            if v == '{':
                # new block
                nline = line.strip()[pos:]
                p = self.parse_line_block(nline)
                #print('this', n[0], nline, pos, p['obj'])
                n[1] = p['obj']
                #print(n)
                # skip ahead the length of  the used string
                skip_until = pos + p['len'] + 1
                #print('skipping', skip_until, line[skip_until:])
                continue

            if v == '}':
                break
            #print(n)
        # in case we have leftovers
        if n != ['', '']:
            ourobj[n[0]] = n[1]

        return {
            'len': len_used,
            'obj': ourobj
        }