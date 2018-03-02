import { Component, OnInit, Output, EventEmitter, Input, OnChanges, SimpleChanges, OnDestroy } from '@angular/core';
import { DataService, Filters } from '../app.services';
import { Subscription } from 'rxjs/Subscription';

import * as _ from 'underscore';

@Component({
  selector: 'app-details',
  templateUrl: './details.component.html',
  styleUrls: ['./details.component.css']
})
export class DetailsComponent implements OnInit, OnChanges, OnDestroy {
  
  allowZoom = true;
  @Output() onSetting = new EventEmitter();
  @Output() onFilter = new EventEmitter();
  @Input() provinceID: number = 0;
  selectedProvince: any = {};
  sp: any = {}; // just a shorthand
  sCountry: any = {};
  countryInfo: any = {};
  
  filtersub: Subscription;

  //data-tooltip: any;
  
  constructor(public dataStore: DataService, public _filters: Filters) { }
  
  ngOnChanges(changes: SimpleChanges) {
    //console.log('DETAIL UPDATE', changes);
    // Probably just the province id selected lul
    if (this.provinceID != 0) {
      this.showDetail();
    }
  }
  
  ngOnDestroy() {
    this.filtersub.unsubscribe();
  }
  
  ngOnInit() {
    //console.log('details compy');
    this.filtersub = this._filters.obsFilter.subscribe(item => this.test(item))
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
  
  showDetail() {
    // Hopefully it exists
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
    this.calculateTag(this.sCountry['tag']);

    province['culturegroup'] = undefined;
    // Find culture group
    _.each(this.dataStore.game['cultures'], (val, idx) => {
      if (val.includes(province['culture'])) {
        province['culturegroup'] = idx;
      }
    });

    console.log('cg,', province)

    // Prettier
    //province['culture'] = this.capitalize(province['culture'])

    this.selectedProvince = province;
    this.sp = province;
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
    
    this.countryInfo = {};
    this.countryInfo['provs'] = p;
    this.countryInfo['totalDev'] = _.reduce(p, (a, b) => a + +b['tax'] + +b['prod'] + +b['man'], 0); // sum the dev
    //console.log(this.countryInfo);
  }

}
