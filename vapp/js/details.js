

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
            //console.log('selected tag', type, tag);
            let cap = this.$store.getters.country(tag);
            if (type == 'reformable') {
                // just want to highlight basically
                this.$store.commit('highlight', cap.cores);
            } else {
                // Get capital and set selected
                this.$store.commit('selected_p', cap.capital);
            }
        },
        setTarget: function(which) {
            this.$store.commit('setTarget', which);
        },
        filter: function(type, specific) {
            //console.log('apply map filter', type, specific);
            this.$store.commit('filter', {'which': type, 'opts': specific});
        },
        countryname: function(tag) {
            let c = this.$store.getters.country(tag);
            return c.name + ' (' + tag + ')';
        },

        flag(tag) {
            if (tag.length == 3) {
                // return url
                return `assets/i/flags/32/${tag}.png`;
            }
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
            //console.log('subj', this.sCountry);
            //console.log('subjdata', _.isEmpty(this.countryInfo.subjects), this.countryInfo.subject_of);  
        },
        subjects(subjlist) {
            if (!_.isEmpty(this.sCountry) && this.sCountry['has_subjects']) {
              let c = this.sCountry;
              let subjs = [];
              let imgs = {
                'personal_union': ['Personal Union', 'Personal_union.png'],
                'vassal': ['Vassal', 'Vassal.png'],
                'tributary_state': ['Tributary', 'Tributary.png'],
                'march': ['March', 'March.png'],
                'daimyo_vassal': ['Daimyo', 'Vassal.png'],
                // colony Colonial.png
              };
              //console.log(c, strs);
              for (let s of c['subjects']) {
                //let t = imgs[s['subject_type']];
                let n = this.countryname(s['second']);
                subjs.push([imgs[s['subject_type']], n, s['second']]);
              }
              return subjs;
            } 
            return ['no subjects'];
        },
        showPane(which) {
            //console.log('show', this.$store.getters.selected_type)
            return _.contains(this.$store.getters.selected_type, which);
        },
        dev_total(tag) {
            return this.$store.getters.country_dev(tag);
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
            //console.log(this.sCountry);

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
        sCouantry() {
            // hrm
            return {
                name: 'country2'
            }
        },
        show() {
            //console.log('show', this.$store.getters.selected_type)
            return this.$store.getters.selected_type;
        },
        filterStr() {
            return fSerialize(this.$store.state.filters);
        },
        // which achievement was selected
        ach() {
            let dets = this.$store.getters.achievement();
            return dets;
        },
        tradenodedata() {
            let nodes = this.$store.getters.tradenodes;
            let ret = [];
            //console.log('nodz',nodes['zanzibar'])
            _.each(nodes, (item, idx) => {
                let p = {
                    'name': idx.title(),
                    'color': 'rgb(' + item.color.join(',') + ')',
                    'inland': item.inland === true,
                };

                /*
                if ('incoming' in item) {
                    p['in'] = _.pluck(item.incoming, 'name').map(x => x.title());
                }*/
                if ('outgoing' in item) {
                    if (Array.isArray(item.outgoing)) {
                        p['out'] = _.pluck(item.outgoing, 'name').map(x => x.title());
                    } else {
                        p['out'] = [item.outgoing['name'].title()];
                    }
                }

                ret.push(p);
            })
            return _.sortBy(ret, x => x.name);
        },
        reformable() {
            return _.sortBy(this.$store.getters.dormant, 'name');
        }
    }

});