import { Component, SimpleChanges, OnChanges, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { DataService, Filters } from './app.services';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit, OnChanges {
  
  private data_paths = [];
  
  title = 'EU4 Map';
  settings = {};
  allowZoom = true;
  provinceID = 0;
  filtersChanged = false;
  
  data = {}; // data of all the stuff from the json bro
  data_src = {/*'paths': 'eu4map.json', not yet, loaded in map component */'provinces': 'provdata.json', 'countries': 'countries.json'};
  
  constructor(private http: HttpClient, public dataStore: DataService, public filters: Filters) {
    this.settings['allowZoom'] = true;
    console.log('DATA STORE???', this.dataStore, dataStore);
    
  }
  
  ngOnInit() {
    console.log('init entire app, load all the data');
    
    // Ideally cache in IndexedDB, but we can wait
    var self = this;
    for (let k in this.data_src) {
      //console.log('load ', self.data_src[k], ' into ', k);
      this.http.get('/assets/' + self.data_src[k])
        .subscribe(function(data) {
          // success
          self.data[k] = data;
          self.dataStore[k] = data;
          console.log('loaded ', k);
        }, function(err) {
          // error
          console.log('error loading json: ', err);
        });
    }
    
  }
  
  save() {
    console.log('called save()');
  }
  
  ngOnChanges(changes: SimpleChanges) {
    console.log('changes', changes);
  }
  
  changeSetting(evt) {
    console.log('changeSetting()');
    /*
    switch(evt['type']) {
      case 'allowZoom':
        this.settings['allowZoom'] = evt['value'];
        this.allowZoom = evt['value'];
        break;
    }*/
    
    // Try to fudge the digest https://stackoverflow.com/a/32377904/858969
    this.settings = JSON.parse(JSON.stringify(this.settings));
    this.settings['allowZoom'] = !this.settings['allowZoom'];
    //this.settings['allowZoom'] = !this.settings['allowZoom'];
    //console.log('now zoom', this.settings['allowZoom']);
  }
  
  changeFilter(evt) {
    console.log('changeFilter()', this.filters);
    this.filtersChanged = !this.filtersChanged;
  }
  
  provinceSelected(provid) {
    console.log('selected a province', provid);
    this.provinceID = provid;
  }
  
  setFilters(choice) {
    if (choice === 'none') {
      this.filters.reset();
    } else if (typeof this.filters[choice] === "boolean") {
      this.filters[choice] = !this.filters[choice];
    }
    this.filtersChanged = !this.filtersChanged; // toggle to force refresh
    console.log('FILTERS', choice);
  }
  
}
