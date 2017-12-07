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
    var defaulttransform = 'translate(500, 200) scale(1)';
    
    var svg = d3.select('#svg').append('svg')
        .attr('width', '100%')
        .attr('height', height + 'px')
        .style('border', '5px solid red')
        //.attr('viewBox', '0 0 ' + width + ' ' + height)
    
    var container = svg.append('g');
    
    var zoom = d3.zoom()
        .scaleExtent([1, 20])
        .on("zoom", this.zoomed)
        .on('start', this.zoomStart)
        .on('end', this.zoomEnd)
        ;
    
    //var paths = svg.append('g');
    
    var rect = container.append("rect")
        .attr('id', 'dragger')
        .attr("class", "overlay")
        .attr("width", width)
        .attr("height", height)
        .style('stroke', 'yellow')
        .style('stroke-width', '1px')
        .call(zoom);
    
        // on drag start, disable pointer events for paths
    var paths = svg.append('g')
        .attr('id', 'paths')
        .attr('transform', defaulttransform);
        
    let self = this;
    d3.json('/assets/eu4map.json').get(function(error, data) {
       if (error) throw error;
       
       console.log('loaded json, len ', data.length);
       self.data = data;
       
       paths.selectAll('path')
            .data(data).enter()
            
            .append('path')
            .attr('id', function(x) {
                return 'province_' + x['id'];
            })
            .attr('d', (x) => x['d'])
            .attr('style', function(x) {
                return 'fill: ' + x['c']['fill'];// + ';stroke:#fff;stroke-width:1;';
            })
            .style('pointer-events', 'none') // default
            .on('mouseover', function(d) {
                d3.select(this).style('stroke', '#fff').style('stroke-width', '1px')
            })
            .on('mouseout', function(d) {
                d3.select(this).style('stroke', null).style('stroke-width', null);
            })
            .on('click', function(d) {
                self.clickDetail(d);
            });
    });
    
  }
  
  clickDetail(d) {
    console.log('deetz',d.id);
    
    // Send d.id up to App, then over to detail
    this.onSelect.emit(d.id);
  }
  
  zoomed() {
    d3.select('#paths').attr("transform", d3.event.transform);
  }
  zoomStart() {
    console.log('zoom start')
  }
  zoomEnd() {
    console.log('zoom end');
  }

}
