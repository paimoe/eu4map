

Vue.component('detailspane', {
    template: '#detailspane',
    data: function() {
        return {
            _selected: 0,
            tnode: {
                name: 'no trade node'
            },
            sCountry: false,
        }
    },
    methods: {
        selection: function(type, tag) {
            console.log('selected tag', type, tag);
        },
        filter: function(type, specific) {
            console.log('apply map filter', type, specific);
        },
        countryname: function(tag) {
            let c = this.$store.getters.country(tag);
            return c.name + ' (' + tag + ')';
        },
        calculateTag: function(tag) {
            let p = this.$store.getters.provinces_of(tag);
            
            this.sCountry['provs'] = p;
            this.sCountry['totalDev'] = _.reduce(p, (a, b) => a + +b['tax'] + +b['prod'] + +b['man'], 0); // sum the dev
            //console.log(p);
            let capital = _.filter(p, (x) => x.id == this.sCountry['capital'])[0];
            this.sCountry['_capital'] = capital === undefined ? {} : capital;
            //console.log(this.countryInfo);

            // Do we need info on their subjects?
            this.sCountry['subject_data'] = !_.isEmpty(this.sCountry.subjects) || this.sCountry.subject_of !== null;
            this.sCountry['has_subjects'] = !_.isEmpty(this.sCountry['subjects']);

            //console.log('subjdata', _.isEmpty(this.countryInfo.subjects), this.countryInfo.subject_of);  
        }
    },
    computed: {
        selected() {
            return this.$store.state.selected_p != 0;
        },
        unselected() {
            return this._selected = 0;
        },
        sp() {
            let id = this.$store.state.selected_p;

            // Get province info and stuff
            let prov = this.$store.getters.province(id);
            if (prov === undefined) {
                return {};
            }

            let ret = prov; // now extend

            ret['cores'] = [].concat(...prov['cores']);
            if (prov.owner !== null) {
                ret['sCountry'] = this.$store.getters.country(prov.owner);
            } else {
                ret['sCountry'] = false;
            }
            this.sCountry = ret['sCountry'];
            console.log(this.sCountry);

            ret['nonp'] = prov.wasteland || prov.ocean || prov.sea || prov.lake;
            ret['owned'] = prov['owner'] !== null;

            if (prov['owned']) {
              this.calculateTag(this.sCountry['tag']);
            }

            ret['culturegroup'] = undefined;
            /* Find culture group
            _.each(this.dataStore.game['cultures'], (val, idx) => {
              //console.log('val', val);
              
                if (_.contains(province['culture'], val)) {
                  province['culturegroup'] = idx;
                }
              
            });
*/
            return ret;
        },
        sCountry() {
            // hrm
            return {
                name: 'country2'
            }
        },
        show() {
            console.log('show', this.$store.getters.selected_type)
            return this.$store.getters.selected_type;
        }
    }

});