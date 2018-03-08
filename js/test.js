"use strict";

/*
todo: list of ints/decimals not converted to numeral
*/

let _ = require('underscore');
let numeral = require('numeral');
let moment = require('moment');
//let co = require('co');
let fs = require('fs');

var len = val => val.length;
var isinstance = (val, t) => typeof(val) === t;
var str = val => val.toString();
var contains = (haystack, needle) => _.contains(haystack, needle);

var is_str = s => _.isString(s);
var is_list = s => _.isArray(s);
var is_date = s => _.isDate(s);
var is_int = s => _.isNumber(s);
var is_obj = s => _.isObject(s);

// Prototypes
/*Array.prototype.append = function(v) {
    this.push(v);
};*/
String.prototype.startswith = function(c) {
    return this.startsWith(c);
};
String.prototype.endswith = function(c) {
    return this.endsWith(c);
};
String.prototype.isdigit = function() {
    return /^\d+$/.test(this);
};
String.prototype.isalnum = function() {
    return /^[\w\d]+$/.test(this);
};
String.prototype.partition = function(s) {
    return this.split(s);
}
String.prototype.count = function(s) {
    // return regex count https://stackoverflow.com/questions/881085/count-the-number-of-occurrences-of-a-character-in-a-string-in-javascript
    //console.log(("str1,str2,str3,str4".match(/,/g) || []).length)
    //console.log('calling count with', s, this)
    let m = this.match(new RegExp(s, 'g') || []);
    return m === null ? 0 : m.length;
}

/* PASTE OUTPUT BELOW */
class ParseFile {
    /*/
    Pass in a string && return a dict

    File loading/saving/caching etc === handled above this
    /*/

