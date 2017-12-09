import json, hashlib, datetime, os, itertools

EU4_PATH = 'B:\SteamLibrary\steamapps\common\Europa Universalis IV'

class Checksum(object):

    cfile = 'checksum.json'

    def __init__(self): 
        # Load checksum file
        with open(self.cfile, 'r') as f:
            self.data = json.loads(f.read())

        self.countries = self.data.get('countries', {})
        self.provinces = self.data.get('provinces', {})
        self.map = self.data.get('map', {})

    def save(self, key, data):
        jstr = json.dumps(data, sort_keys=True).encode('utf-8')

        h = hashlib.md5(jstr).hexdigest()

        set_dict = {
            'hash': h,
            'len': len(data),
            'when': str(datetime.datetime.now())
            }
        self.data[key].update(set_dict)

        with open(self.cfile, 'w') as f:
            f.write(json.dumps(self.data))

        print(set_dict)

class DataParser(object): 
    def __init__(self): 
        self.min_dt = datetime.datetime(1444, 11, 11)

    def checksum(self): pass
    def load_file(self, fname, type='json'): pass # type = json/csv/custom?
    def save(self): pass

    def gamefilepath(self, path):
        fp = os.path.join(EU4_PATH, *path.split(os.path.sep))
        assert os.path.exists(fp), "File {0} does not exist in EU4 directory".format(str)
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