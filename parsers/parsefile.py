import datetime, re
from decimal import Decimal 

"""
In order to facilitate transpiling to JS, different style conventions in this file, and aliases
Do as much as I can here to conver it to JS since i'll be here more
- use parens for if clauses
- commented out {} so we can use them easier
- remove any lines that end in #JSDEL
"""
"""
var jstr = str => str;
function jstr(str) {
    return str;
}
"""
class jstr(str):
    #def __init__(self, *args, **kwargs):
    #    super().__init__()
    def slice(self, i, j=None):
        return self[i:j]
    def startsWith(self, s):
        return self.startswith(s)
    def endsWith(self, s):
        return self.endswith(s)
    #def rsplit(self, sep, limit=-1):
    #    return super().split(sep, maxsplit)
def contains(stack, needle):
    return needle in stack
def to_date(year, month, day):
    return datetime.datetime(year, month, day)

class ParseFile(object):#{ 
    """
    Pass in a string and return a dict

    File loading/saving/caching etc is handled above this
    """
    def __init__(self, t=None): return self.constructor(t)

    def constructor(self, t=None):#{ 
        self.t = t
        self.rdepth = 0
        self.placeholders = {}

        # Match braces that contain these values: whitespace, string, quotes, periods (for decimals), = (for k/v (OPTIONAL)), negative signs
        # single quotes (for peoples names: Kai-Ka'us)
        self.match_braces = re.compile('\{([\w\s\"\.\=\-\']*?)\}')
        self.match_date = re.compile('(\d{4})\.(\d+)\.(\d+)')
        # Should match a list of numbers, including decimals and negatives
        self.match_num_list = re.compile('^[\s\d\.\-]+$')
        self.quote_splitter = re.compile('("[^"]+")')
    #}

    def set_placeholder(self, txt):#{ 
        self.rdepth += 1
        key = 'placeholder' + str(self.rdepth)
        self.placeholders[key] = txt

        return key
    #}

    def gen2(self, s):#{
        """
        Split into first encountered }, then match to opening {
        Replace with a placeholder value
        """
        if (contains(s, '}') == False):#{ 
            return s
        #}

        # Split string on first close brace, then backtrack
        sp = s.split('}', 1)

        init = sp[0]

        block = init.rsplit('{', 1)

        innermost = block[1]

        remainder_left = block[0]

        phkey = self.set_placeholder(innermost)

        remainder_right = sp[1]

        return remainder_left + phkey + remainder_right
    #}

    def gen(self, s):#{
        # Run through string per character
        # Generator
        k = None
        v = None

        reserved = ['{', '}', '=', '"', '']
        ignore = ['EU4txt', '}']

        subblock = False
        collect = []

        in_quote = False
        quoted = []

        for chars in s.split(' '):#{
            chars = jstr(chars) #JSDEL

            # Skip ones we're filtering out
            if (chars.startsWith('placeholder')):#{
                v = self.resolve_placeholder(chars)
            #}

            # Skip these
            if (contains(ignore, chars) or contains(reserved, chars)):#{
                continue
            #}

            # We have no key, so probably need it
            if (k == None):#{
                k = self.clean_value(chars)
            #}
            # We have a key, but no value, and this isn't a random thing
            elif (k != None and v == None and not contains(reserved, chars)): #{
                # Check if we're in a quote
                if (not in_quote and chars.startsWith('"') and not chars.endsWith('"')):#{
                    #print('starting quote', chars)
                    in_quote = not in_quote
                    quoted.append(chars.slice(1))
                    continue
                #}
                elif (in_quote and not chars.endsWith('"')):#{
                    #print('continueing quote', chars)
                    quoted.append(chars)
                    continue
                #}
                elif (in_quote and chars.endsWith('"')):#{
                    quoted.append(chars.slice(0, -1))
                    chars = ' '.join(quoted) 
                    #print('ending quote', chars)
                    quoted = []
                    in_quote = False
                #}
                v = self.clean_value(chars) 
            
            if (k != None and v != None): #{

                # Cast
                v = self.clean_value(v)

                # Dictify if necessary
                if (isinstance(v, (list, tuple))):#{
                    v = self.dictify(v)
                #}

                if (isinstance(k, (datetime.datetime, datetime.date))):#{
                    # Cast keys that are datetimes to string, so our json encode works (plus we don't need them as dts really)
                    k = k.isoformat()
                #}

                yield (k, v)

                k = None
                v = None
            #}
        #}
    #}

    # Quick regexp for easy blocks. Add in \= to also match k,v but can be annoying
    def magic_replace(self, matchobj):#{
        #print(matchobj.group(0))
        g = matchobj.group(0).strip().replace('{', '').replace('}', '')
        new_ph_key = self.set_placeholder(g)
        return new_ph_key
    #}

    def parse(self, t=None):#{
        if (t == None): #{
            t = self.t
        #}

        # Remove comments
        cleaned = []
        for line in t.split("\n"):#{
            if (contains(line, '#')): #{
                p = line.partition('#')
                cleaned.append(p[0])
            #}
            else: #{
                cleaned.append(line)
            #}
        #}
        t = "\n".join(cleaned)

        t = t.replace('}', ' } ').replace('{', ' { ').replace('=', ' = ').replace("\n", " ")

        # Remove multiple spaces
        t = ' '.join(t.split())

        # Replace easily matched braces with placeholders
        # Replace each match with a built in placeholder
        # Loop until we have no more matches
        while (contains(t, '{')): #{
            nt = self.match_braces.sub(self.magic_replace, t)

            if nt == t: # No more matches/replacements were made
                break

            t = nt
        #}

        # Use string manipulation for the remainder
        while (contains(t, '{')): #{
            t = self.gen2(t)
        #}

        # Now parse through t, while replacing the placeholders
        comp = {}
        used_keys = []
        for k, char in self.gen(t):#{

            # Sometimes we awesomely use the same key name
            if (contains(used_keys, k)): #{
                if (isinstance(comp[k], list)):#{
                    comp[k].append(char)
                #}
                else: #{
                    comp[k] = [comp[k], char]
                #}
            #}
            else: #{
                comp[k] = char
            #}

            used_keys.append(k)
        #}
        # Convert list of tuples into dictionary
        return comp
    #}

    def resolve_placeholder(self, phkey):#{
        """
        Resolve recursively
        """
        if (contains(self.placeholders, phkey) == False): #{
            raise KeyError('Unknown placeholder: {0}'.format(phkey))
        #}

        ph = self.placeholders[phkey]

        if (contains(ph, '=')): #{
            # Normal
            #print('normal', ph)
            v = self.gen(ph)
            v = list(map(self.clean_value, v))
        #}
        elif (ph.replace(" ", "").isdigit()):#{
            # Contains only numbers or spaces or decimals (just numbers for now, parse decimals later)
            v = self.parse_number_list(ph)
        #}
        elif (ph.replace(" ", "").isalnum()):#{
            # Probably a list of say tags, just straight text
            # But might also be placeholders
            stack = []

            for val in filter(lambda x: len(x) > 0, ph.split(' ')):#{
                val = jstr(val) #JSDEL
                if (val.startsWith('placeholder')):#{
                    val = self.resolve_placeholder(val)
                #}
                #print('VAL VAL VAL', val)
                # todo: possibly don't want to clean_val, or if a list is like [a b c no] it'll try to cast it to bool
                # so just keep as strings/ints
                stack.append(val)
            #}
            v = stack
        #}
        elif (ph.count('"') % 2 == 0): #{
            # If an even number of quotes
            v = self.parse_str_list(ph)
        #}

        # Does this contain more placeholders?
        return v
    #}

    def dictify(self, obj):#{
        comp = {}
        if (len(obj) == 0): #{
            # Could be an empty list for some stupid reason
            return obj
        #}

        test = obj[0]

        if (isinstance(test, (str, int))):#{
            # Don't dictify list of items. Pray there aren't lists of numbers with internal dicts, seems like they're mostly
            # k=v, k2=v2, k3={ a=1 } which would work anyway
            return obj
        #}

        if (isinstance(test, list)):#{
            # Keep going deeper

            mklist = []
            for _, item in enumerate(obj):#{
                #print('zbop')
                vals = self.dictify(item)
                mklist.append(vals)
            #}
            return mklist
        #}

        if (isinstance(test, tuple)):#{
            # List of tuples, hopefully. squash into dict
            comp = { k:None for k, v in obj }
            #print('testcomp', comp)
            for _, item in enumerate(obj):#{
                #print('type', item, type(item))
                if (comp[item[0]] == None): #{
                    comp[item[0]] = item[1]
                #}
                elif (isinstance(comp[item[0]], list) == False):#{
                    comp[item[0]] = [comp[item[0]]]
                    comp[item[0]].append(item[1])
                #}
                else: #{
                    comp[item[0]].append(item[1])
                #}
            #}
        #}

        if (comp != {}): #{
            return comp
        #}
        else: #{
            return obj
        #}
    #}

    def parse_str_list(self, s):#{
        """
        Contains an even number of quotes, and no equals sign. Split on quotes, remove any empty elements

        eg:
        "Conquest of Paradise" "Wealth of Nations" "Res Publica" "Art of War" "Rights of Man" "Mandate of Heaven" "Third Rome"
        """
        stack = []
        for item in self.quote_splitter.split(s):#{
            # Split out the items that are quoted
            if (contains(item, '"') == False): #{
                # now just a normal string with n items
                listed = filter(lambda x: len(x.strip()) > 0, item.split(' '))
                stack.extend(list(map(self.clean_value, listed)))
            #}
            else: #{
                # Quoted part, so use the whole thing
                stack.append(self.clean_value(item))
            #}
        return stack
    #}

    def parse_number_list(self, s):#{
        """
        List of either ints or decimals
        """
        flist = list(map(int, filter(lambda x: len(x) > 0, s.split(' '))))
        #JS flist = 
        return flist
    #}

    def parse_number(self, s):#{
        """
        '0.0000' -> 0
        '-1.000' -> -1
        '-5.124' -> Decimal('-5.124')
        '1.1.12' -> '1.1.12'
        """
        num = s

        if (num.count('.') == 1):#{
            # Check if we can round it
            p = num.partition('.')
            if (int(p[2]) == 0): #{
                num = int(p[0])
            #}
            else: #{
                num = Decimal(num)
            #}
        #}
        elif (num.count('.') > 1): #{
            # Possibly a dummy date like 1.1.1, just return
            pass
        #}
        else: #{
            try:
                num = int(num)
            except ValueError:
                num = s
        #}
        return num
    #}

    def clean_value(self, val):#{ 
        #print('cleaning ', val)
        if (isinstance(val, str)):#{
            val = jstr(val) #JSDEL
            if (val.startsWith('"') and val.endsWith('"')):#{ // Remove unnecessary quotes
                val = val.slice(1,-1)
            #}
            elif (val.isdigit()):#{ // If it's all integers
                val = int(val)
            #}
            elif (val == 'no'): #{ //Bool casting
                val = False
            #}
            elif (val == 'yes'): #{
                val = True
            #}
            else:#{
                # If it looks like a date
                datesearch = self.match_date.search(val)
                if (datesearch != None):#{
                    val = to_date(*list(map(int, datesearch.groups())))
                #}
                # If it looks like a decimal, or list of them
                elif (self.match_num_list.match(val)):#{
                    mklist = []
                    for num in val.split():#{

                        v = self.parse_number(num)

                        mklist.append(v)

                    # Switch back to single if possible
                    if (len(mklist) == 1): #{
                        val = mklist[0]
                    #}
                    else: #{
                        val = mklist
                    #}
                    #print('MATCHED LIST THANG:', val, type(val))
                #}

        if (isinstance(val, list)):#{
            if (len(val) == 0): #{
                return val
            #}

            if (str(val[0]).isdigit()):#{
                val = list(map(int, val))
            #}
            elif (isinstance(val[0], str)):#{
                # Probably str, remove quotes
                val = list(map(lambda x: x.strip('"'), val))
            #}
        #}
        return val
    #}
#}
