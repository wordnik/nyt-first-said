var d3 = require('d3-selection');
var siteRoot = d3.select('#site-root');
var accessor = require('accessor')();
var normalizeObjects = require('normalize-objects')({
  defaults: {
    date: undefined,
  },
});
var curry = require('lodash.curry');
var fieldsThatShouldRenderAsJSON = require('../json-fields');
var jsonFieldNames = fieldsThatShouldRenderAsJSON.map((obj) => obj.field);
var dateFields = [];

var selectFields = ['environment', 'form', 'purpose', 'releaseState'];
var fixedValuesForFields = {};

function renderSites({ siteData }) {
  normalizeObjects(siteData);
  var sites = siteRoot.selectAll('.site').data(siteData, accessor('site'));
  sites.exit().remove();

  if (siteData.length < 1) {
    return;
  }

  var fields = Object.keys(siteData[0]);

  // Header row
  var headerRow = siteRoot.append('thead');
  headerRow
    .selectAll('.field-label')
    .data(fields, (x) => x)
    .enter()
    .append('th')
    .classed('field-label', true)
    .text((x) => x);

  var newSites = sites.enter().append('tr').classed('site', true);
  appendElementsForSites(newSites, siteData[0]);

  var sitesToUpdate = newSites.merge(sites);
  fields.forEach(curry(updateSitesField)(sitesToUpdate));
}

function appendElementsForSites(sitesSel, exampleSite) {
  // Move 'site' to the front.
  var fields = Object.keys(exampleSite);
  fields.splice(fields.indexOf('site'), 1);
  fields.sort();
  fields.unshift('site');
  fields.forEach(appendElementsForField);

  function appendElementsForField(field) {
    let container = sitesSel.append('td').classed('field-container', true);
    // container.append('div').classed('field-label', true).text(field);
    appendControlForValue(container, field, typeof exampleSite[field]);
  }
}

function appendControlForValue(container, field, valueType) {
  if (jsonFieldNames.includes(field)) {
    container.append('textarea').attr('data-of', field);
  } else if (selectFields.includes(field)) {
    let selectControl = container.append('select').attr('data-of', field);
    let options = selectControl
      .selectAll('option')
      .data(fixedValuesForFields[field]);
    options.exit().remove();
    // let existingOptions = options
    //   .enter()
    //   .append('option')
    //   .merge(options)
    //   .text(accessor('identity'))
    //   .attr('value', accessor('identity'));
  } else {
    let input = container.append('input').attr('data-of', field);
    if (valueType === 'boolean') {
      input.attr('type', 'checkbox');
    } else if (dateFields.indexOf(field) !== -1) {
      input.attr('type', 'date');
    } else {
      input.attr('type', 'text');
    }
  }
}

function updateSitesField(sitesSel, field) {
  if (jsonFieldNames.includes(field)) {
    sitesSel.select(`[data-of=${field}]`).text(curry(getValueForField)(field));
  } else if (selectFields.includes(field)) {
    sitesSel
      .select(`[data-of=${field}]`)
      .selectAll('option')
      .attr('selected', getSelectedAttrValue);
  } else {
    sitesSel
      .select(`[data-of=${field}]`)
      .attr('value', curry(getValueForField)(field))
      .each(curry(setChecked)(field));
  }

  function getSelectedAttrValue(optionValue) {
    const fieldValue = d3.select(this.parentNode).datum()[field];
    console.log(fieldValue, optionValue, 'match', fieldValue === optionValue);
    return fieldValue === optionValue ? 'selected' : null;
  }
}

// If this field has a boolean value and that value is true, then
// checked should be set on the element.
function setChecked(field, site) {
  var value = site[field];
  if (value && typeof value === 'boolean') {
    this.setAttribute('checked', null);
  }
}

function getValueForField(fieldName, site) {
  var fieldDef = fieldsThatShouldRenderAsJSON.find(
    (obj) => obj.field === fieldName
  );
  if (fieldDef) {
    return JSON.stringify(site[fieldName]);
    // }
    // else if (dateFields.indexOf(field) !== -1) {
    //   // input type=date supports only dates, not dates with times.
    //   var dateWithTime = site[field];
    //   if (dateWithTime) {
    //     return dateWithTime.split('T')[0];
    //   }
  } else {
    return site[fieldName];
  }
}

module.exports = renderSites;
