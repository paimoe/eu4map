import { Component, OnInit, Output, EventEmitter, Input, OnChanges, SimpleChanges } from '@angular/core';
import { DataService, Filters } from '../app.services';

@Component({
  selector: 'app-details',
  templateUrl: './details.component.html',
  styleUrls: ['./details.component.css']
})
export class DetailsComponent implements OnInit, OnChanges {
  
  allowZoom = true;
  @Output() onSetting = new EventEmitter();
  @Output() onFilter = new EventEmitter();
  @Input() provinceID: number = 0;
  selectedProvince = {};
  sCountry = {};
  
  constructor(public dataStore: DataService, public filters: Filters) { }
  
  ngOnChanges(changes: SimpleChanges) {
    //console.log('DETAIL UPDATE', changes);
    // Probably just the province id selected lul
    if (this.provinceID != 0) {
      this.showDetail();
    }
  }
  
  ngOnInit() {
    //console.log('details compy');
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
    let country = this.dataStore.countries[province.owner];
    console.log('c', province, country);
    this.selectedProvince = province;
    this.sCountry = country;
  }
  
  filter(type) {
    console.log('filter by this type', type)
    if (typeof this.filters[type] === "boolean") {
      this.filters[type] = !this.filters[type];
    }
    this.onFilter.emit();
  }

}
