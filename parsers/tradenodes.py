import json

from parsers.base import DataParser_save
import pprint
class TradenodeParser(DataParser_save):
    """
    Parser fudged up somewhere, hormuz members is just a string
    """
    output = 'output/tradenodes.json'
    data = {}

    def __init__(self, test=False, **kwargs):
        super().__init__(test=test, **kwargs)

        self.nodes = self.gamefilepath('common/tradenodes/00_tradenodes.txt')

        self.internal = kwargs.get('internal', False)

    def parse_all(self, one=None): 
        self.cs.start()

        with open(self.nodes, 'r') as fc:
            read = fc.read()
        self.data = self.oneline(read)


        # Used in provinceparser to allocate each province to a trade node

        # replace some colors cause they don't exist in the nodes file
        # taken from: https://eu4.paradoxwikis.com/Trade_nodes
        # https://eu4.paradoxwikis.com/images/f/f7/Trade_nodes_with_arrows.png
        """
        Get all colors from page:
        $$('.sortable tr td:first-child').forEach(i => {
            let rgb = i.querySelector('span').style.background.split(')')[0].slice(4);
            let name = i.innerText.trim().replace(/\s+/g, '_').replace(/\W/g, '').toLowerCase();
            console.log(name, rgb);
        })
        Sublime find/replace: (\w+)\s+(\d+)\,\s+(\d+)\,\s+(\d+)\s and \t'\1': [\2, \3, \4],\n as replace
        """
        replacements = {
            'aleppo': [ 120,148,140],
            'alexandria': [ 200, 200, 102],
            'amazonas_node': [57, 160, 101, 'Amazonas'], # amazonas
            'astrakhan': [130, 25, 74],
            'australia': [69, 130, 203],
            'baltic_sea': [8, 82, 165],
            'basra': [193, 65, 54],
            'beijing': [147, 157, 76],
            'ganges_delta': [118, 99, 151, 'Bengal'], # bengal
            'bordeaux': [36, 132, 247],
            'brazil': [220, 138, 57],
            'california': [199, 175, 12],
            'canton': [195, 149, 155],
            'cape_of_good_hope': [240, 167, 130],
            'carribean_trade': [220, 150, 158], # carribean
            'comorin_cape': [33, 101, 137], # ceylon
            'champagne': [193, 26, 14],
            'chengdu': [231, 181, 12],
            'chesapeake_bay': [193, 26, 14],
            'constantinople': [126, 203, 120],
            'crimea': [59, 158, 125],
            'cuiaba': [94, 117, 55],
            'doab': [236, 162, 19],
            'english_channel': [220, 138, 57],
            'ethiopia': [36, 109, 194],
            'genoa': [218, 215, 56],
            'girin': [41, 82, 45],
            'goa': [110, 173, 129],
            'great_lakes': [57, 168, 220],
            'gulf_of_aden': [100, 94, 125],
            'gulf_of_st_lawrence': [193, 192, 14],
            'hangzhou': [4, 144, 178],
            'hormuz': [40, 121, 66],
            'hudson_bay': [97, 220, 117],
            'indus': [135, 104, 85],
            'ivory_coast': [48, 164, 51],
            'kashmir': [63, 150, 30],
            'katsina': [215, 56, 56],
            'kazan': [132, 70, 102],
            'kiev': [117, 161, 67],
            'kongo': [171, 148, 148],
            'krakow': [191, 113, 133],
            'lhasa': [94, 136, 191],
            'lima': [193, 26, 14],
            'lbeck': [190, 70, 70],
            'malacca': [182, 134, 100],
            'mexico': [0, 176, 0],
            'mississippi_river': [117, 165, 188],
            'the_moluccas': [125, 92, 110],
            'nippon': [59, 158, 125],
            'north_sea': [117, 165, 188],
            'novgorod': [97, 126, 37],
            'ohio': [129, 214, 238],
            'panama': [104, 137, 140],
            'patagonia': [219, 124, 139],
            'persia': [204, 119, 31],
            'philippines': [26, 53, 177],
            'ragusa': [39, 108, 140],
            'rheinland': [114, 171, 184],
            'laplata': [62, 122, 189], # rio_de_la_plata
            'rio_grande': [194, 140, 86],
            'safi': [191, 110, 62],
            'samarkand': [118, 193, 153],
            'saxony': [93, 124, 87],
            'sevilla': [57, 160, 101],
            'siam': [84, 152, 93],
            'siberia': [201, 97, 74],
            'timbuktu': [136, 157, 23],
            'tunis': [146, 134, 57],
            'venice': [54, 167, 156],
            'white_sea': [210, 46, 28],
            'wien': [220, 220, 220],
            'xian': [191, 113, 133],
            'yumen': [116, 92, 39],
            'zambezi': [32, 164, 51],
            'zanzibar': [130, 17, 17],
        }

        # Also create an 'incoming' based on others' 'outgoing'
        def out_nodes(node):
            if 'outgoing' in node:
                if isinstance(node['outgoing'], dict):
                    return [node['outgoing']['name']]
                return [ n['name'] for n in node['outgoing'] ]
            return []
        for node, info in self.data.items():
            # Find node in others
            incoming = [ k for k,v in self.data.items() if node in out_nodes(v) ]
            self.data[node]['incoming'] = incoming

        for k,v in replacements.items():
            if k in self.data:
                if 'color' not in self.data[k]:
                    self.data[k]['color'] = v[0:3]

                if len(v) == 4:
                    # use new name
                    self.data[v[3]] = self.data[k]
                    del self.data[k]

        if one is not None:
            print(self.data[one])
            return self.data[one]

        # only save the name
        if not self.internal:
            self.save(self.data)

        return self.data

    def belongs_to(self, pid):
        for name, node in self.data.items():
            if pid in node['members']:
                return name

    def is_main(self, pid):
        for name, node in self.data.items():
            if pid == node['location']:
                return True
        return False

