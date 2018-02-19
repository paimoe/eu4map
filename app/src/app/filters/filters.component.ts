import { Component, OnInit } from '@angular/core';
import { DataService, Filters } from '../app.services';

@Component({
  selector: 'app-filters',
  templateUrl: './filters.component.html',
  styleUrls: ['./filters.component.css']
})
export class FiltersComponent implements OnInit {
  
  _defaults: any;
  
  exclusives: string[] = ['hre', 'releasable', 'tradenodes', 'formable'];
  
  constructor(public dataStore: DataService, public _filters: Filters) {

  }

  ngOnInit() {
    // load like filters.json
  }
  
  setFilter(choice, value = true, addsubfilter = false) {
    console.log('FilterComponent', choice, value);
    if (choice === 'none') {
      this._filters.reset();
    } else {
      this._filters.toggle(choice, value);
    }
    
    if (addsubfilter === true) {
      console.log('add subfilter');
      // load from some json file who knows
    }
    
    //this.filtersChanged = !this.filtersChanged; // toggle to force refresh
    //console.log('FILTERS', choice);
  }
}
