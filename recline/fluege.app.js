jQuery(function($) {
  window.dataExplorer = null;
  window.explorerDiv = $('.data-explorer-here');

  // This is some fancy stuff to allow configuring the multiview from
  // parameters in the query string
  //
  // For more on state see the view documentation.
  var state = recline.View.parseQueryString(decodeURIComponent(window.location.search));
  if (state) {
    _.each(state, function(value, key) {
      try {
        value = JSON.parse(value);
      } catch(e) {}
      state[key] = value;
    });
  } else {
    state.url = 'demo';
  }
  var dataset = null;
  if (state.dataset || state.url) {
    var datasetInfo = _.extend({
        url: state.url,
        backend: state.backend
      },
      state.dataset
    );
    dataset = new recline.Model.Dataset(datasetInfo);
  } else {
    dataset = new recline.Model.Dataset({
      records: [
        {startdatum: '2011-01-01', dauer: "1:30", maschine: "D-AZEM", start: "Berlin", landung: "Islamabad", route: { "type": "LineString", "coordinates": [ [12.49, 52.88 ], [70.31, 31.05 ] ] } },
		{startdatum: '2011-02-04', dauer: "9:20", maschine: "D-AZEM", start: "Islamabad", landung: "Minsk", route: { "type": "LineString", "coordinates": [ [13.40, 52.56], [-1.60, 54.97] ] } },
		{startdatum: '2011-02-01', dauer: "0:30", maschine: "D-AZEM", start: "Islamabad", landung: "Washington", route: { "type": "LineString", "coordinates": [ [13.40, 52.56], [-1.60, 54.97] ] } },
		{startdatum: '2011-02-06', dauer: "0:30", maschine: "D-AZEM", start: "Berlin", landung: "Washington", route: { "type": "LineString", "coordinates": [ [13.40, 52.56], [-1.60, 54.97] ] } },
		{startdatum: '2011-02-08', dauer: "1:45", maschine: "D-AZEM", start: "Berlin", landung: "München", route: { "type": "LineString", "coordinates": [ [13.40, 52.56], [-1.60, 54.97] ] } },
		{startdatum: '2011-02-08', dauer: "1:59", maschine: "D-AZEM", start: "Berlin", landung: "München", route: { "type": "LineString", "coordinates": [ [13.40, 52.56], [-1.60, 54.97] ] } },
		{startdatum: '2011-06-10', dauer: "1:10", maschine: "D-AZEM", start: "Berlin", landung: "München", route: { "type": "LineString", "coordinates": [ [13.40, 52.56], [-1.60, 54.97] ] } },

      ],
      // let's be really explicit about fields
      // Plus take opportunity to set date to be a date field and set some labels
      fields: [
        {id: 'startdatum', type: 'date', label: 'Start'},
        {id: 'dauer', type: 'string', label: 'Dauer'},
        {id: 'maschine', type: 'string', label: 'Maschine'},
		{id: 'start', type: 'string', label: 'Start'},
		{id: 'landung', type: 'string', label: 'Landung'},
        {id: 'route', type: 'geojson', label: 'Route'}
      ]
    });
  }
  createExplorer(dataset, state);
});


// make Explorer creation / initialization in a function so we can call it
// again and again
var createExplorer = function(dataset, state) {
  // remove existing data explorer view
  var reload = false;
  if (window.dataExplorer) {
    window.dataExplorer.remove();
    reload = true;
  }
  window.dataExplorer = null;
  var $el = $('<div />');
  $el.appendTo(window.explorerDiv);

  var views = [
    {
      id: 'grid',
      label: 'Tabelle',
      view: new recline.View.SlickGrid({
        model: dataset
      })
    },
    {
      id: 'map',
      label: 'Karte',
      view: new recline.View.Map({
        model: dataset,
        state : { geomField: "route" }
      })
    },
  ];

  window.dataExplorer = new recline.View.MultiView({
    model: dataset,
    el: $el,
    state: state,
    views: views
  });
}

