/*jshint multistr:true */

this.recline = this.recline || {};
this.recline.View = this.recline.View || {};

(function($, my) {

my.ValueFilter = Backbone.View.extend({
  className: 'recline-filter-editor well', 
  template: ' \
    <div class="filters"> \
      <h3>Filters</h3> \
      <button class="btn js-add-filter add-filter">Filter hinuufügen</button> \
      <form class="form-stacked js-add" style="display: none;"> \
        <fieldset> \
          <label>Spalten</label> \
          <select class="fields"> \
            {{#fields}} \
            <option value="{{id}}">{{label}}</option> \
            {{/fields}} \
          </select> \
          <button type="submit" class="btn">Hinzufügen</button> \
        </fieldset> \
      </form> \
      <form class="form-stacked js-edit"> \
        {{#filters}} \
          {{{filterRender}}} \
        {{/filters}} \
        {{#filters.length}} \
        <button type="submit" class="btn update-filter">Aktualisieren</button> \
        {{/filters.length}} \
      </form> \
    </div> \
  ',
  filterTemplates: {
    term: ' \
      <div class="filter-{{type}} filter"> \
        <fieldset> \
          {{field}} \
          <a class="js-remove-filter" href="#" title="Filter entfernen" data-filter-id="{{id}}">&times;</a> \
          <input type="text" value="{{term}}" name="term" data-filter-field="{{field}}" data-filter-id="{{id}}" data-filter-type="{{type}}" /> \
        </fieldset> \
      </div> \
    '
  },
  events: {
    'click .js-remove-filter': 'onRemoveFilter',
    'click .js-add-filter': 'onAddFilterShow',
    'submit form.js-edit': 'onTermFiltersUpdate',
    'submit form.js-add': 'onAddFilter'
  },
  initialize: function() {
    this.el = $(this.el);
    _.bindAll(this, 'render');
    this.model.fields.bind('all', this.render);
    this.model.queryState.bind('change', this.render);
    this.model.queryState.bind('change:filters:new-blank', this.render);
    this.render();
  },
  render: function() {
    var self = this;
    var tmplData = $.extend(true, {}, this.model.queryState.toJSON());
    // we will use idx in list as the id ...
    tmplData.filters = _.map(tmplData.filters, function(filter, idx) {
      filter.id = idx;
      return filter;
    });
    tmplData.fields = this.model.fields.toJSON();
    tmplData.filterRender = function() {
      return Mustache.render(self.filterTemplates.term, this);
    };
    var out = Mustache.render(this.template, tmplData);
    this.el.html(out);
  },
  updateFilter: function(input) {
    var self = this;
    var filters = self.model.queryState.get('filters');
    var $input = $(input);
    var filterIndex = parseInt($input.attr('data-filter-id'), 10);
    var value = $input.val();
    filters[filterIndex].term = value;
  },
  onAddFilterShow: function(e) {
    e.preventDefault();
    var $target = $(e.target);
    $target.hide();
    this.el.find('form.js-add').show();
  },
  onAddFilter: function(e) {
    e.preventDefault();
    var $target = $(e.target);
    $target.hide();
    var field = $target.find('select.fields').val();
    this.model.queryState.addFilter({type: 'term', field: field});
  },
  onRemoveFilter: function(e) {
    e.preventDefault();
    var $target = $(e.target);
    var filterId = $target.attr('data-filter-id');
    this.model.queryState.removeFilter(filterId);
  },
  onTermFiltersUpdate: function(e) {
    var self = this;
    e.preventDefault();
    var filters = self.model.queryState.get('filters');
    var $form = $(e.target);
    _.each($form.find('input'), function(input) {
      self.updateFilter(input);
    });
    self.model.queryState.set({filters: filters, from: 0});
    self.model.queryState.trigger('change');
  }
});

})(jQuery, recline.View);