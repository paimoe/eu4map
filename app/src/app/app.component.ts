import { Component, SimpleChanges, OnChanges, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { DataService, Filters } from './app.services';
import * as _ from 'underscore';

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
  //filtersChanged = false;
  redrawMap = false; // Sent to map component
  loaded = false;
  
  data = {}; // data of all the stuff from the json @todo: needed?
  data_src = {'paths': 'eu4map.json', 'provinces': 'provdata.json', 'countries': 'countries.json', 'tradenodes': 'tradenodes.json', 'game': '_all.json', 'save': '_day1.json'};
  
  constructor(private http: HttpClient, public dataStore: DataService, public filters: Filters) {
    this.settings['allowZoom'] = true;
  }
  
  ngOnInit() {
    console.log('init entire app, load all the data');
    
    // Ideally cache in IndexedDB, but we can wait
    var self = this;
    var dcount = Object.keys(self.data_src).length;
    var allFiles = [];
    for (let k in this.data_src) {
      allFiles.push(this.http.get('assets/' + self.data_src[k]).toPromise());
    }
    Promise.all(allFiles).then(function(datas) {
      //console.log('finished all promises', datas);
      
      // Manually for now
      self.dataStore.paths      = datas[0];
      self.dataStore.provinces  = datas[1];
      self.dataStore.countries  = datas[2];
      self.dataStore.tradenodes = datas[3];
      self.dataStore.game       = datas[4]; // Things in data/_all.json
      self.dataStore.save       = datas[5]; // Example save game from day1 with diplomacy set

      self.ds = self.dataStore;
      
      // Get all unique like religions/cultures?

      self.loaded = true;
      self.redrawMap = true;

      self.applySave();
      
    }, function(err) {
      console.log('err', err);
    })
  }
  
  save() {
    console.log('called save()');
  }
  
  ngOnChanges(changes: SimpleChanges) {
    console.log('changes', changes);
  }
  
  changeSetting(evt) {
    //console.log('changeSetting()');
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
  
  provinceSelected(provid) {
    //console.log('selected a province', provid);
    this.provinceID = provid;
  }
  
  setFilters(choice, value, addsubfilter = false) {
    return;/*
    if (choice === 'none') {
      this.filters.reset();
    } else {
      this.filters.toggle(choice, value);
    }
    
    if (addsubfilter === true) {
      console.log('add subfilter');
      // load from some json file who knows
    }
    
    this.filtersChanged = !this.filtersChanged; // toggle to force refresh
    //console.log('FILTERS', choice);
    */
  }

  applySave() {
    // Map diplomacies + others onto countries
    console.log('savedata', this.dataStore.save);
    for (let cid in this.dataStore.countries) {
      var c = this.dataStore.countries[cid];
      c['subject_of'] = null;
      c['subjects'] = [];
    }
    //var deps = ['']
    _.each(this.dataStore.save.diplomacy, (kind, idx) => {
      //console.log('kind', kind, idx);
      _.each(kind, (data, idx2) => {
        //this.dataStore.countries
        if (idx == 'dependency') {
          // Get both countries
          this.ds.countries[data.first].subjects = this.ds.countries[data.first].subjects || [];
          this.ds.countries[data.first].subjects.push(data);
          this.ds.countries[data.second].subject_of = data;
        }
      });
    });
  }
  
  parseSaveFile(savestr) {

  }

}
