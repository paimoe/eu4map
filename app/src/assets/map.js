/* global d3 */
document.addEventListener("DOMContentLoaded", function(event) { 
  //do work
    
});

function draw_graph2() {
    console.log('draw idk');
}

function draw_graph() {

    
    function tileinfo(d) {
        //console.log(d);
        //document.querySelector('#tile').innerHTML = 'tile#' + d.id;
    }
    
    function tileedit(d) {
        document.querySelector('#edit input.id').value = d['id'];
        document.querySelector('#edit input.name').value = d['name'];
    }
    
    window.panning = false;
    window.zooming = false;
    
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
        .on("zoom", zoomed)
        .on('start', zoomStart)
        .on('end', zoomEnd)
        ;
    
    var drag = d3.drag()
        .on('drag', dragged);
    
    //var paths = svg.append('g');
    
    var rect = container.append("rect")
        .attr('id', 'dragger')
        .attr("class", "overlay")
        .attr("width", width)
        .attr("height", height)
        .style('stroke', 'yellow')
        .style('stroke-width', '1px')
        //.style('pointer-events', 'none')
        .call(zoom);
    
        // on drag start, disable pointer events for paths
    var paths = svg.append('g')
        .attr('id', 'paths')
        .attr('transform', defaulttransform);
    
       // d3.select('svg g').call(zoom);
    //d3.select('rect').attr('transform', defaulttransform);
    //svg.append('circle').attr('cx', -500).attr('cy', 0).attr('r', 30).attr('stroke', 'black').attr('fill', 'white');
    
    d3.json('/assets/eu4map.json').get(function(error, data) {
        if (error) throw error;
    
        // Global
    
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
            .on('mouseover', function(d) {
                d3.select(this).style('stroke', '#fff').style('stroke-width', '1px')
                tileinfo(d);
            })
            .on('mouseout', function(d) {
                d3.select(this).style('stroke', null).style('stroke-width', null);
            })
            .on('click', function(d) {
                //if (d3.event.defaultPrevented) return;
                tileedit(d);
            })/*
            .call(drag)*/
            //.call(zoom)
            ;
    
    });
    
    function zoomed() {
        var t = d3.event.transform;
        console.log(d3.event.transform);
    
       // t.x = Math.min(-500)
    
        d3.select('#paths').attr("transform", t);
    
        //console.log(rect.node().getBBox());
    
        // set timeout to disable?
        /*setTimeout(function() {
            console.log('remove pointers');
            //d3.select('#dragger').style('pointer-events', 'none');
        }, 1500);*/
    }
    
    function dragged() {
        // A province was dragged, so re-enable and begin zoom func
        //console.log('dragged',d3.event.x, d3.event.y, d3.event.dx, d3.event.dy);
        
        var newdims = {
            'x':1
        };
        //d3.select('#dragger').style('pointer-events', 'all');
    }
    
    function zoomStart() {
        console.log('zoom start')
        // disable province events
        d3.selectAll('path').style('pointer-events', 'none');
    }
    function zoomEnd() {
        console.log('zoom end')
    }
}