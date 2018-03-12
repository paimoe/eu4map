// Services maybe
import { Injectable } from '@angular/core';
import {BehaviorSubject} from 'rxjs/BehaviorSubject';

@Injectable() 
export class DataService {
  provinces: any;
  countries: any;
  paths: any;
  tradenodes: any;
  game: any;
  save: any;
}

@Injectable()
export class Actions {

  private _action = new BehaviorSubject<any>(null);
  obsAction = this._action.asObservable();
  action: string = '';
  value: string = '';

  commit(field, value) {
    this.action = field;
    this.value = value;
    this._action.next([field, value]);
  }
}

@Injectable() 
export class Filters {
  /*
  This stores the data, and loads it. when it changes, the observables are updated.
  FilterComponent only reads, and calls set()/reset() etc
  */
 
   
  // Where we store our info, when it changes, it sends out events
  private _filters = new BehaviorSubject<any>(null);
  // Observable navItem stream
  obsFilter = this._filters.asObservable();
  // service command
  changeNav(number) {
    console.log('CHANGENAV', this._filters);
    this._filters.next(number);
  };
  
  on(which) {
    // return whether this is enabled or not
  }

  showingFiltered: boolean = false;
  selectedProvince: any = 0;
  
  // map modes
  hre: boolean = false;
  releaseable: boolean = false;
  tradenodes: boolean = false;
  tradegoods: boolean = false; // when viewing all trade goods
  
  // make a list of exclusives, and when we enable one, all the other exclusives are removed
  formable: boolean = false;
  religion: string;
  culture: string;
  tradegood: string;
  
  // religious views
  province_r: string = '';
  country_r: string = '';
  
  // cultures
  province_c: string = '';
  country_c: string = '';

  
  // can we add a set/get and a toggle()? would be easier, and resetAll()
  reset() {
    console.log('resetting filters!!!!')
    this.hre = this.releaseable = this.formable = this.tradegoods = this.tradenodes = false;
    this.province_r = this.province_c = this.country_r = this.country_c = this.tradegood = '';

    this._filters.next('calling next() in reset()')
  }
  
  toggle(choice, value) {
    console.log('CHOICE TOGGLE', choice, this[choice], value, typeof(this[choice]));
    this.reset();
    if (choice !== 'none') {
      if (typeof this[choice] === "boolean") {
        this[choice] = !this[choice];
      } else if (typeof this[choice] == "string") {
        //console.log('setting filter', choice);
        this[choice] = value; 
      }
      
      // Ok updated our choices, now update observable?
      this._filters.next('_filters.next() value, now change the data');
    }
  }
  
  exclusives = ['hre', 'tradenodes'];
  isExclusive(e) {
    
  }
  
  set(k, v) {
    
  }

  selected(provinceid) {
    // we clicked on a provinced
    console.log('filtersComponent selected()', provinceid);
    this.selectedProvince = provinceid;
    this._filters.next('selectedProvince');
  }

  showFilterDetails(which) {
    // Send thing out to the details menu
    this.showingFiltered = true;
    this.selectedProvince = 0;
    this._filters.next('showFilterDetails' + which);
  }

  hideFilterDetails(which) {
    // but don't disable the filter
    this.showingFiltered = false;
    this.selectedProvince = 0;
  }
}