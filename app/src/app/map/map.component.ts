import { Component, OnInit, Output, EventEmitter, Input, OnChanges, SimpleChanges } from '@angular/core';
import * as d3 from 'd3';
import { DataService, Filters, Actions } from '../app.services';
import { Subscription } from 'rxjs/Subscription';
import * as _ from 'underscore';

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
  ds: DataService;
  
  @Input() appSettings;
  @Input() title: string;
  @Output() onSelect = new EventEmitter<number>();
  //@Input() filtersChanged;
  @Input() redrawMap;
  
  filtersub: Subscription;
  actionsub: Subscription;
  
  constructor(public dataStore: DataService, public _filters: Filters, public actions: Actions) {
  }
  
  ngOnChanges(changes: SimpleChanges) {
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
  
  toggleZoom() {
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

  action_in(item) {
    console.log('got new action in map: ', item);
    if (item !== null) {
      let sp = item[0].split('_');
      if (sp[0] == 'map') {
        switch (sp[1]) {
          case 'zoomTo':
            this.zoomToCountry(item[1],1);
            break;
          case 'zoomToProv':
            this.zoomToProvince(item[1],1);
            break;
        }
      }
    }
  }

  ngOnInit() {
    //console.log('mapComponent ngOninit()');
    this.filtersub = this._filters.obsFilter.subscribe(item => this.filtersChanged(item));
    this.actionsub = this.actions.obsAction.subscribe(item => this.action_in(item));

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

    var enableDragging = true;
    
    var svg = d3.select('#svg svg')
        .attr('width', '100%')
        .attr('height', '100%')
        //.style('border', '1px solid black')
    
        // Use switching for now :(
        if (enableDragging) {
          svg.on('contextmenu', function(d) {
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
        }
    
    var container = svg.append('g');
    
    var zoom = d3.zoom()
        //.scaleExtent([.001, .20])
        /* TS: add this. to funcs */
        .on("zoom", this.zoomed)
        .on('start', this.zoomStart)
        .on('end', this.zoomEnd);
    
    if (enableDragging) {
      var rect = container.append("rect")
          .attr('id', 'dragger')
          .attr("class", "overlay")
          .attr("width", '100%')
          .attr("height", '100%')
          .style('pointer-events', 'all')
          .call(zoom);
    }
    
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
        .attr('transform', 'translate(0.000000,2048.000000) scale(0.1,-0.1)');

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
            return self.provinceStyle(d);
        })
        .attr('class', function(d) {
            return self.provinceClass(d);
        });

        
    //path.exit().remove();

    // Add text on top? and maybe a star for the capital?
    /*build.append('text')
        .text('This is text')
        .attr('dx', 100)
        .attr('dy', -100)
        .style('fill', 'white')
        .attr('font-size', 35)
        .attr('transform', 'scale(1, -1)')
        ;
    */

    // Draw seperate trade arrows/routes
  }
  
  provinceClass(node) {
    //console.log('provinceClass', node)
    // node['owner'] == 'TAG'
      let classes = ['pn'];
      var inactive = false;
      var prov = this.ds.provinces[node.id];
      var is_prov = prov !== undefined;
      
      // Who owns it?
      var country = null;
      if (node.owner !== null) {
        let c = this.ds.countries[node.owner]; 
        if (c !== undefined) {
          var country = this.ds.countries[node.owner];
        }
      }
      //console.log('country', country);

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
      // if this province is in a country that passes the filter
      if (this._filters.country_r) {
        if (country !== null) {
          let field = country['religion'];
          var inactive = this.ifInactive(node, field, this._filters.country_r);
        }
      }
      if (this._filters.country_c) {
        /*if (country !== null) {
          let field = country['culture'];
          var inactive = this.ifInactive(node, field, this._filters.country_r);
        }*/
      }
      if (this._filters.tradegood) {
        if (is_prov) {
          //console.log('compare', this.ds.provinces[node.id].trade, this._filters.tradegood);
          var inactive = this.ifInactive(node, prov.trade, this._filters.tradegood);
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

  provinceStyle(node) {
    // If country exists                    
    let c = this.getCountry(node['owner']);
    var color = 'gray';
    if (c !== false) {
        if (!c['color']) {
            //console.log('NO COLOR: ', c['name']);
        }
        var color = '#' + c['color'];
    }            

    // Check for filters
    if (this._filters.tradenodes) {
      // Set color to the tradenode it's in
      for (let idx in this.ds.tradenodes) {
        var item = this.ds.tradenodes[idx];
        //console.log('item', item);

        if ('color' in item && _.contains(item.members, node.id)) {
          var col = item['color'];
          var color = 'rgb(' + col[0] + ',' + col[1] + ',' + col[2] + ')';
        }
      }
      /*var tnode = this.ds.tradenodes[node.tradenode.name];
      if ('color' in tnode) {
        var color = 'rgb(' + tnode.color[0] + ',' + tnode.color[1] + ',' + tnode.color[2] + ')';
      }*/
    }

    return 'fill: ' + color;
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
  
  zoomToProvince(provid, zoomLevel) {
    // Get bbox and translate
    let prov = document.querySelector('#province_' + provid);
    if (prov !== null && prov.hasOwnProperty('getBBox')) {
      var box = prov.getBBox();

      // revert the initial transform data
      //.attr('transform', 'translate(0.000000,2048.000000) scale(0.100000,-0.100000)');
      var x1 = box.x * 0.1 + 0;
      var y2 = box.y * -0.1 + 2048;
      // For it to be on screen, have to also use the height
      var y2 = y2 - box.height * 0.1;
      console.log('position of province top left and bottom right: ', x1, y2)
    }
  }

  zoomToCountry(tag, zoomLevel) {
    /*console.log('in zoomToCountry', tag)
    let provs = this.ds.countries[tag].provs;
    var bounds = {'top': -Infinity, 'bot': -Infinity, 'left': -Infinity, 'right': -Infinity};

    if (provs.length > 0) {
      // find boundaries of all these provinces
      for (let id of provs) {
        let p = document.querySelector('#province_' + id);
        let box = p.getBBox();
        console.log(box);
      }
    }
    // find all provinces in this country
    */
  }

}
