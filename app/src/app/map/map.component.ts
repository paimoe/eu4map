import { Component, OnInit, Output, EventEmitter, Input, OnChanges, SimpleChanges } from '@angular/core';
import * as d3 from 'd3';
import { DataService, Filters } from '../app.services';
import { Subscription } from 'rxjs/Subscription';

@Component({
  selector: 'app-map',
  templateUrl: './map.component.html',
  styleUrls: ['./map.component.css']
})
export class MapComponent implements OnInit, OnChanges {
  
  data = [];
  allowZoom: boolean;
  
  dataPaths: any;
  dataProvinces: any;
  
  @Input() appSettings;
  @Input() title: string;
  @Output() onSelect = new EventEmitter<number>();
  //@Input() filtersChanged;
  @Input() redrawMap;
  
  filtersub: Subscription;
  
  constructor(public dataStore: DataService, public _filters: Filters) {
  }
  
  ngOnChanges(changes: SimpleChanges) {
    //console.log('datastore', this.dataStore)
    //console.log('map changes func',changes);
    let key = Object.keys(changes)[0];
    if (key == 'filtersChanged') {
      // Rerun _filters
      //console.log('ngChanges on map', this._filters);
      //this.drawMap();
    } else if (key == 'redrawMap') {
      //console.log('got redrawMap event');
      this.drawMap();
    } else {
      this.toggleZoom();
    }
  }
  
  toggleZoom(): void {
    let allow = this.appSettings['allowZoom'];
    if (allow === true) {
      // Allow zoom
      var dragger = 'all';
      var path = 'none';
    } else {
      var dragger = 'none';
      var path = 'all';
    }
    d3.select('#dragger').style('pointer-events', dragger);
    d3.selectAll('path').style('pointer-events', path);
  }
  
  filtersChanged(item) {
    //console.log('called filtersChanged', item)
    this.drawMap();
  }
  
  ngOnDestroy() {
    this.filtersub.unsubscribe();
  }

  ngOnInit() {
    //console.log('mapComponent ngOninit()');
    this.filtersub = this._filters.obsFilter.subscribe(item => this.filtersChanged(item));
    this.ds = this.dataStore;
    
    //this.filtersub = this._filters.obsFilter.subscribe(item => this.filtersChanged(item))
    //console.log(this._filters.obsFilter);
    //console.log('started the whatever');
    
    var width = 1500;
    var height = 700;
    var defaulttransform = {
        'translate': [-3000,-400],
        'scale': 1.3
    };
    var defaulttransformstr = 'translate(1500,-400) scale(-0.05, 0.05)';
    
    var svg = d3.select('#svg svg')
        .attr('width', '100%')
        .attr('height', '100%')
        //.style('border', '1px solid black')
    
        // Use switching for now :(
        .on('contextmenu', function(d) {
            d3.event.preventDefault();
            // Switch 
            let e = d3.select('#dragger');
            let paths = d3.selectAll('path');
            if (e.style['pointer-events'] == 'all') {
                e.style['pointer-events'] = 'none';
                paths.classed('pn', false);
            } else {
                e.style['pointer-events'] = 'all';
                paths.classed('pn', true);
            }
        });
    
    var container = svg.append('g');
    
    var zoom = d3.zoom()
        //.scaleExtent([.001, .20])
        /* TS: add this. to funcs */
        .on("zoom", this.zoomed)
        .on('start', this.zoomStart)
        .on('end', this.zoomEnd);
    
    var rect = container.append("rect")
        .attr('id', 'dragger')
        .attr("class", "overlay")
        .attr("width", '100%')
        .attr("height", '100%')
        .style('pointer-events', 'all')
        .call(zoom);
    
    var paths = svg.append('g').attr('id', 'paths');
  }
  
