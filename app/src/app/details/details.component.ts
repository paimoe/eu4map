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
  selectedProvince = {};
  sCountry = {};
  countryInfo = {};
  
  filtersub: Subscription;
  
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
    console.log('TEST NEW FILTER', item, this._filters.hre);
  }
  
  setAllowZoom() {
    //console.log('setAllowZoom()');
    this.allowZoom = !this.allowZoom;
    // Emit this up
    this.onSetting.emit(this.allowZoom);
  }
  
  showDetail() {
    // Hopefully it exists
    let province = this.dataStore.provinces[this.provinceID];
    this.selectedProvince = province;
    if (province.owner !== null) {
      let country = this.dataStore.countries[province.owner];
      this.sCountry = country;
    } else {
      this.sCountry = false;
    }

    // check if is province
    province['nonp'] = province.wasteland || province.ocean || province.sea;
    console.log('c', province);
    this.calculateTag(this.sCountry['tag']);
  }
  
  filter(type) {/*
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
    console.log(this.countryInfo);
  }

}
