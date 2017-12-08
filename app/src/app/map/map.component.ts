import { Component, OnInit, Output, EventEmitter, Input, OnChanges, SimpleChanges } from '@angular/core';
import * as d3 from 'd3';
import { DataService, Filters } from '../app.services';

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
  @Input() filtersChanged;
  
  constructor(public dataStore: DataService, public filters: Filters) {
    
    // load json
  }
  
  ngOnChanges(changes: SimpleChanges) {
    console.log('map changes func',changes);
    if (Object.keys(changes)[0] == 'filtersChanged') {
      // Rerun filters
      console.log('ngChanges on map', this.filters);
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

  ngOnInit() {
    console.log('started the whatever');
    
    var width = 1500;
    var height = 700;
    var defaulttransform = {
        'translate': [-3000,-400],
        'scale': 1.3
    };
    var defaulttransformstr = 'translate(1500,-400) scale(-0.05, 0.05)';
    
    var svg = d3.select('#svg svg')
        .attr('width', '100%')
        .attr('height', height + 'px')
        .style('border', '1px solid black')
    
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
        .attr("width", width)
        .attr("height", height)
        .style('stroke', 'yellow')
        .style('stroke-width', '1px')
        .style('pointer-events', 'all')
        .call(zoom);
    
    var paths = svg.append('g').attr('id', 'paths');
    
    //const url = '/output/eu4map.json';
    const url = '/assets/eu4map.json';
    
    let self = this;
    
    // Get countries
    d3.json('/assets/countries.json').get(function(error, countries) {
        if (error) throw error;
        
        // Send countries data up to app (should this be moved to App?)
        self.dataStore.countries = countries;
    
        // Get tile info
        d3.json('/assets/provdata.json').get(function(error, provdata) {
            if (error) throw error;
            
            self.dataProvinces = provdata;
            
            // Countries with no provinces are releasable (probably)
    
            d3.json(url).get(function(error, pathdata) {
                if (error) throw error;
                
                self.dataPaths = pathdata;
                
                self.drawMap();
    
            });
    
        });
    
    });
    
  }
  
  drawMap() {
    /* TS */// self.data = data;
    console.log('DRAWING MAP');
    let self = this;
    let pathsdata = self.dataPaths;
    for (let p in pathsdata) {
        if (pathsdata.hasOwnProperty(p)) {
            let id = pathsdata[p]['id'];
            pathsdata[p] = Object.assign({}, pathsdata[p], self.dataProvinces[id]);
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
            //console.log(d);
        });
    
    // Apply these every time
    d3.selectAll('path').attr('style', function(d) {
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
      let classes = ['pn'];
      
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
      
      // Check filters and ignore any others if we're filtered out
      if (this.filters.hre === true) {
        if (node['hre'] === true) {
          return classes.join(' ');
        } else {
          if (water === false && node['wasteland'] === false) {
            classes.push('pinactive');
          }
          return classes.join(' ');
        }
      }

      // Is it uncolonized?
      return classes.join(' ');
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