  drawMap() {
    /* TS */// self.data = data;
    if (this.dataStore.paths === undefined) {
      return;
    }
    //console.log('Drawing map');
    let self = this;
    
    /* Get data from storage */
    var pathsdata = self.dataStore.paths;
    var countries = self.dataStore.countries; // not sure if needed
    var provinces = self.dataStore.provinces; // not sure if needed
    var tradenodes = self.dataStore.tradenodes;
    
    for (let p in pathsdata) {
        if (pathsdata.hasOwnProperty(p)) {
            let id = pathsdata[p]['id'];
            pathsdata[p] = Object.assign({}, pathsdata[p], provinces[id]);
        }
    }
    
    // Remove existing paths
    //d3.selectAll('#paths g').remove();
    
    // Global
    let build = d3.select('#paths').selectAll('g')
        .data(pathsdata).enter()
        .append('g')
        .attr('transform', 'translate(0.000000,2048.000000) scale(0.100000,-0.100000)');

    let path = build.append('path')
        .attr('id', (x) => 'province_' + x['id'])
        .attr('d', (x) => x['d'])
        .on('mouseover', function(d) {
            d3.select(this).classed('hover', true);
        })
        .on('mouseout', function(d) {
            d3.select(this).classed('hover', false);
        })
        .on('click', function(d) {
            self.clickDetail(d);
        });
    
    // Apply these every time
    d3.selectAll('path')
        .attr('style', function(d) {
            // If country exists                    
            let c = self.getCountry(d['owner']);
            if (c === false) {
                var color = 'gray';
            } else {
                if (!c['color']) {
                    console.log('NO COLOR: ', c['name']);
                }
                var color = '#' + c['color'];
            }            
            return 'fill: ' + color;
        })
        .attr('class', function(d) {
            return self.provinceClass(d);
        });

        
    //path.exit().remove();

    // Add text on top? and maybe a star for the capital?
    /*build.append('text')
        .text('This is text')
        .attr('x', 0)
        .attr('y', 0)
        .style('fill', 'white')
        ;
    */
  }
  
  provinceClass(node) {
    //console.log('provinceClass', node)
    // node['owner'] == 'TAG'
      let classes = ['pn'];
      var inactive = false;
      
      // Who owns it?

      // Is it wasteland?
      if (node['wasteland'] === true) {
          classes.push('pwaste');
      }

      // Is it ocean?
      var water = false;
      if (node['sea'] === true || node['ocean'] === true) {
          var water = true;
          classes.push('psea');
      }
      if (node['lake'] === true) {
        classes.push('plake');
      }
      
      // Check _filters and ignore any others if we're filtered out
      if (this._filters.hre === true) {
        var inactive = this.ifInactive(node, node.hre, true);
      }
      if (this._filters.province_r) {
        var inactive = this.ifInactive(node, node.religion, this._filters.province_r);
      }
      if (this._filters.province_c) {
        var inactive = this.ifInactive(node, node.culture, this._filters.province_c);
      }
      if (this._filters.tradegood) {
        if (this.ds.provinces[node.id] !== undefined) {
          //console.log('compare', this.ds.provinces[node.id].trade, this._filters.tradegood);
          var inactive = this.ifInactive(node, this.ds.provinces[node['id']].trade, this._filters.tradegood);
        } else {
          var inactive = true;
        }
      }
      // tradegood
      // country_r/c

      if (inactive === true) {
        classes.push('pinactive');
      }

      // Is it uncolonized?
      return classes.join(' ');
  }

  ifInactive(node, field, testvalue) {
    let water = node['sea'] === true || node['ocean'] === true || node['lake'] === true;
    if (field === testvalue) {
      return false;
    } else {
      // We want to set this to inactive, unless its water/wasteland
      if (water === false && node['wasteland'] === false) {
        return true;
      }
    }
    return false;
  }
    
  // Get country this belongs to
  getCountry(tag) {
      if (tag === null || tag === undefined) {
          return false;
      }
      if (this.dataStore.countries.hasOwnProperty(tag) === false) {
          return false;
      } 
      return this.dataStore.countries[tag];
  }
  
  clickDetail(d) {
    // Send d.id up to App, then over to detail
    this._filters.selected(d.id);
    this.onSelect.emit(d.id);
  }
  
  zoomed() {
    var t = d3.event.transform;
    //console.log(t);
    d3.select('#paths').attr('transform', "translate(" + t.x + "," + t.y + ") scale(" + t.k + "," + t.k + ")");
  }
  zoomStart() {
    //console.log('zoom start')
  }
  zoomEnd() {
    //console.log('zoom end');
  }
  
  zoomToProvince(provid, zoomLevel) {}

}
