

Vue.component('eumap', {
  template: '#eumap',
  data: function() {
    return {
      inited: false,
      game: {},
      target: 'province',
      highlight: false,
    }
  },
  mounted: function() {
    //console.log('load map, draw init then wait for data to be set to use drawProvinces');

    // set up watchers fuck
    //c//onsole.log(this.$store.watch)
    //this.$store.watch()
    //this.init2();
    this.game = this.$store.state.game;
  },
  watch: {
    isloaded (new1, old1) {
      //console.log('draw2 was updated?????');
      this.init(); // data files are loaded
    },
    redraw (new1, old1) {
      console.log('map:redraw')

      // Check target
      this.target = this.$store.getters.target;

      // If this is (for now) an achievement filter, make sure we highlight
      this.highlight = false;
      if (_.contains(this.$store.getters.selected_type, 'achievement')) {
        this.highlight = true;
      }

      this.drawProvinces();
    }
  },

  computed: {
    isloaded() {
      return this.$store.getters.loaded;
    },
    redraw() {
      return this.$store.getters.check_if_redraw;
    },

    
  },

  methods: {/*
    init2: function(){
      console.log('init2 called')

      //then draw
      this.draw2;
    },*/
    filter: function(which) {
      return this.$store.getters.filters(which);
    },
    drawProvinces: function() {
      //console.log('drawing provinces');

      if (this.inited === false) {
        // make sure we init first
        console.log('initting first');
        this.init();
      }

      /*if (this.dataStore.paths === undefined) {
        return;
      }*/

      let self = this;
      
      /* Get data from storage */
      var pathsdata = self.$store.state.game.paths;
      //console.log('pdata1', pathsdata[0])
      var countries = self.$store.state.game.c; // not sure if needed
      var provinces = self.$store.state.game.p; // not sure if needed
      var tradenodes = self.$store.state.game.tradenodes;
      
      for (let p in pathsdata) {
          if (pathsdata.hasOwnProperty(p)) {
              let id = pathsdata[p]['id'];
              pathsdata[p] = Object.assign({}, pathsdata[p], provinces[id]);
          }
      }

      //console.log('PEEDATA', pathsdata, pathsdata[0]);
      
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
      return pathsdata;
    },
    init: function() {
      console.log('map: setup');
      // initial setup, don't apply filters though
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

      this.inited = true;

      this.drawProvinces(); // try to remove the need for this and just run on update?
    },

    provinceClass: function(node) {

      // Update a something somewhere so we can make a loading thing, since this is called for each province each time filters are updated

      let classes = ['pn'];
      var inactive = false;
      var prov = this.$store.getters.province(node.id);
      var is_prov = prov !== undefined;
      
      if (this.highlight) {
        classes.push('highlight');
      }

      // Who owns it?
      var country = null;
      if (node.owner !== null) {
        let c = this.$store.getters.country(node.owner); 
        if (c !== undefined) {
          var country = c;
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
      if (this.filter('hre') === true) {
        var inactive = this.ifInactive(node, node.hre, true);
      }

      // now allows for both province and country. some provs obviously don't belong to a country
      if (this.filter('religion')) {
        let compare = null;
        if (this.target == 'countries') {
          if (country !== null) {
            compare = country.religion;
          }
        } else {
          // compare the province
          compare = node.religion;
        }
        var inactive = this.ifInactive(node, compare, this.filter('religion'));          
      }
      if (this.filter('culture')) {
        let compare = null;
        if (this.target == 'countries') {
          if (country !== null) {
            compare = country.culture;
          }
        } else {
          // compare the province
          compare = node.culture;
        }
        var inactive = this.ifInactive(node, compare, this.filter('culture'));          
      }
      if (this.filter('tradegood')) {
        if (is_prov) {
          //console.log('compare', this.ds.provinces[node.id].trade, this._filters.tradegood);
          var inactive = this.ifInactive(node, prov.trade, this.filter('tradegood'));
        } else {
          var inactive = true;
        }
      }
      // tradegood

      // If we've selected an achievement
      if (this.filter('achievement')) {
        let ach = this.$store.getters.achievement(this.filter('achievement'));
        let cored = ach.happened.owns_core_province;
            cored = !Array.isArray(cored) ? [cored] : cored;
        let owned = ach.happened.owns;
            owned = !Array.isArray(owned) ? [owned] : owned;

        var inactive = this.ifInactive(node, _.contains(_.union(owned,cored), node.id), true);
      }

      if (inactive === true) {
        classes.push('pinactive');
      }

      // Is it uncolonized?
      return classes.join(' ');
    },

  provinceStyle: function(node) {
    // If country exists    
    //console.log('provinceStyle', this.filter('tradenodes'))

    // if we're highlighting, just do that
    if (this.highlight) {
      // use hamburgs colour
      return 'fill:#e35f07';
    }

    let c = this.getCountry(node['owner']);
    var color = 'gray';
    if (c !== false) {
        if (!c['color']) {
            //console.log('NO COLOR: ', c['name']);
        }
        var color = '#' + c['color'];
    }            

    // Check for filters
    if (this.filter('tradenodes')) {
      // Set color to the tradenode it's in
      let tn = this.$store.state.game.tradenodes;
      for (let idx in tn) {
        var item = tn[idx];
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
  },

  ifInactive: function(node, field, testvalue) {
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
  },
    
  // Get country this belongs to
  getCountry: function(tag) {
      if (tag === null || tag === undefined) {
          return false;
      }
      return this.$store.getters.country(tag);
  },
  
  clickDetail: function(d) {
    //console.log('clicked province', d)
    // Check if inactive/sea zone/wasteland?
    this.$store.commit('selected_p', d.id);
  },
  
  zoomed: function() {
    var t = d3.event.transform;
    //console.log(t);
    //console.log('t', t.x, t.y);
    d3.select('#paths').attr('transform', "translate(" + t.x + "," + t.y + ") scale(" + t.k + "," + t.k + ")");
  },
  zoomStart: function() {
    //console.log('zoom start')
  },
  zoomEnd:function() {
    //console.log('zoom end');
  },
  
  zoomToProvince:function(provid, zoomLevel) {
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
  },

  zoomToCountry:function(tag, zoomLevel) {
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
  },

    redraw: function() {
      // might not be needed if its computed
    },
    toggleZoom: function() {
      /*

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
      */
    },

    action_in: function(item) {
      /*

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
      */
    }
  },
});