import { Component, OnInit, Output, EventEmitter, Input, OnChanges, SimpleChanges } from '@angular/core';
import * as d3 from 'd3';

@Component({
  selector: 'app-map',
  templateUrl: './map.component.html',
  styleUrls: ['./map.component.css']
})
export class MapComponent implements OnInit, OnChanges {
  
  data = [];
  allowZoom: boolean;
  
  @Input() appSettings;
  @Input() title: string;
  @Output() onSelect = new EventEmitter<number>();
  
  constructor() {
    
    // load json
  }
  
  ngOnChanges(changes: SimpleChanges) {
    console.log('map changes func',changes);
    this.toggleZoom();
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
                paths.attr('class', 'pa');
            } else {
                e.style['pointer-events'] = 'all';
                paths.attr('class', 'pn');
            }
        });
    
    var container = svg.append('g');
    
    var zoom = d3.zoom()
        //.scaleExtent([.001, .20])
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
    d3.json(url).get(function(error, data) {
        if (error) throw error;
        
        self.data = data;
    
        // Global
        paths.selectAll('g')
            .data(data).enter()
            
            .append('g')
            .attr('transform', 'translate(0.000000,2048.000000) scale(0.100000,-0.100000)')
            .append('path')
    
            .attr('id', (x) => 'province_' + x['id'])
            .attr('d', (x) => x['d'])
            .attr('style', (x) => 'fill: ' + x['hex'])
            .attr('class', 'pn')
    
            .on('mouseover', function(d) {
                d3.select(this).classed('hover', true);
            })
            .on('mouseout', function(d) {
                d3.select(this).classed('hover', false);
            })
            .on('click', function(d) {
                self.clickDetail(d);
                //tileedit(d);
            });
    
    });
    
  }
  
  clickDetail(d) {
    console.log('deetz',d.id);
    
    // Send d.id up to App, then over to detail
    this.onSelect.emit(d.id);
  }
  
  zoomed() {
    var t = d3.event.transform;
    //console.log(t);
    d3.select('#paths').attr('transform', "translate(" + t.x + "," + t.y + ") scale(" + t.k + "," + t.k + ")");
  }
  zoomStart() {
    console.log('zoom start')
  }
  zoomEnd() {
    console.log('zoom end');
  }

}
