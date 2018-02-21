'use strict';

(function(){

  var module = angular.module('geonode_main_search', [], function($locationProvider) {
      if (window.navigator.userAgent.indexOf("MSIE") == -1){
          $locationProvider.html5Mode({
            enabled: true,
            requireBase: false
          });

          // make sure that angular doesn't intercept the page links
          angular.element("a").prop("target", "_self");
      }
    });

    // Used to set the class of the filters based on the url parameters
    module.set_initial_filters_from_query = function (data, url_query, filter_param){
        for(var i=0;i<data.length;i++){
            if( url_query == data[i][filter_param] || url_query.indexOf(data[i][filter_param] ) != -1){
                data[i].active = 'active';
            }else{
                data[i].active = '';
            }
        }
        return data;
    }

  // Load categories, keywords, and regions
  module.load_categories = function ($http, $rootScope, $location){
        var params = typeof FILTER_TYPE == 'undefined' ? {} : {'type': FILTER_TYPE};
        if ($location.search().hasOwnProperty('title__icontains')){
          params['title__icontains'] = $location.search()['title__icontains'];
        }
        $http.get(CATEGORIES_ENDPOINT, {params: params}).success(function(data){
            if($location.search().hasOwnProperty('category__identifier__in')){
                data.objects = module.set_initial_filters_from_query(data.objects,
                    $location.search()['category__identifier__in'], 'identifier');
            }
            $rootScope.categories = data.objects;
            if (HAYSTACK_FACET_COUNTS && $rootScope.query_data) {
                module.haystack_facets($http, $rootScope, $location);
            }
        });
    }

  module.load_keywords = function ($http, $rootScope, $location){
        var params = typeof FILTER_TYPE == 'undefined' ? {} : {'type': FILTER_TYPE};
        if ($location.search().hasOwnProperty('title__icontains')){
          params['title__icontains'] = $location.search()['title__icontains'];
        }
        $http.get(KEYWORDS_ENDPOINT, {params: params}).success(function(data){
            if($location.search().hasOwnProperty('keywords__slug__in')){
                data.objects = module.set_initial_filters_from_query(data.objects,
                    $location.search()['keywords__slug__in'], 'slug');
            }
            $rootScope.keywords = data.objects;
            if (HAYSTACK_FACET_COUNTS && $rootScope.query_data) {
                module.haystack_facets($http, $rootScope, $location);
            }
        });
    }

  module.load_regions = function ($http, $rootScope, $location){
        var params = typeof FILTER_TYPE == 'undefined' ? {} : {'type': FILTER_TYPE};
        if ($location.search().hasOwnProperty('title__icontains')){
          params['title__icontains'] = $location.search()['title__icontains'];
        }
        $http.get(REGIONS_ENDPOINT, {params: params}).success(function(data){
            if($location.search().hasOwnProperty('regions__name__in')){
                data.objects = module.set_initial_filters_from_query(data.objects,
                    $location.search()['regions__name__in'], 'name');
            }
            $rootScope.regions = data.objects;
            if (HAYSTACK_FACET_COUNTS && $rootScope.query_data) {
                module.haystack_facets($http, $rootScope, $location);
            }
        });
    }

    module.load_owners = function ($http, $rootScope, $location){
        var params = typeof FILTER_TYPE == 'undefined' ? {} : {'type': FILTER_TYPE};
        if ($location.search().hasOwnProperty('title__icontains')){
            params['title__icontains'] = $location.search()['title__icontains'];
        }
        $http.get(OWNERS_ENDPOINT, {params: params}).success(function(data){
            if($location.search().hasOwnProperty('owner__username__in')){
                data.objects = module.set_initial_filters_from_query(data.objects,
                    $location.search()['owner__username__in'], 'identifier');
            }
            $rootScope.owners = data.objects;
            if (HAYSTACK_FACET_COUNTS && $rootScope.query_data) {
                module.haystack_facets($http, $rootScope, $location);
            }
        });
    }

  // Update facet counts for categories and keywords
  module.haystack_facets = function($http, $rootScope, $location) {
      var data = $rootScope.query_data;
      if ("categories" in $rootScope) {
          $rootScope.category_counts = data.meta.facets.category;
          for (var id in $rootScope.categories) {
              var category = $rootScope.categories[id];
              if (category.identifier in $rootScope.category_counts) {
                  category.count = $rootScope.category_counts[category.identifier]
              } else {
                  category.count = 0;
              }
          }
      }

      if ("keywords" in $rootScope) {
          $rootScope.keyword_counts = data.meta.facets.keywords;
          for (var id in $rootScope.keywords) {
              var keyword = $rootScope.keywords[id];
              if (keyword.slug in $rootScope.keyword_counts) {
                  keyword.count = $rootScope.keyword_counts[keyword.slug]
              } else {
                  keyword.count = 0;
              }
          }
      }

      if ("regions" in $rootScope) {
          $rootScope.regions_counts = data.meta.facets.regions;
          for (var id in $rootScope.regions) {
              var region = $rootScope.regions[id];
              if (region.name in $rootScope.region_counts) {
                  region.count = $rootScope.region_counts[region.name]
              } else {
                  region.count = 0;
              }
          }
      }

      if ("owners" in $rootScope) {
          $rootScope.owner_counts = data.meta.facets.owners;
          for (var id in $rootScope.owners) {
              var owner = $rootScope.owners[id];
              if (owner.name in $rootScope.owner_counts) {
                  owner.count = $rootScope.owner_counts[owner.name]
              } else {
                  owner.count = 0;
              }
          }
      }
  }

  /*
  * Load categories and keywords
  */
  module.run(function($http, $rootScope, $location){
    /*
    * Load categories and keywords if the filter is available in the page
    * and set active class if needed
    */
    if ($('#categories').length > 0){
       module.load_categories($http, $rootScope, $location);
    }
    if ($('#keywords').length > 0){
       module.load_keywords($http, $rootScope, $location);
    }
    if ($('#regions').length > 0){
       module.load_regions($http, $rootScope, $location);
    }
    if ($('#owners').length > 0){
       module.load_owners($http, $rootScope, $location);
    }

    // Activate the type filters if in the url
    if($location.search().hasOwnProperty('type__in')){
      var types = $location.search()['type__in'];
      if(types instanceof Array){
        for(var i=0;i<types.length;i++){
          $('body').find("[data-filter='type__in'][data-value="+types[i]+"]").addClass('active');
        }
      }else{
        $('body').find("[data-filter='type__in'][data-value="+types+"]").addClass('active');
      }
    }

    // Activate the sort filter if in the url
    if($location.search().hasOwnProperty('order_by')){
      var sort = $location.search()['order_by'];
      $('body').find("[data-filter='order_by']").removeClass('selected');
      $('body').find("[data-filter='order_by'][data-value="+sort+"]").addClass('selected');
    }

  });


  module.filter('keywordLocationFilter', function() { 
    var data_filter = 'keywords__slug__in';
    
    return function(input, query) {
      var output;

      if(query[data_filter].indexOf('clear-results') >= 0){
        return [];
      }

      output = input.filter(function(item){
          return item.keywords.indexOf(MAP_TYPE) >=0;
      });
  
      return output;
  
    }
  
  });

  module.filter('keywordFilter', function() { 
      var data_filter = 'keywords__slug__in';
      
      return function(input, query) {
        var output;
        var query_entry = query[data_filter];

        if(typeof query_entry == 'undefined') query_entry = [];

        // if(typeof MAP_TYPE !== 'undefined'){
        //   if(query_entry.indexOf(MAP_TYPE) < 0){
        //     query_entry.push(MAP_TYPE)
        //   }
        // }

        console.log(query_entry);

        output = input.filter(function(item){
          if(query_entry){
            return query_entry.every(function(currentValue){
              return item.keywords.indexOf(currentValue) >=0;
            });
          }else{
            return false;
          }
        });
    
        return output;
    
      }
    
    });


  module.filter('rsFilter', function() { 
    return function(input) {
      var output = true;

      if(input && input.hasOwnProperty('detail_url')){
        if(input.detail_url.indexOf('lulc') >= 0 || input.detail_url.indexOf('va') >= 0) output = false;
      }

      return output;
    }
  
  });
    
  /*
  * Main search controller
  * Load data from api and defines the multiple and single choice handlers
  * Syncs the browser url with the selections
  */
  module.controller('geonode_search_controller', function($injector, $scope, $window, $location, $http, Configs, $rootScope){
    $scope.query = $location.search();
    $scope.query.limit = $scope.query.limit || CLIENT_RESULTS_LIMIT;
    $scope.query.offset = $scope.query.offset || 0;
    $scope.page = Math.round(($scope.query.offset / $scope.query.limit) + 1);
    
    if(typeof MAP_TYPE == 'undefined'){
      $scope.query['other_rs'] = true;
    }else{
      $scope.query.keywords__slug__in = $scope.query.keywords__slug__in || MAP_TYPE;
    }

    function process_results(location_data, filters_data, data){
      var allLocations = [];
      var allScale = [];
      var allHazard = [];

      var addToLocations = function(location) {
        // Store to allLocations
        var province = location.province.toLowerCase();
        var found = allLocations.some(function (loc) {
          return loc.code === province;
        });
        
        if(!found){
          allLocations.push({
              code: province,
              name: location.province,
              municipality: []
          });
        }
        
        var targetLocation = allLocations.find(function(loc) {
          return loc.code === province;
        });
        
        // Add to municipality
        if(targetLocation){
          var hasMunicipality = targetLocation.municipality.some(function(mun) {
            return mun.code === location.mun_code;
          });

          if(!hasMunicipality){
            targetLocation.municipality.push({
              name: location.city,
              code: location.mun_code
            })
          }
        }
      }

      function processFilter(filterData){
        var targetFilter = filterData.type === 'scale' ? allScale : allHazard;
        var found = targetFilter.some(function (filter) {
          return filterData.filter === filter.filter;
        });

        if(!found) {
          targetFilter.push(filterData);
        }
      }

      $scope.results = data.objects.map(function(result) {
        // Get keywords
        var keywordList = [];
        var locationArr = [];

        // Get keywords
        if(result.hasOwnProperty('metadata_xml')){
          var xmlDoc = $.parseXML( result.metadata_xml );
          var keywordObjects = xmlDoc.getElementsByTagName('gmd:keyword'); //gmd:keyword
          for (var keyword of keywordObjects) {
            keywordList.push(keyword.getElementsByTagName('gco:CharacterString')[0].innerHTML.toLowerCase());
          }
        }

        if(result.hasOwnProperty('detail_url')){
          var detailUrl = decodeURIComponent(result.detail_url).split(':')[1];
          if(typeof detailUrl !== 'undefined') {
            var detailArr = detailUrl.split('_');
            for(var detail of detailArr) {
              detail = detail.toLowerCase();
              if(keywordList.indexOf(detail) < 0) {
                keywordList.push(detail.toLowerCase()); 
              }          
            }
          }
        }

        // Get keywords from name
        if(result.hasOwnProperty('name')){
          var nameArr = result.name.split('_');
          for(var name of nameArr) {
            name = name.toLowerCase();
            if(keywordList.indexOf(name) < 0) {
              keywordList.push(name); 
            }          
          }
        }
        
        
        // Get keywords from doc_file
        if(result.hasOwnProperty('doc_file')){
          // "documents/agri_72204000_lulc.jpg".split('.')[0].split('/')[1].split('_')
          // check if file
          var docFileArr = result.doc_file.split('.')[0].split('/')[1].split('_');
          if(docFileArr.length > 1){
            for(var docFile of docFileArr) {
              docFile = docFile.toLowerCase();
              if(keywordList.indexOf(docFile) < 0) {
                keywordList.push(docFile); 
              }          
            }
          }          
        }
        

        // Get locations from keywords
        var locationStr = [];
        var locationArr = location_data.filter(function(location){
          var exists = keywordList.indexOf(location.mun_code) >= 0;
          if(exists){
            locationStr.push(location.city.toLowerCase() + ', ' + location.province.toLowerCase());
            addToLocations(location);
          }
          
          return exists;
        });

        // console.log('locationArr', locationArr);
                
        result.keywords = keywordList;
        result.locations = locationArr;
        result.locationsLabel = locationStr.join('; ');
        delete result['metadata_xml'];  
        return result;
      });

      // console.log($scope.results);

      // Get filters from keywords
      filters_data.objects.forEach(processFilter);
      
      $rootScope.hazards = allHazard;
      $rootScope.scales = allScale;
      
      console.log('allLocations', JSON.stringify(allLocations));
      if(!$rootScope.locations) $rootScope.locations = allLocations;
    }
   
    //Get data from apis and make them available to the page
    function query_api(data){
      $scope.isLoadingFilters = true;

      if(typeof MAP_TYPE != 'undefined'){
        data.map_type = MAP_TYPE;
      }

      $http.get(Configs.url, {params: data || {}}).success(function(data){        
        $http.get(LOCATIONS_ENDPOINT).success(function(location) {
          $http.get(FILTERS_ENDPOINT).success(function(filters) {
            $scope.isLoadingFilters = false;
            process_results(location, filters, data);
          });
        });

        $scope.total_counts = data.meta.total_count;
        $scope.$root.query_data = data;
        
        if (HAYSTACK_SEARCH) {
          if ($location.search().hasOwnProperty('q')){
            $scope.text_query = $location.search()['q'].replace(/\+/g," ");
          }
        } else {
          if ($location.search().hasOwnProperty('title__icontains')){
            $scope.text_query = $location.search()['title__icontains'].replace(/\+/g," ");
          }
        }

        //Update facet/keyword/category counts from search results
        if (HAYSTACK_FACET_COUNTS){
            module.haystack_facets($http, $scope.$root, $location);
            $("#types").find("a").each(function(){
                if ($(this)[0].id in data.meta.facets.subtype) {
                    $(this).find("span").text(data.meta.facets.subtype[$(this)[0].id]);
                }
                else if ($(this)[0].id in data.meta.facets.type) {
                    $(this).find("span").text(data.meta.facets.type[$(this)[0].id]);
                } else {
                    $(this).find("span").text("0");
                }
            });
        }
      });
    };

    if( !(FILTER_TYPE == 'layer' && MAP_TYPE == 'lulc') ) {
      query_api($scope.query)
    }

    var allLayersLocation = [{"code":"compostela valley","name":"COMPOSTELA VALLEY","municipality":[{"name":"MAWAB","code":"118206000"},{"name":"MACO","code":"118204000"},{"name":"MABINI (DOÑA ALICIA)","code":"118203000"},{"name":"PANTUKAN","code":"118211000"}]},{"code":"davao del norte","name":"DAVAO DEL NORTE","municipality":[{"name":"NEW CORELLA","code":"112314000"},{"name":"TAGUM CITY (Capital)","code":"112319000"},{"name":"BRAULIO E. DUJALI","code":"112323000"},{"name":"CARMEN","code":"112303000"},{"name":"PANABO CITY","code":"112315000"},{"name":"SANTO TOMAS","code":"112318000"},{"name":"ASUNCION (SAUG)","code":"112301000"},{"name":"KAPALONG","code":"112305000"}]},{"code":"bohol","name":"BOHOL","municipality":[{"name":"LOAY","code":"71228000"},{"name":"LOBOC","code":"71229000"},{"name":"ALICIA","code":"71202000"},{"name":"UBAY","code":"71246000"},{"name":"GARCIA HERNANDEZ","code":"71222000"},{"name":"JAGNA","code":"71225000"},{"name":"SAN MIGUEL","code":"71238000"},{"name":"TRINIDAD","code":"71244000"},{"name":"DAGOHOY","code":"71217000"},{"name":"DANAO","code":"71218000"},{"name":"VALENCIA","code":"71247000"},{"name":"CANDIJAY","code":"71211000"},{"name":"PANGLAO","code":"71233000"},{"name":"DAUIS","code":"71219000"},{"name":"MABINI","code":"71231000"},{"name":"ALBURQUERQUE","code":"71201000"},{"name":"BACLAYON","code":"71205000"},{"name":"CORELLA","code":"71215000"},{"name":"CORTES","code":"71216000"},{"name":"BATUAN","code":"71207000"},{"name":"CARMEN","code":"71212000"},{"name":"BIEN UNIDO","code":"71248000"},{"name":"TAGBILARAN CITY (Capital)","code":"71242000"},{"name":"INABANGA","code":"71224000"},{"name":"TALIBON","code":"71243000"},{"name":"SAGBAYAN (BORJA)","code":"71236000"},{"name":"MARIBOJOC","code":"71232000"},{"name":"JETAFE","code":"71226000"},{"name":"SIERRA BULLONES","code":"71240000"},{"name":"CATIGBIAN","code":"71213000"},{"name":"PILAR","code":"71234000"},{"name":"ANTEQUERA","code":"71204000"},{"name":"BALILIHAN","code":"71206000"},{"name":"GUINDULMAN","code":"71223000"},{"name":"SEVILLA","code":"71239000"},{"name":"SIKATUNA","code":"71241000"},{"name":"SAN ISIDRO","code":"71237000"}]},{"code":"palawan","name":"PALAWAN","municipality":[{"name":"PUERTO PRINCESA CITY (Capital)","code":"175316000"}]},{"code":"ilocos norte","name":"ILOCOS NORTE","municipality":[{"name":"PIDDIG","code":"12818000"},{"name":"VINTAR","code":"12823000"},{"name":"BANNA (ESPIRITU)","code":"12811000"},{"name":"MARCOS","code":"12813000"},{"name":"CURRIMAO","code":"12808000"},{"name":"PAOAY","code":"12816000"},{"name":"DINGRAS","code":"12809000"},{"name":"SARRAT","code":"12821000"},{"name":"LAOAG CITY (Capital)","code":"12812000"},{"name":"SOLSONA","code":"12822000"},{"name":"BADOC","code":"12803000"},{"name":"BURGOS","code":"12806000"},{"name":"PASUQUIN","code":"12817000"},{"name":"SAN NICOLAS","code":"12820000"},{"name":"BATAC CITY","code":"12805000"},{"name":"BACARRA","code":"12802000"},{"name":"PINILI","code":"12819000"},{"name":"BANGUI","code":"12804000"}]},{"code":"abra","name":"ABRA","municipality":[{"name":"PIDIGAN","code":"140118000"},{"name":"SAN ISIDRO","code":"140121000"},{"name":"SAN QUINTIN","code":"140123000"},{"name":"PILAR","code":"140119000"},{"name":"DOLORES","code":"140107000"},{"name":"LA PAZ","code":"140108000"},{"name":"TAYUM","code":"140124000"},{"name":"LAGANGILANG","code":"140110000"},{"name":"SAN JUAN","code":"140122000"},{"name":"BUCAY","code":"140103000"},{"name":"MANABO","code":"140116000"},{"name":"SALLAPADAN","code":"140120000"},{"name":"BANGUED (Capital)","code":"140101000"},{"name":"LANGIDEN","code":"140112000"},{"name":"PEÑARRUBIA","code":"140117000"}]},{"code":"davao del sur","name":"DAVAO DEL SUR","municipality":[{"name":"DAVAO CITY","code":"112402000"},{"name":"DIGOS CITY (Capital)","code":"112403000"},{"name":"KIBLAWAN","code":"112406000"},{"name":"PADADA","code":"112411000"},{"name":"SULOP","code":"112414000"},{"name":"MATANAO","code":"112410000"},{"name":"BANSALAN","code":"112401000"},{"name":"HAGONOY","code":"112404000"},{"name":"MALALAG","code":"112408000"},{"name":"MAGSAYSAY","code":"112407000"}]},{"code":"capiz","name":"CAPIZ","municipality":[{"name":"CUARTERO","code":"61901000"},{"name":"MA-AYON","code":"61907000"},{"name":"SIGMA","code":"61916000"},{"name":"DUMALAG","code":"61903000"},{"name":"DAO","code":"61902000"},{"name":"MAMBUSAO","code":"61908000"},{"name":"SAPI-AN","code":"61915000"}]},{"code":"surigao del norte","name":"SURIGAO DEL NORTE","municipality":[{"name":"SURIGAO CITY (Capital)","code":"166724000"},{"name":"PLACER","code":"166717000"},{"name":"SISON","code":"166722000"},{"name":"MAINIT","code":"166714000"},{"name":"TUBOD","code":"166727000"},{"name":"ALEGRIA","code":"166701000"},{"name":"BACUAG","code":"166702000"},{"name":"SAN FRANCISCO (ANAO-AON)","code":"166719000"}]},{"code":"agusan del sur","name":"AGUSAN DEL SUR","municipality":[{"name":"BAYUGAN","code":"160301000"}]},{"code":"occidental mindoro","name":"OCCIDENTAL MINDORO","municipality":[{"name":"ABRA DE ILOG","code":"175101000"},{"name":"MAMBURAO (Capital)","code":"175106000"},{"name":"CALINTAAN","code":"175102000"},{"name":"RIZAL","code":"175108000"},{"name":"SAN JOSE","code":"175110000"},{"name":"SANTA CRUZ","code":"175111000"},{"name":"MAGSAYSAY","code":"175105000"},{"name":"SABLAYAN","code":"175109000"}]},{"code":"la union","name":"LA UNION","municipality":[{"name":"BAGULIN","code":"13304000"},{"name":"NAGUILIAN","code":"13311000"},{"name":"SANTO TOMAS","code":"13317000"},{"name":"SAN FERNANDO CITY (Capital)","code":"13314000"},{"name":"PUGO","code":"13312000"},{"name":"ROSARIO","code":"13313000"},{"name":"ARINGAY","code":"13302000"},{"name":"CABA","code":"13309000"},{"name":"BALAOAN","code":"13305000"},{"name":"BANGAR","code":"13306000"},{"name":"LUNA","code":"13310000"},{"name":"SANTOL","code":"13318000"},{"name":"SUDIPEN","code":"13319000"},{"name":"SAN GABRIEL","code":"13315000"},{"name":"BACNOTAN","code":"13303000"},{"name":"SAN JUAN","code":"13316000"},{"name":"TUBAO","code":"13320000"},{"name":"AGOO","code":"13301000"},{"name":"BAUANG","code":"13307000"}]},{"code":"negros occidental","name":"NEGROS OCCIDENTAL","municipality":[{"name":"SAGAY CITY","code":"64523000"},{"name":"BACOLOD CITY (Capital)","code":"64501000"},{"name":"MURCIA","code":"64520000"},{"name":"HINIGARAN","code":"64511000"},{"name":"MANAPLA","code":"64518000"},{"name":"VICTORIAS CITY","code":"64531000"},{"name":"CADIZ CITY","code":"64504000"},{"name":"HINOBA-AN (ASIA)","code":"64512000"},{"name":"PULUPANDAN","code":"64522000"},{"name":"BAGO CITY","code":"64502000"},{"name":"KABANKALAN CITY","code":"64515000"},{"name":"HIMAMAYLAN CITY","code":"64510000"},{"name":"ESCALANTE CITY","code":"64509000"},{"name":"TOBOSO","code":"64529000"},{"name":"ISABELA","code":"64514000"},{"name":"MOISES PADILLA (MAGALLON)","code":"64519000"},{"name":"BINALBAGAN","code":"64503000"},{"name":"SAN CARLOS CITY","code":"64524000"},{"name":"PONTEVEDRA","code":"64521000"},{"name":"SAN ENRIQUE","code":"64525000"},{"name":"CALATRAVA","code":"64505000"},{"name":"SILAY CITY","code":"64526000"},{"name":"TALISAY CITY","code":"64528000"},{"name":"LA CARLOTA CITY","code":"64516000"},{"name":"VALLADOLID","code":"64530000"},{"name":"LA CASTELLANA","code":"64517000"},{"name":"ENRIQUE B. MAGALONA (SARAVIA)","code":"64508000"}]},{"code":"bukidnon","name":"BUKIDNON","municipality":[{"name":"SUMILAO","code":"101319000"},{"name":"MANOLO FORTICH","code":"101314000"},{"name":"BAUNGON","code":"101301000"},{"name":"MALITBOG","code":"101313000"},{"name":"LIBONA","code":"101311000"},{"name":"TALAKAG","code":"101320000"}]},{"code":"agusan del norte","name":"AGUSAN DEL NORTE","municipality":[{"name":"CARMEN","code":"160204000"},{"name":"SANTIAGO","code":"160210000"},{"name":"TUBAY","code":"160211000"},{"name":"BUTUAN CITY (Capital)","code":"160202000"},{"name":"NASIPIT","code":"160209000"},{"name":"JABONGA","code":"160205000"},{"name":"CABADBARAN","code":"160203000"},{"name":"REMEDIOS T. ROMUALDEZ","code":"160212000"},{"name":"MAGALLANES","code":"160208000"},{"name":"BUENAVISTA","code":"160201000"},{"name":"KITCHARAO","code":"160206000"}]},{"code":"misamis oriental","name":"MISAMIS ORIENTAL","municipality":[{"name":"MAGSAYSAY (LINUGOS)","code":"104317000"},{"name":"BALINGOAN","code":"104303000"},{"name":"BINUANGAN","code":"104304000"},{"name":"KINOGUITAN","code":"104312000"},{"name":"SALAY","code":"104322000"},{"name":"SUGBONGCOGON","code":"104323000"},{"name":"CAGAYAN DE ORO CITY (Capital)","code":"104305000"},{"name":"OPOL","code":"104321000"},{"name":"EL SALVADOR","code":"104307000"},{"name":"ALUBIJID","code":"104301000"},{"name":"LIBERTAD","code":"104315000"},{"name":"GITAGUM","code":"104309000"},{"name":"INITAO","code":"104310000"},{"name":"TAGOLOAN","code":"104324000"},{"name":"VILLANUEVA","code":"104326000"},{"name":"GINGOOG CITY","code":"104308000"},{"name":"TALISAYAN","code":"104325000"},{"name":"MANTICAO","code":"104318000"},{"name":"NAAWAN","code":"104320000"},{"name":"MEDINA","code":"104319000"},{"name":"BALINGASAG","code":"104302000"},{"name":"JASAAN","code":"104311000"},{"name":"LUGAIT","code":"104316000"},{"name":"LAGUINDINGAN","code":"104314000"},{"name":"LAGONGLONG","code":"104313000"}]},{"code":"ilocos sur","name":"ILOCOS SUR","municipality":[{"name":"BURGOS","code":"12904000"},{"name":"CAOAYAN","code":"12907000"},{"name":"VIGAN CITY (Capital)","code":"12934000"},{"name":"SANTA CRUZ","code":"12924000"},{"name":"SANTA LUCIA","code":"12925000"},{"name":"SUYO","code":"12932000"},{"name":"SANTA MARIA","code":"12926000"},{"name":"SAN VICENTE","code":"12921000"},{"name":"SANTA CATALINA","code":"12923000"},{"name":"NAGBUKEL","code":"12913000"},{"name":"NARVACAN","code":"12914000"},{"name":"BANAYOYO","code":"12902000"},{"name":"LIDLIDDA","code":"12911000"},{"name":"SANTIAGO","code":"12927000"},{"name":"SALCEDO (BAUGEN)","code":"12916000"},{"name":"CANDON CITY","code":"12906000"},{"name":"SINAIT","code":"12930000"},{"name":"SANTA","code":"12922000"},{"name":"BANTAY","code":"12903000"},{"name":"SAN ILDEFONSO","code":"12919000"},{"name":"SANTO DOMINGO","code":"12928000"},{"name":"CABUGAO","code":"12905000"},{"name":"SAN JUAN (LAPOG)","code":"12920000"},{"name":"GALIMUYOD","code":"12909000"},{"name":"MAGSINGAL","code":"12912000"},{"name":"SAN ESTEBAN","code":"12918000"},{"name":"TAGUDIN","code":"12933000"}]},{"code":"nueva ecija","name":"NUEVA ECIJA","municipality":[{"name":"GUIMBA","code":"34911000"},{"name":"LICAB","code":"34914000"},{"name":"CUYAPO","code":"34906000"},{"name":"LLANERA","code":"34915000"},{"name":"TALAVERA","code":"34930000"},{"name":"MUÑOZ SCIENCE CITY","code":"34917000"},{"name":"SANTO DOMINGO","code":"34929000"},{"name":"ALIAGA","code":"34901000"},{"name":"CABANATUAN CITY","code":"34903000"},{"name":"CABIAO","code":"34904000"},{"name":"GENERAL MAMERTO NATIVIDAD","code":"34909000"},{"name":"PEÑARANDA","code":"34921000"},{"name":"SANTA ROSA","code":"34928000"},{"name":"SAN LEONARDO","code":"34927000"},{"name":"QUEZON","code":"34922000"},{"name":"TALUGTUG","code":"34931000"},{"name":"ZARAGOZA","code":"34932000"},{"name":"GAPAN CITY","code":"34908000"},{"name":"SAN ISIDRO","code":"34925000"},{"name":"SAN ANTONIO","code":"34924000"},{"name":"JAEN","code":"34912000"},{"name":"NAMPICUAN","code":"34918000"}]},{"code":"pangasinan","name":"PANGASINAN","municipality":[{"name":"ROSALES","code":"15531000"},{"name":"POZZORUBIO","code":"15530000"},{"name":"AGUILAR","code":"15502000"},{"name":"BUGALLON","code":"15515000"},{"name":"BAUTISTA","code":"15510000"},{"name":"ASINGAN","code":"15506000"},{"name":"URDANETA CITY","code":"15546000"},{"name":"BAYAMBANG","code":"15511000"},{"name":"BALUNGAO","code":"15507000"},{"name":"SANTA MARIA","code":"15539000"},{"name":"TAYUG","code":"15543000"},{"name":"SAN JACINTO","code":"15534000"},{"name":"ALCALA","code":"15504000"},{"name":"MAPANDAN","code":"15528000"},{"name":"MANGALDAN","code":"15526000"},{"name":"DAGUPAN CITY","code":"15518000"}]},{"code":"misamis occidental","name":"MISAMIS OCCIDENTAL","municipality":[{"name":"OROQUIETA CITY (Capital)","code":"104209000"},{"name":"JIMENEZ","code":"104207000"},{"name":"SINACABAN","code":"104214000"},{"name":"TANGUB CITY","code":"104215000"},{"name":"BONIFACIO","code":"104203000"},{"name":"SAPANG DALAGA","code":"104213000"},{"name":"PANAON","code":"104211000"},{"name":"CLARIN","code":"104205000"},{"name":"OZAMIS CITY","code":"104210000"},{"name":"ALORAN","code":"104201000"},{"name":"TUDELA","code":"104216000"},{"name":"PLARIDEL","code":"104212000"}]},{"code":"kalinga","name":"KALINGA","municipality":[{"name":"RIZAL (LIWAN)","code":"143211000"},{"name":"TABUK (Capital)","code":"143213000"}]},{"code":"apayao","name":"APAYAO","municipality":[{"name":"FLORA","code":"148103000"},{"name":"LUNA","code":"148105000"},{"name":"SANTA MARCELA","code":"148107000"},{"name":"PUDTOL","code":"148106000"}]},{"code":"zamboanga del norte","name":"ZAMBOANGA DEL NORTE","municipality":[{"name":"JOSE DALMAN (PONOT)","code":"97222000"},{"name":"MANUKAN","code":"97207000"},{"name":"LABASON","code":"97205000"},{"name":"BACUNGAN (Leon T. Postigo)","code":"97226000"},{"name":"SINDANGAN","code":"97218000"},{"name":"KATIPUNAN","code":"97203000"},{"name":"PRES. MANUEL A. ROXAS","code":"97211000"},{"name":"POLANCO","code":"97210000"},{"name":"DIPOLOG CITY (Capital)","code":"97202000"},{"name":"LILOY","code":"97206000"},{"name":"SALUG","code":"97213000"}]},{"code":"surigao del sur","name":"SURIGAO DEL SUR","municipality":[{"name":"CAGWAIT","code":"166804000"},{"name":"TAGO","code":"166818000"},{"name":"SAN MIGUEL","code":"166816000"},{"name":"TAGBINA","code":"166817000"},{"name":"LANUZA","code":"166810000"},{"name":"BAROBO","code":"166801000"},{"name":"CARMEN","code":"166806000"},{"name":"MARIHATAG","code":"166814000"},{"name":"LIANGA","code":"166811000"},{"name":"SAN AGUSTIN","code":"166815000"}]},{"code":"maguindanao","name":"MAGUINDANAO","municipality":[{"name":"SULTAN KUDARAT (NULING)","code":"153812000"},{"name":"SULTAN MASTURA","code":"153824000"},{"name":"KABUNTALAN (TUMBAO)","code":"153814000"},{"name":"NORTHERN KABUNTALAN","code":"153834000"},{"name":"DATU ODIN SINSUAT (DINAIG)","code":"153807000"},{"name":"PARANG","code":"153811000"}]},{"code":"camarines sur","name":"CAMARINES SUR","municipality":[{"name":"LIBMANAN","code":"51718000"},{"name":"SIPOCOT","code":"51734000"},{"name":"CALABANGA","code":"51708000"},{"name":"NAGA CITY","code":"51724000"},{"name":"PILI (Capital)","code":"51728000"},{"name":"MILAOR","code":"51721000"},{"name":"MINALABAC","code":"51722000"},{"name":"BULA","code":"51706000"},{"name":"NABUA","code":"51723000"},{"name":"BAAO","code":"51701000"},{"name":"BOMBON","code":"51704000"},{"name":"CABUSAO","code":"51707000"},{"name":"SAN FERNANDO","code":"51732000"},{"name":"BATO","code":"51703000"},{"name":"CAMALIGAN","code":"51709000"},{"name":"CANAMAN","code":"51710000"},{"name":"GAINZA","code":"51713000"},{"name":"PAMPLONA","code":"51726000"},{"name":"MAGARAO","code":"51720000"}]},{"code":"sarangani","name":"SARANGANI","municipality":[{"name":"MALAPATAN","code":"128006000"},{"name":"ALABEL (Capital)","code":"128001000"},{"name":"GLAN","code":"128002000"}]},{"code":"pampanga","name":"PAMPANGA","municipality":[{"name":"ARAYAT","code":"35403000"}]},{"code":"bulacan","name":"BULACAN","municipality":[{"name":"SAN JOSE DEL MONTE CITY","code":"31420000"},{"name":"BUSTOS","code":"31406000"},{"name":"PLARIDEL","code":"31417000"},{"name":"PANDI","code":"31415000"},{"name":"SANTA MARIA","code":"31423000"},{"name":"HAGONOY","code":"31409000"},{"name":"PAOMBONG","code":"31416000"},{"name":"BOCAUE","code":"31404000"},{"name":"MARILAO","code":"31411000"},{"name":"MEYCAUAYAN","code":"31412000"},{"name":"GUIGUINTO","code":"31408000"},{"name":"MALOLOS (Capital)","code":"31410000"},{"name":"BULACAN","code":"31405000"},{"name":"OBANDO","code":"31414000"},{"name":"BALAGTAS (BIGAA)","code":"31402000"},{"name":"CALUMPIT","code":"31407000"}]},{"code":"lanao del norte","name":"LANAO DEL NORTE","municipality":[{"name":"ILIGAN CITY","code":"103504000"},{"name":"BACOLOD","code":"103501000"},{"name":"KAUSWAGAN","code":"103507000"},{"name":"BAROY","code":"103503000"},{"name":"LALA","code":"103509000"},{"name":"LINAMON","code":"103510000"},{"name":"MATUNGAO","code":"103513000"},{"name":"POONA PIAGAPO","code":"103517000"},{"name":"KAPATAGAN","code":"103505000"},{"name":"KOLAMBUGAN","code":"103508000"},{"name":"SULTAN NAGA DIMAPORO","code":"103506000"},{"name":"MAGSAYSAY","code":"103511000"},{"name":"MAIGO","code":"103512000"},{"name":"SALVADOR","code":"103518000"},{"name":"BALOI","code":"103502000"},{"name":"PANTAO RAGAT","code":"103516000"},{"name":"SAPAD","code":"103519000"},{"name":"NUNUNGAN","code":"103515000"},{"name":"PANTAR","code":"103523000"},{"name":"TAGOLOAN","code":"103520000"}]},{"code":"aklan","name":"AKLAN","municipality":[{"name":"IBAJAY","code":"60406000"},{"name":"MAKATO","code":"60411000"},{"name":"TANGALAN","code":"60417000"},{"name":"BANGA","code":"60403000"},{"name":"MALINAO","code":"60413000"},{"name":"NABAS","code":"60414000"},{"name":"NEW WASHINGTON","code":"60415000"},{"name":"NUMANCIA","code":"60416000"},{"name":"KALIBO (Capital)","code":"60407000"},{"name":"BATAN","code":"60404000"},{"name":"ALTAVAS","code":"60401000"},{"name":"LEZO","code":"60408000"},{"name":"BALETE","code":"60402000"}]},{"code":"north cotabato","name":"NORTH COTABATO","municipality":[{"name":"PIGKAWAYAN","code":"124711000"},{"name":"COTABATO CITY","code":"129804000"}]},{"code":"tarlac","name":"TARLAC","municipality":[{"name":"ANAO","code":"36901000"},{"name":"RAMOS","code":"36912000"}]},{"code":"davao oriental","name":"DAVAO ORIENTAL","municipality":[{"name":"TARRAGONA","code":"112511000"},{"name":"BANAYBANAY","code":"112502000"},{"name":"LUPON","code":"112507000"},{"name":"MATI (Capital)","code":"112509000"},{"name":"SAN ISIDRO","code":"112510000"},{"name":"BOSTON","code":"112503000"},{"name":"CATEEL","code":"112505000"},{"name":"CARAGA","code":"112504000"},{"name":"BAGANGA","code":"112501000"},{"name":"MANAY","code":"112508000"}]},{"code":"batangas","name":"BATANGAS","municipality":[{"name":"SANTO TOMAS","code":"41028000"}]},{"code":"south cotabato","name":"SOUTH COTABATO","municipality":[{"name":"GENERAL SANTOS CITY (DADIANGAS)","code":"126303000"}]},{"code":"laguna","name":"LAGUNA","municipality":[{"name":"FAMY","code":"43408000"},{"name":"SANTA MARIA","code":"43427000"},{"name":"SINILOAN","code":"43429000"},{"name":"CABUYAO","code":"43404000"},{"name":"SANTA ROSA","code":"43428000"},{"name":"BINAN","code":"43403000"},{"name":"CALAMBA CITY","code":"43405000"},{"name":"SAN PABLO CITY","code":"43424000"},{"name":"CALAUAN","code":"43406000"},{"name":"NAGCARLAN","code":"43417000"},{"name":"ALAMINOS","code":"43401000"},{"name":"BAY","code":"43402000"},{"name":"LOS BAÑOS","code":"43411000"},{"name":"PILA","code":"43422000"},{"name":"VICTORIA","code":"43430000"},{"name":"MABITAC","code":"43414000"},{"name":"PANGIL","code":"43421000"},{"name":"SAN PEDRO","code":"43425000"},{"name":"SANTA CRUZ (Capital)","code":"43426000"},{"name":"PAGSANJAN","code":"43419000"},{"name":"MAGDALENA","code":"43415000"}]},{"code":"rizal","name":"RIZAL","municipality":[{"name":"JALA-JALA","code":"45807000"},{"name":"PILILLA","code":"45810000"}]},{"code":"mountain province","name":"MOUNTAIN PROVINCE","municipality":[{"name":"PARACELIS","code":"144406000"}]},{"code":"cagayan","name":"CAGAYAN","municipality":[{"name":"APARRI","code":"21505000"},{"name":"LAL-LO","code":"21516000"}]},{"code":"oriental mindoro","name":"ORIENTAL MINDORO","municipality":[{"name":"GLORIA","code":"175206000"},{"name":"BULALACAO (SAN PEDRO)","code":"175204000"},{"name":"PINAMALAYAN","code":"175209000"}]},{"code":"quezon","name":"QUEZON","municipality":[{"name":"DOLORES","code":"45615000"},{"name":"REAL","code":"45638000"}]},{"code":"ifugao","name":"IFUGAO","municipality":[{"name":"ALFONSO LISTA (POTIA)","code":"142707000"}]},{"code":"iloilo","name":"ILOILO","municipality":[{"name":"SAN RAFAEL","code":"63042000"}]},{"code":"isabela","name":"ISABELA","municipality":[{"name":"CAUAYAN CITY","code":"23108000"}]},{"code":"cavite","name":"CAVITE","municipality":[{"name":"BACOOR","code":"42103000"},{"name":"DASMARIÑAS","code":"42106000"},{"name":"CARMONA","code":"42104000"}]}];

    if (FILTER_TYPE == 'layer') {
      if(!$rootScope.locations) $rootScope.locations = allLayersLocation;
    }
    

    /*
    * Pagination
    */
    // Control what happens when the total results change
    $scope.$watch('total_counts', function(){
      $scope.numpages = Math.round(
        ($scope.total_counts / $scope.query.limit) + 0.49
      );

      // In case the user is viewing a page > 1 and a
      // subsequent query returns less pages, then
      // reset the page to one and search again.
      if($scope.numpages < $scope.page){
        $scope.page = 1;
        $scope.query.offset = 0;
        query_api($scope.query);
      }

      // In case of no results, the number of pages is one.
      if($scope.numpages == 0){$scope.numpages = 1};
    });

    $scope.paginate_down = function(){
      if($scope.page > 1){
        $scope.page -= 1;
        $scope.query.offset =  $scope.query.limit * ($scope.page - 1);
        query_api($scope.query);
      }
    }

    $scope.paginate_up = function(){
      if($scope.numpages > $scope.page){
        $scope.page += 1;
        $scope.query.offset = $scope.query.limit * ($scope.page - 1);
        query_api($scope.query);
      }
    }
    /*
    * End pagination
    */


    if (!Configs.hasOwnProperty("disableQuerySync")) {
        // Keep in sync the page location with the query object
        $scope.$watch('query', function(){
          $location.search($scope.query);
        }, true);
    }

    $scope.clearSearch = function(evt) {
      var data_filter = 'keywords__slug__in';

      evt.preventDefault();

      if($('#myProvinceSelect').length){
        $('#myProvinceSelect').val(undefined);
      }
      if($('#myMunicipalitySelect').length){
        $('#myMunicipalitySelect').val(undefined);
      }
      if($('#myHazardSelect').length){
        $('#myHazardSelect').val(undefined);
      }
      if($('#myScaleSelect').length){
        $('#myScaleSelect').val(undefined);
      }

      $scope.query[data_filter] = ['clear-results'];
      // $window.location.reload(true);
    }

    $scope.validateLocation = function(selectedProvince, selectedMunicipality) {
      if(
        typeof selectedProvince === 'undefined' ||
        typeof selectedMunicipality === 'undefined'
      ) return true;

      if( typeof selectedMunicipality.code === '') return true;

      if($('#myMunicipalitySelect')[0].selectedOptions.length === 0) return true;
      
      // Validate selectedMunicipality
      var found = selectedProvince.municipality.some(function (municipality) {
        return municipality.code === selectedMunicipality.code;
      });

      if(!found) return true;

      return false;
    }

    $scope.validateFilter = function(selectedHazard, selectedScale) {
      if(
        typeof selectedHazard === 'undefined' &&
        typeof selectedScale === 'undefined'
      ) return true;

      if(
        $('#myHazardSelect')[0].selectedOptions.length === 0 &&
        $('#myScaleSelect')[0].selectedOptions.length === 0
      ) return true;

      return false;
    }

    /*
    * Listens to province select field
    */
    $scope.location_submit = function(selectedProvince, selectedMunicipality){  
      if(
        typeof selectedProvince === 'undefined' ||
        typeof selectedMunicipality === 'undefined'
      ) return false;

      if( typeof selectedMunicipality.code === '') return false;

      // Validate selectedMunicipality
      var found = selectedProvince.municipality.some(function (municipality) {
        return municipality.code === selectedMunicipality.code;
      });

      if(!found) return;

      // Update datacoverage map visibility
      $('#mainMapSideHolder').css('visibility', 'visible')
      $('#mainMapSideHolder #ext-comp-1009').css('display', 'block');

      var query_entry = [];
      var data_filter = 'keywords__slug__in';
      var value = selectedMunicipality ? selectedMunicipality.code : selectedProvince.code;
            
      // If the query object has the record then grab it
      // if ($scope.query.hasOwnProperty(data_filter)){
      //   if ($scope.query[data_filter] instanceof Array){
      //     query_entry = $scope.query[data_filter];
      //   }else{
      //     query_entry.push($scope.query[data_filter]);
      //   }
      // }

      // Remove mun_code
      // query_entry = query_entry.filter(function(key){
      //   return !Number(key);
      // });

      query_entry.push(value);
      
      delete $scope.query['extent'];

      $scope.query[data_filter] = query_entry;


      if (FILTER_TYPE == 'layer') {
        query_api($scope.query);
      }

      $scope.hasNoFilter = false;
    }

    /*
    * Listens to hazard scale select field
    */
    $scope.filters_submit = function(selectedHazard, selectedScale){  
      var query_entry = [];
      var data_filter = 'keywords__slug__in';
      
      if(selectedHazard){
        query_entry.push(selectedHazard.filter);
      }
      if(selectedScale){
        query_entry.push(selectedScale.filter);
      }
            
      delete $scope.query['extent'];
      $scope.query[data_filter] = query_entry;

      $scope.hasNoFilter = false;
    }
    /*
    * Add the selection behavior to the element, it adds/removes the 'active' class
    * and pushes/removes the value of the element from the query object
    */
    $scope.multiple_choice_listener = function($event){
      var element = $($event.target);
      var query_entry = [];
      var data_filter = element.attr('data-filter');
      var value = element.attr('data-value');

      // If the query object has the record then grab it
      if ($scope.query.hasOwnProperty(data_filter)){

        // When in the location are passed two filters of the same
        // type then they are put in an array otherwise is a single string
        if ($scope.query[data_filter] instanceof Array){
          query_entry = $scope.query[data_filter];
        }else{
          query_entry.push($scope.query[data_filter]);
        }
      }

      // If the element is active active then deactivate it
      if(element.hasClass('active')){
        // clear the active class from it
        element.removeClass('active');

        // Remove the entry from the correct query in scope

        query_entry.splice(query_entry.indexOf(value), 1);
      }
      // if is not active then activate it
      else if(!element.hasClass('active')){
        // Add the entry in the correct query
        if (query_entry.indexOf(value) == -1){
          query_entry.push(value);
        }
        element.addClass('active');
      }

      //save back the new query entry to the scope query
      $scope.query[data_filter] = query_entry;

      //if the entry is empty then delete the property from the query
      if(query_entry.length == 0){
        delete($scope.query[data_filter]);
      }
      query_api($scope.query);
    }

    $scope.single_choice_listener = function($event){
      var element = $($event.target);
      var query_entry = [];
      var data_filter = element.attr('data-filter');
      var value = element.attr('data-value');

      // If the query object has the record then grab it
      if ($scope.query.hasOwnProperty(data_filter)){
        query_entry = $scope.query[data_filter];
      }

      if(!element.hasClass('selected')){
        // Add the entry in the correct query
        query_entry = value;

        // clear the active class from it
        element.parents('ul').find('a').removeClass('selected');

        element.addClass('selected');

        //save back the new query entry to the scope query
        $scope.query[data_filter] = query_entry;

        query_api($scope.query);
      }
    }

    /*
    * Text search management
    */
    var text_autocomplete = $('#text_search_input').yourlabsAutocomplete({
          url: AUTOCOMPLETE_URL_RESOURCEBASE,
          choiceSelector: 'span',
          hideAfter: 200,
          minimumCharacters: 1,
          placeholder: gettext('Enter your text here ...'),
          autoHilightFirst: false
    });

    $('#text_search_input').keypress(function(e) {
      if(e.which == 13) {
        $('#text_search_btn').click();
        $('.yourlabs-autocomplete').hide();
      }
    });

    $('#text_search_input').bind('selectChoice', function(e, choice, text_autocomplete) {
          if(choice[0].children[0] == undefined) {
              $('#text_search_input').val($(choice[0]).text());
              $('#text_search_btn').click();
          }
    });

    $('#text_search_btn').click(function(){
        if (HAYSTACK_SEARCH)
            $scope.query['q'] = $('#text_search_input').val();
        else
            $scope.query['title__icontains'] = $('#text_search_input').val();
        query_api($scope.query);
    });

    /*
    * Region search management
    */
    var region_autocomplete = $('#region_search_input').yourlabsAutocomplete({
          url: AUTOCOMPLETE_URL_REGION,
          choiceSelector: 'span',
          hideAfter: 200,
          minimumCharacters: 1,
          appendAutocomplete: $('#region_search_input'),
          placeholder: gettext('Enter your region here ...')
    });
    $('#region_search_input').bind('selectChoice', function(e, choice, region_autocomplete) {
          if(choice[0].children[0] == undefined) {
              $('#region_search_input').val(choice[0].innerHTML);
              $('#region_search_btn').click();
          }
    });

    $('#region_search_btn').click(function(){
        $scope.query['regions__name__in'] = $('#region_search_input').val();
        query_api($scope.query);
    });

    $scope.feature_select = function($event){
      var element = $($event.target);
      var article = $(element.parents('article')[0]);
      if (article.hasClass('resource_selected')){
        element.html('Select');
        article.removeClass('resource_selected');
      }
      else{
        element.html('Deselect');
        article.addClass('resource_selected');
      }
    };

    /*
    * Date management
    */

    $scope.date_query = {
      'date__gte': '',
      'date__lte': ''
    };
    var init_date = true;
    $scope.$watch('date_query', function(){
      if($scope.date_query.date__gte != '' && $scope.date_query.date__lte != ''){
        $scope.query['date__range'] = $scope.date_query.date__gte + ',' + $scope.date_query.date__lte;
        delete $scope.query['date__gte'];
        delete $scope.query['date__lte'];
      }else if ($scope.date_query.date__gte != ''){
        $scope.query['date__gte'] = $scope.date_query.date__gte;
        delete $scope.query['date__range'];
        delete $scope.query['date__lte'];
      }else if ($scope.date_query.date__lte != ''){
        $scope.query['date__lte'] = $scope.date_query.date__lte;
        delete $scope.query['date__range'];
        delete $scope.query['date__gte'];
      }else{
        delete $scope.query['date__range'];
        delete $scope.query['date__gte'];
        delete $scope.query['date__lte'];
      }
      if (!init_date){
        query_api($scope.query);
      }else{
        init_date = false;
      }

    }, true);

    /*
    * Spatial search
    */
    if ($('.leaflet_map').length > 0) {
      angular.extend($scope, {
        layers: {
          baselayers: {
            stamen: {
              name: 'Toner Lite',
              type: 'xyz',
              url: 'http://{s}.tile.stamen.com/toner-lite/{z}/{x}/{y}.png',
              layerOptions: {
                subdomains: ['a', 'b', 'c'],
                attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>',
                continuousWorld: true
              }
            }
          }
        },
        map_center: {
          lat: 5.6,
          lng: 3.9,
          zoom: 0
        },
        defaults: {
          zoomControl: false
        }
      });

			
      var leafletData = $injector.get('leafletData'),
          map = leafletData.getMap('filter-map');

      map.then(function(map){
        map.on('moveend', function(){
          $scope.query['extent'] = map.getBounds().toBBoxString();
          delete $scope.query['keywords__slug__in'];
                    
          $scope.hasNoFilter = false;
          query_api($scope.query);
        });
      });
    
      var showMap = false;
      $('#_extent_filter').click(function(evt) {
     	  showMap = !showMap
        if (showMap){
          leafletData.getMap().then(function(map) {
            map.invalidateSize();
          });
        } 
      });
    }

    $scope.hasNoFilter = true;
  });
})();