"""
    'aleppo': [120, 148, 140],
    'alexandria': [200, 200, 102],
    'amazonas': [57, 160, 101],
    'astrakhan': [130, 25, 74],
    'australia': [69, 130, 203],
    'baltic_sea': [8, 82, 165],
    'basra': [193, 65, 54],
    'beijing': [147, 157, 76],
    'bengal': [118, 99, 151],
    'bordeaux': [36, 132, 247],
    'brazil': [220, 138, 57],
    'california': [199, 175, 12],
    'canton': [195, 149, 155],
    'cape_of_good_hope': [240, 167, 130],
    'caribbean': [220, 150, 158],
    'ceylon': [33, 101, 137],
    'champagne': [193, 26, 14],
    'chengdu': [231, 181, 12],
    'chesapeake_bay': [193, 26, 14],
    'constantinople': [126, 203, 120],
    'crimea': [59, 158, 125],
    'cuiaba': [94, 117, 55],
    'doab': [236, 162, 19],
    'english_channel': [220, 138, 57],
    'ethiopia': [36, 109, 194],
    'genoa': [218, 215, 56],
    'girin': [41, 82, 45],
    'goa': [110, 173, 129],
    'great_lakes': [57, 168, 220],
    'gulf_of_aden': [100, 94, 125],
    'gulf_of_st_lawrence': [193, 192, 14],
    'hangzhou': [4, 144, 178],
    'hormuz': [40, 121, 66],
    'hudson_bay': [97, 220, 117],
    'indus': [135, 104, 85],
    'ivory_coast': [48, 164, 51],
    'kashmir': [63, 150, 30],
    'katsina': [215, 56, 56],
    'kazan': [132, 70, 102],
    'kiev': [117, 161, 67],
    'kongo': [171, 148, 148],
    'krakow': [191, 113, 133],
    'lhasa': [94, 136, 191],
    'lima': [193, 26, 14],
    'lbeck': [190, 70, 70],
    'malacca': [182, 134, 100],
    'mexico': [0, 176, 0],
    'mississippi_river': [117, 165, 188],
    'the_moluccas': [125, 92, 110],
    'nippon': [59, 158, 125],
    'north_sea': [117, 165, 188],
    'novgorod': [97, 126, 37],
    'ohio': [129, 214, 238],
    'panama': [104, 137, 140],
    'patagonia': [219, 124, 139],
    'persia': [204, 119, 31],
    'philippines': [26, 53, 177],
    'ragusa': [39, 108, 140],
    'rheinland': [114, 171, 184],
    'rio_de_la_plata': [62, 122, 189],
    'rio_grande': [194, 140, 86],
    'safi': [191, 110, 62],
    'samarkand': [118, 193, 153],
    'saxony': [93, 124, 87],
    'sevilla': [57, 160, 101],
    'siam': [84, 152, 93],
    'siberia': [201, 97, 74],
    'timbuktu': [136, 157, 23],
    'tunis': [146, 134, 57],
    'venice': [54, 167, 156],
    'white_sea': [210, 46, 28],
    'wien': [220, 220, 220],
    'xian': [191, 113, 133],
    'yumen': [116, 92, 39],
    'zambezi': [32, 164, 51],
    'zanzibar': [130, 17, 17],
"""