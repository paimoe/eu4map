import { Component, OnInit, Output, EventEmitter, Input, OnChanges, SimpleChanges } from '@angular/core';
import { DataService } from '../app.services';

@Component({
  selector: 'app-details',
  templateUrl: './details.component.html',
  styleUrls: ['./details.component.css']
})
export class DetailsComponent implements OnInit, OnChanges {
  
  allowZoom = true;
  @Output() onSetting = new EventEmitter();
  @Input() provinceID: number = 0;
  
  constructor(public dataStore: DataService) { }
  
  ngOnChanges(changes: SimpleChanges) {
    console.log('DETAIL UPDATE', changes);
    // Probably just the province id selected lul
    if (this.provinceID != 0) {
      this.showDetail();
    }
  }
  
  ngOnInit() {
    console.log('details compy');
  }
  
  setAllowZoom() {
    console.log('setAllowZoom()');
    this.allowZoom = !this.allowZoom;
    // Emit this up
    this.onSetting.emit(this.allowZoom);
  }
  
  showDetail() {
    // Somehow get global info 
    console.log('showing detail of selected province');
    // Hopefully it exists
    let province = this.dataStore.provinces[this.provinceID];
    console.log(this.provinceID, province);
  }

}
