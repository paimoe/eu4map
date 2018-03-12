import { Component, OnInit, Output, EventEmitter, Input, OnChanges, SimpleChanges, OnDestroy } from '@angular/core';
import { DataService, Filters, Actions } from '../app.services';
import { Subscription } from 'rxjs/Subscription';

import * as _ from 'underscore';

@Component({
  selector: 'app-details',
  templateUrl: './details.component.html',
  styleUrls: ['./details.component.css']
})
export class DetailsComponent implements OnInit, OnChanges, OnDestroy {
  
  allowZoom = true;
  ds: DataService;
  @Output() onSetting = new EventEmitter();
  @Output() onFilter = new EventEmitter();
  @Input() provinceID: number = 0;
  selectedProvince: any = {};
  sp: any = {}; // just a shorthand
  sCountry: any = {};
  countryInfo: any = {};
  tnode: any = {};

  show: string = 'none'; // which detail panel to show
  
  filtersub: Subscription;
  actionsub: Subscription;

  //data-tooltip: any;
  
  constructor(public dataStore: DataService, public _filters: Filters, public actions: Actions) { }
  
  ngOnChanges(changes: SimpleChanges) {
    //console.log('DETAIL UPDATE', changes);
    // Probably just the province id selected lul
    if (this.provinceID != 0) {
      //let province = this.dataStore.provinces[this.provinceID];
      //console.log('provid', this.provinceID)
      if (this._filters.tradenodes) {
        // show trade details
        this.showTradeNode();
      } else {
        this.showDetail();
      }
    }
  }
  
  ngOnDestroy() {
    this.filtersub.unsubscribe();
  }
  
  ngOnInit() {
    //console.log('details compy');
    this.filtersub = this._filters.obsFilter.subscribe(item => this.test(item))
    this.actionsub = this.actions.obsAction.subscribe(item => this.action_in(item));

    this.ds = this.dataStore;
  }

  action_in(item) {
    console.log('got new action in details: ', item);
    if (item !== null) {
      let sp = item[0].split('_');
      if (sp[0] == 'details') {
        switch (sp[1]) {
        }
      }
    }
  }
  action_out(field, value) {
    console.log('sending action from details', field, value)
    this.actions.commit(field, value);
  }
  
  test(item) {
    //6console.log('TEST NEW FILTER', item, this._filters.hre);
  }

  unselected() {
    //console.log('unselected', this.sp, _.isEmpty(this.sp),this.sp == {})
    return _.isEmpty(this.sp);
  }
  
  setAllowZoom() {
    //console.log('setAllowZoom()');
    this.allowZoom = !this.allowZoom;
    // Emit this up
    this.onSetting.emit(this.allowZoom);
  }

  capitalize(s) {
    return s.charAt(0).toUpperCase() + s.slice(1);
  }

  selection(type, which) {
    //console.log('selection()', type, which);
    this.action_out('map_zoomTo', which);
  }
  
  showDetail() {
    // Hopefully it exists
    this.show = 'province';
    let province = this.dataStore.provinces[this.provinceID];

    // Flatten since our parser is trash
    province['cores'] = [].concat(...province['cores'])
    // Primary core first

    if (province.owner !== null) {
      let country = this.dataStore.countries[province.owner];
      this.sCountry = country;
    } else {
      this.sCountry = false;
    }

    // check if is province
    province['nonp'] = province.wasteland || province.ocean || province.sea || province.lake;
    province['owned'] = province['owner'] !== null;
    //console.log('c', province);

    if (province['owned']) {
      this.calculateTag(this.sCountry['tag']);
    }

    province['culturegroup'] = undefined;
    // Find culture group
    _.each(this.dataStore.game['cultures'], (val, idx) => {
      //console.log('val', val);
      
        if (_.contains(province['culture'], val)) {
          province['culturegroup'] = idx;
        }
      
    });

    console.log('cg,', province)

    // Prettier
    //province['culture'] = this.capitalize(province['culture'])

    this.selectedProvince = province;
    this.sp = province;
  }

  showTradeNode() {
    let province = this.dataStore.provinces[this.provinceID];
    console.log('show trade node data', province.tradenode.name, this.ds.tradenodes[province.tradenode.name]);
    this.show = 'tradenode';

    this.tnode.name = province.tradenode.name;
  }
  
  filter(which, val) {
    console.log('Setting filter', which, val);
    this._filters.toggle(which, val);
  /*

    call setFilter() on filtercomponent?
    console.log('filter by this type', type)
    if (typeof this.filters[type] === "boolean") {
      this.filters[type] = !this.filters[type];
    }
    this.onFilter.emit();*/
  }
  
  calculateTag(tag) {
    let p = _.filter(this.dataStore.provinces, (x) => x['owner'] == tag);
    
    this.countryInfo = this.sCountry;
    this.countryInfo['provs'] = p;
    this.countryInfo['totalDev'] = _.reduce(p, (a, b) => a + +b['tax'] + +b['prod'] + +b['man'], 0); // sum the dev
    //console.log(p);
    let capital = _.filter(p, (x) => x.id == this.sCountry['capital'])[0];
    this.countryInfo['_capital'] = capital === undefined ? {} : capital;
    //console.log(this.countryInfo);

    // Do we need info on their subjects?
    this.countryInfo['subject_data'] = !_.isEmpty(this.countryInfo.subjects) || this.countryInfo.subject_of !== null;
    this.countryInfo['has_subjects'] = !_.isEmpty(this.countryInfo['subjects']);

    //console.log('subjdata', _.isEmpty(this.countryInfo.subjects), this.countryInfo.subject_of);
  }

  countryname(tag) {
    // Get country info for this tag
    //let country = this.ds.countries[tag];
    //return country.name;
    if (!_.isEmpty(tag)) {
      return this.dataStore.countries[ tag ].name;
    }
    return '';
  }
  flag(tag) {
    if (tag.length == 3) {
      // return url
      return `assets/i/flags/32/${tag}.png`;
    }
  }
  subjects(subjlist) {
    if (!_.isEmpty(this.countryInfo) && this.countryInfo['has_subjects']) {
      let c = this.countryInfo;
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
  }

}
