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
    def __init__(self): pass
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