// Services maybe
import { Injectable } from '@angular/core';

@Injectable() 
export class DataService {
  provinces: any;
  countries: any;
  paths: any;
}

@Injectable() 
export class Filters {
  hre: boolean = false;
  releaseable: boolean = false;
  formable: boolean = false;
  religion: string;
  culture: string;
  tradegood: string;
  
  // can we add a set/get and a toggle()? would be easier, and resetAll()
  reset() {
    //console.log('resetting filters')
    this.hre = this.releaseable = this.formable = false;
  }
  
  toggle(choice) {
    console.log('CHOICE TOGGLE', this[choice]);
    if (typeof this[choice] === "boolean") {
      this[choice] = !this[choice];
    }
  }
}