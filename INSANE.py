from itertools import islice
import collections, re, datetime
tests = """government = despotic_monarchy
government_rank = 1
primary_culture = albanian
religion = catholic
technology_group = eastern
capital = 4175 # Lezhe

# The League of Lezhe
1443.3.4 = {
    monarch = {
        name = "Gjergj Skanderbeg"
        dynasty = "Kastrioti"
        birth_date = 1405.1.1       
        adm = 6
        dip = 5
        mil = 6
        leader = {  name = "Skanderbeg"             type = general  fire = 5    shock = 5   manuever = 5    siege = 0}
    }
    clear_scripted_personalities = yes
    add_ruler_personality = inspiring_leader_personality
    add_ruler_personality = silver_tongue_personality
}

1443.3.4 = {
    heir = {
        name = "Gjon"
        monarch_name = "Gjon II"
        dynasty = "Kastrioti"
        birth_date = 1420.1.1
        death_date = 1478.1.1
        claim = 95
        adm = 3
        dip = 4
        mil = 2
    }
}

1468.1.18 = {
    monarch = {
        name = "Gjon II"
        dynasty = "Kastrioti"
        birth_date = 1420.1.1       
        adm = 3
        dip = 4
        mil = 2
    }
}

1468.1.18 = {
    heir = {
        name = "Constantino"
        monarch_name = "Constantino"
        birth_date = 1440.1.1
        death_date = 1478.6.16
        claim = 95
        adm = 3
        dip = 2
        mil = 1
    }
}

1478.1.1 = {
    monarch = {
        name = "Constantino"
        dynasty = "Kastrioti"
        birth_date = 1440.1.1       
        adm = 3
        dip = 2
        mil = 1
    }
}
"""

tests = """
jungle = {
        color = { 98 163 18 }

        type = jungle
        sound_type = jungle

        movement_cost = 1.5
        defence = 1
        cs_only_local_development_cost = 0.35
        nation_designer_cost_multiplier = 0.8
        supply_limit = 5
        
        terrain_override = {
            1237 1245 2703 #South East Asia
            746 838 #South America
            534 535 537 546 547 551 553 560 564 566 567 568 570 571 573 1946 1950 2028 2029 2034 2038 2042
            2048 2049 2050 2091 2098 2096 2099 2100
            2039
            486 490 743 745 748 826 835 840 846 848 2630 2637 2641 2647 2654 2655 2659 2664 2819 2927
            
            582 2397 2398 579 2402 1815 590 2403 2400 589 602 1817 2389 2388 592 591 2404 843
            789 1151 1181 1182 1183 2952
            
            616 2372 610 2377
            756 759 757 765 2894 2896 2914 2929 
            1125 1138 1139 1162 1249
            1118
            
            660 663 664 666 2160 2161 2162 2164 2166 
            2731 2732 #Australia
            4021 4024 4025 4026 #Madagascar
            4090 4105 4109 #Central Africa
        }
    }   
"""

TESTS = {
    "1583.1.1 = { fort_15th = no fort_16th = yes }": {'fort_15th': 'no', 'fort_16th': 'yes'}
}

def blockParser(line):
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
    newkey = ''
    newval = ''
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
            #print('adding to ', setting_which)
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
            #print('this',nline, pos, line.strip())
            p = blockParser(nline)
            n[1] = p['obj']
            print(n)
            # skip ahead the length of  the used string
            skip_until = pos + p['len']
            print('skipping', skip_until)
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
"""
for line in tests:
    if '{' in line:
        #print('HAS A BLOCK', line)
        if line.count('{') == line.count('}'):
            print('--------------------')
            # single line block
            # Get first up to equals
            d = line.split(' = ')
            key = d.pop(0)
            #print('ass',key, '='.join(d))
            rest = '='.join(d)
            #rest = rest.rstrip('}').lstrip('{')
            
            ourobj = blockParser(rest)

            print('ourobj=', ourobj['obj'])
"""

def gen(txt):
    braces = 0
    building = False
    build_multi = []
    for cnt, line in enumerate(txt):
        #print(cnt, line)
        print(build_multi)
        #line = self.remove_comment_line(line.strip())
        if building:
            # currently building, only have the previous line. if this is another open
            bdiff = line.count('{') - line.count('}')
            braces += bdiff

            if bdiff > 0:
                # further depth
                continue
            elif bdiff == 0:
                # just add the line, it either has no braces, or an even number of them
                build_multi.append(line)
                continue
            elif bdiff < 0:
                # went out one? soooo
                if braces == 0:
                    yield ' '.join(build_multi)
                    build_multi = []
                    building = False
                else:
                    # still in some block, so keep going
                    continue
            #print('in building', braces, line)

        """
        # normalize whitespace
        line = ' '.join(line.split())
        #print('new line', line)
        
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

                else:
                    continue

        if line == '':
            continue
        """
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
                #print('braces', braces,line)
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

#print(list(gen(tests)))

def combine_eq(t):
    has_key = None
    use_val = False
    group = {}
    val = None

    # accumulate quoted strings
    quoted = []
    makelist = None
    makelistmulti = []
    makelistkeys = ['color', 'terrain_override'] # this will be inherited from the parsers

    # combine into groups, surrounding the = sign
    for part in t.split():
        print('=' * 30)
        print('PART', part)
        if has_key is None and part not in ['=', '}'] and (part not in makelistkeys and makelist is None):
            has_key = part
            print('setting key to ', has_key)
            continue
        elif has_key is not None and part == '=' and makelist is None:
            print('changing to set value')
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
            print('closing block')
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
                    quoted = []#
            #print('found val', val)
            # are we opening a block?
            if val == '{':
                print('making openblock')
                val = 'CONTROL_OPENBLOCK'
            group[has_key] = val
            #print(group)
            yield (has_key, val)

            # reset everything
            use_val = False
            has_key = None
            group = {}
            makelist = None
            makelistmulti = []
            val = None

import pprint
class Builder(object):
    def __init__(self):
        self.keys = []
        self.depth = 0
        self.tree = []
        self.data = collections.defaultdict()

        self.splitter = 'xx__xx'

    def nest(self, keys, value):
        dic = self.data
        lastkey = keys[-1]
        for key in keys[:-1]:
            dic = dic.setdefault(key, {})

        try:
            # see if it exists, and convert to list if it does
            # if it doesn't exist, dic[lastkey] will hit exception
            if not isinstance(dic[lastkey], list):
                dic[lastkey] = [dic[lastkey]]
            dic[lastkey].append(value)

        except KeyError:
            # just set it
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

        # build key
        key = self.splitter.join(self.tree) + self.splitter + k
        if self.depth == 0:
            key = k
        
        # convert value
        if not isinstance(v, list):
            dtkey = re.search("(\d{4})\.(\d+)\.(\d+)", v)
            if dtkey is not None:
                v = datetime.datetime(*list(map(int, dtkey.groups())))
            elif v.isdigit():
                v = int(v)
            elif v in ['yes', 'no']:
                v = v == 'yes'

        # set nested dict
        b = self.nest(key.split(self.splitter), v)

        #self.data[key] = e
        #self.data2.update(e)

    def deeper(self, k):
        self.tree.append(k)
        self.depth += 1

    def shallow(self):
        self.tree.pop()
        self.depth -= 1

    def show(self):
        pprint.pprint(self.data)

def oneline(t):
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

    builder = Builder()

    for k,v in combine_eq(back):
        #print(k,v)
        builder.add(k, v)

    builder.show()

oneline(tests)

"""
it sets the k/v to siege = 0
then finds a } and uses that as a key
then another one (hasn't found a =, so wont switch to vlaue change)
"""