import { Component, OnInit, Input, OnChanges, SimpleChanges } from '@angular/core';
import { DataService, Filters } from '../app.services';

@Component({
  selector: 'app-filters',
  templateUrl: './filters.component.html',
  styleUrls: ['./filters.component.css']
})
export class FiltersComponent implements OnInit {
  
  _defaults: any;
  type: string;
  ds: DataService;

  @Input() loadedReceiver: boolean;
  
  exclusives: string[] = ['hre', 'releasable', 'tradenodes', 'formable'];

  opts = {
    target: '',
    include_wasteland: false,
  };
  religions: any;
  religiongroups: any;
  
  constructor(public dataStore: DataService, public _filters: Filters) {

  }

  ngOnInit() {
    // defaults
    this.opts.target = 'provinces';
    this.opts.include_wasteland = false;
  }

  ngOnChanges(changes: SimpleChanges) {
    let key = Object.keys(changes)[0];
    if (key == 'loadedReceiver') {
      // Now we can load the filters? check.
      if (changes[key]['currentValue'] === true) {
        // 
        // Have to convert it a bit since angular sucks and can't loop an object
        let rkeys = Object.keys(this.dataStore.game['religions']);
        let religiongroups = [];
        for (let prop of rkeys) {
          religiongroups.push(prop);
        }
        //this.religionlist = this.dataStore.game['religions'];
        //console.log(religionlist);
        this.religions = this.dataStore.game['religions'];
        this.religiongroups = religiongroups.sort();
      }
    }
  }

  setFilter(choice, value = true, addsubfilter = false) {
    //console.log('FilterComponent', choice, value);
    if (choice === 'none') {
      this.type = null;
      this._filters.reset();
    } else {
      this._filters.toggle(choice, value);
    }
    
    //this.filtersChanged = !this.filtersChanged; // toggle to force refresh
    //console.log('FILTERS', choice);
  }

  filterType(which) {
    if (this.type == which) {
      this.type = null;
      this._filters.hideFilterDetails(which);
    } else {
      this.type = which;
      // we selected a filter type, so show the dropdown, and show the details panel differently
      this._filters.showFilterDetails(which);
    }
  }

  setTarget(which) {
    // Are we targetting 'provinces' or 'countries'
    this.opts.target = which;
  }

  setOption(opt) {
    // Toggle option
    this.opts[opt] = !this.opts[opt];
  }

}