    constructor(t){ 
        this.t = t
        this.rdepth = 0
        this.placeholders = {}

        // Match braces that contain these values { whitespace, string, quotes, periods (for decimals), = (for k/v (OPTIONAL)), negative signs
        // single quotes (for peoples names: Kai-Ka'us)
        this.match_braces = /\{([\w\s\"\.\=\-\']*?)\}/g
        this.match_date = /(\d{4})\.(\d+)\.(\d+)/
        // Should match a list of numbers, including decimals && negatives
        this.match_num_list = /^[\s\d\.\-]+$/
        this.quote_splitter = /("[^"]+")/
    }
    set_placeholder (txt){ 
        this.rdepth += 1
        var key = 'placeholder' + str(this.rdepth)
        this.placeholders[key] = txt

        return key
    }
    gen2(s){
        /*/
        Split into first encountered }, then match to opening {
        Replace with a placeholder value
        /*/
        //console.log('gen2', s);
        if (contains(s, '}') == false){ 
            return s
        }

        // Split string on first close brace, then backtrack
        var i = s.indexOf('}');
        var sp = [s.slice(0, i), s.slice(i + 1)]
        //console.log('sp', sp);

        var init = sp[0]

        var pieces = init.split(/\{/g);
            //console.log('pieces', pieces);

        var block = pieces[pieces.length - 1];
        //console.log('block', block);

        var innermost = block;

        var remainder_left = pieces.slice(0, pieces.length - 1).join(' { ')//block[0]

        var phkey = this.set_placeholder(innermost)

        var remainder_right = sp[1]

        //console.log("\n\n\nleft:", remainder_left, "\nphkey", phkey, "\nright:", remainder_right, "\n\n\n")


        return remainder_left + phkey + remainder_right
    }
    * gen(s){
        // no idea really
        //co(function* () {
            // Run through string per character
            // Generator
            var k = undefined
            var v = undefined

            var reserved = ['{', '}', '=', '"', '']
            var ignore = ['EU4txt', '}']

            var subblock = false
            var collect = []

            var in_quote = false
            var quoted = []
            
            // Can't use _.each or it won't be yieldable
            var split_on_space = s.split(/\s+/g)
            for (let idx in split_on_space) {
                var chars = split_on_space[idx];
                console.log('charz', k, chars);
                // Skip ones we're filtering out
                if (chars.startsWith('placeholder')){
                    var v = this.resolve_placeholder(chars)
                }

                // Skip these
                if (contains(ignore, chars) || contains(reserved, chars)){
                    continue
                }

                // We have no key, so probably need it
                if (k == undefined){
                    var k = this.clean_value(chars)
                }
                // We have a key, but no value, && this isn't a random thing
                else if (k != undefined && v == undefined && ! contains(reserved, chars)) {
                    // Check if we're in a quote
                    //console.log('aquiring value', k, chars);
                    if (! in_quote && chars.startsWith('"') && ! chars.endsWith('"')){
                        //prnumeral('starting quote', chars)
                        var in_quote = ! in_quote
                        quoted.push(chars.slice(1))
                        continue
                    }
                    else if (in_quote && ! chars.endsWith('"')){
                        //prnumeral('continueing quote', chars)
                        quoted.push(chars)
                        continue
                    }
                    else if (in_quote && chars.endsWith('"')){
                        quoted.push(chars.slice(0, -1))
                        var chars = quoted.join(' ')
                        //prnumeral('ending quote', chars)
                        var quoted = []
                        var in_quote = false
                    }
                    var v = this.clean_value(chars) 
                }
                
                if (k != undefined && v != undefined) {

                    // Cast
                    var v = this.clean_value(v)

                    // Dictify if necessary
                    if (is_list(v)){
                        var v = this.dictify(v)
                    }

                    if (is_date(k)){
                        // Cast keys that are datetimes to string, so our json encode works (plus we don't need them as dts really)
                        //var k = k.isoformat()
                        console.log('do nothing? they will be moments()',k);
                    }

                    yield [k,v]

                    var k = undefined
                    var v = undefined
                }
            }

        //})
        //.then((val) => {
         //   console.log('yieleded?', val);
        //})
    }

    // Quick regexp for easy blocks. Add in \= to also match k,v but can be annoying
    magic_replace(matchobj){
        //prnumeral(matchobj.group(0))
        //console.log('magic_replace', matchobj)
        var g = matchobj.replace('{', '').replace('}', '').trim()
        var new_ph_key = this.set_placeholder(g)
        return new_ph_key
    }

    parse(t){
        if (t == undefined) {
            var t = this.t
            this.t = t;
        }

        // Remove comments
        var cleaned = []
        _.each(t.split(/\r?\n/), line => {
            if (contains(line, '#')) {
                var p = line.split('#')
                cleaned.push(p[0])
            }
            else if (line.length == 0) {
                return;
            }
            else {
                cleaned.push(line)
            }
        });
        var t = cleaned.join("\n")

        var t = t.replace(/\}/g, ' } ').replace(/\{/g, ' { ').replace(/=/g, ' = ').replace(/\s+/, " ")
        //console.log('huhhhhh', t);

        // Remove multiple spaces
        //?var t = t.split(' ').join(' ');

        // Replace easily matched braces with placeholders
        // Replace each match with a built in placeholder
        // Loop until we have no more matches
        //var self = this;
        while (contains(t, '{')) {
            var nt = t.replace(this.match_braces, (matchobj) => this.magic_replace(matchobj))

            if (nt == t) { // No more matches/replacements were made
                break;
            }
            console.log('len', t.length);
            var t = nt
        }

        // Use string manipulation for the remainder, if any
        var i = 0;
        while (contains(t, '{')) {
            console.log('STILL CONTAINS')
            //console.log("\n\n", t, "\n\n")
            var t = this.gen2(t)
            //i++;
            //if (i == 5) { break;}
        }

        //console.log("\n\ncontains:", contains(t, "{"), "\n\n")
        
        // Now parse through t, while replacing the placeholders
        var comp = {}
        var used_keys = []

        console.log('after while2', t, "\n\n");
        for (let item of this.gen(t)) {
            console.log('item', item);

            let k = item[0]; 
            let char = item[1];

            // Sometimes we awesomely use the same key name
            if (contains(used_keys, k)) {
                if (isinstance(comp[k], list)){
                    comp[k].push(char)
                }
                else {
                    comp[k] = [comp[k], char]
                }
            }
            else {
                comp[k] = char
            }

            used_keys.push(k)
        }
        // Convert list of tuples into dictionary
        return comp
    }

    resolve_placeholder (phkey){
        /*/
        Resolve recursively
        /*/
        if (contains(Object.keys(this.placeholders), phkey) == false) {
            console.error('Unknown placeholder', phkey, contains(this.placeholders, phkey));
            console.log('------', contains(Object.keys(this.placeholders), phkey),this.placeholders['placeholder24'])
            throw "error";
        }

        var ph = this.placeholders[phkey]
        console.log('loading placeholder', phkey);
        var nospace = /\s+/g
        if (contains(ph, '=')) {
            // Normal
            //prnumeral('normal', ph)
            console.log('checking first block', ph)
            var v = {};
            for (let item of this.gen(ph)) {
                let k = item[0];
                let char = item[1];
                // Hav eto consume the entire generator
                console.log('kkkkkk char', k, char)
                v[k] = this.clean_value(char);
            }
            //var v = this.gen(ph)
            //var v = _.map(v, this.clean_value)
        }
        else if (ph.replace(nospace, "").isdigit()){
            // Contains only numbers || spaces || decimals (just numbers for now, parse decimals later)
            var v = this.parse_number_list(ph)
            console.log('probs number list', ph, v);
        }
        else if (ph.replace(nospace, "").isalnum()){
            // Probably a list of say tags, just straight text
            // But might also be placeholders
            var stack = []
            console.log('chekcing ', ph.replace(nospace, ""), ph.replace(nospace, "").isalnum());
            _.each(_.filter(ph.split(' '), x => x.length > 0), (val, idx) => {
                if (val.startsWith('placeholder')){
                    var val = this.resolve_placeholder(val)
                }
                stack.push(val)
            })
            var v = stack
        }
        else if (ph.count('"') % 2 == 0) {
            // If an even number of quotes
            var v = this.parse_str_list(ph)
        }

        // Does this contain more placeholders?
        return v
    }

    dictify (obj){
        /*
        Convert list of objects into an object with each value in a list
        */
        //console.log('dictifying', obj)
        var comp = {}
        if (len(obj) == 0) {
            // Could be an empty list for some stupid reason
            return obj
        }

        var test = obj[0]

        if (is_str(test) || is_int(test)){
            // Don't dictify list of items. Pray there aren't lists of numbers with internal dicts, seems like they're mostly
            // k=v, k2=v2, k3={ a=1 } which would work anyway
            return obj
        }
        if (numeral.isNumeral(test)) {
            return obj;
        }

        if (is_list(test)){
            // Keep going deeper

            var mklist = []
            _.each(obj, (item, idx) => {
                //prnumeral('zbop')
                var vals = this.dictify(item)
                mklist.push(vals)
            })
            return mklist
        }

        if (is_obj(test)){
            // List of tuples, hopefully. squash into dict
            //var comp = { k {undefined for k, v in obj }
            //prnumeral('testcomp', comp)
            _.each(obj, (item, idx) => {
                //console.log('type', item, idx)
                let ks = Object.keys(item);
                _.each(ks, k => {
                    let v = item[k];
                    if (comp[k] == undefined) {
                        comp[k] = v
                    }
                    else if (!is_list(comp[k])) {
                        comp[k] = [comp[k]]
                        comp[k].push(v)
                    }
                    else {
                        comp[k].push(v)
                    }

                })
            })
        }

        if (comp != {}) {
            return comp
        }
        else {
            return obj
        }
    }

    parse_str_list (s){
        /*/
        Contains an even number of quotes, && no equals sign. Split on quotes, remove any empty elements

        eg {
        "Conquest of Paradise" "Wealth of Nations" "Res Publica" "Art of War" "Rights of Man" "Mandate of Heaven" "Third Rome"
        /*/
        var stack = []
        _.each(s.split(this.quote_splitter), (item, idx) => {
            // Split out the items that are quoted
            if (contains(item, '"') == false) {
                // now just a normal string with n items
                var listed = _.filter(item.split(' '), x => x.trim().length)
                //stack.extend(list(map(this.clean_value, listed)))
                // @todo
                stack.push(...listed)
            }
            else {
                // Quoted part, so use the whole thing
                stack.push(this.clean_value(item))
            }
        })
        return stack
    }

    parse_number_list (s){
        /*/
        List of either ints || decimals
        /*/
        //PY: var flist = list(map(int, filter(lambda x { len(x) > 0, s.split(' '))))
        var flist = [];
        _.each(s.split(' '), (val, idx) => {
            if (val.length > 0) {
                flist.push(numeral(val));
            }
        })
        return flist
    }

    parse_number (s){
        /*
        '0.0000' -> 0
        '-1.000' -> -1
        '-5.124' -> float('-5.124')
        '1.1.12' -> '1.1.12'
        */
        return numeral(s)
        /*
        var num = s

        if (num.count('.') == 1){
            var num = numeral(num);
        }
        else if (num.count('.') > 1) {
            // Possibly a dummy date like 1.1.1, just return
            
        }
        else {
            var num = numeral(num)
        }
        return num*/
    }

    clean_value (val){ 
        //prnumeral('cleaning ', val)
        if (is_str(val)) {
            if (val.startsWith('"') && val.endsWith('"')){ // Remove unnecessary quotes
                var val = val.slice(1,-1)
            }
            else if (val.isdigit()){ // If it's all integers
                //console.log('isdigit');
                var val = numeral(val)
            }
            else if (val == 'no') { //Bool casting
                var val = false
            }
            else if (val == 'yes') {
                var val = true
            }
            else{
                // If it looks like a date
                var datesearch = val.match(this.match_date)
                //console.log('datesearhc', datesearch);
                if (datesearch !== null){
                    var val = moment({y: datesearch[1], M: datesearch[2], d: datesearch[3]});
                }
                // If it looks like a decimal, || list of them
                else if (this.match_num_list.test(val)){
                    var mklist = []
                    _.each(val.split(' '), (num, idx) => {

                        var v = this.parse_number(num)

                        mklist.push(v)
                    })
                    // Switch back to single if possible
                    if (len(mklist) == 1) {
                        var val = mklist[0]
                    }
                    else {
                        var val = mklist
                    }
                    //prnumeral('MATCHED LIST THANG {', val, type(val))
                }
            }
        }

        if (is_list(val)){
            if (len(val) == 0) {
                return val
            }
            /* should already be cast
            if (typeof val[0].isdigit()){
                var val = _.map(val, x => numeral(x))
            }*/
            if (!_.isObject(val) && is_str(val[0])){
                // Probably str, remove quotes
                var val = _.map(val, x => {console.log('xxx', x);x.trim('"')})
            }
        }
        return val
    }
}
var p = new ParseFile()
var d = '';

function loadfile() {
    return fs.readFile('example_save.eu4', 'latin1', (err, data) => {
        if (err) throw err;
        //console.log(data);

        //console.log('------------------');
        d = data;
        //fp = p.parse(data);
        return data;     

    })
};
loadfile();