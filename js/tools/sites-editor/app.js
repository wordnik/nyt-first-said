var handleError = require('handle-error-web');
var wireControls = require('./dom/wire-controls');
var renderSites = require('./dom/render-sites');
var renderDownloadLink = require('render-dl-link');
var noThrowJSONParse = require('no-throw-json-parse');
var fieldsThatShouldRenderAsJSON = require('./json-fields');

(function go() {
  window.onerror = reportTopLevelError;
  wireControls({
    onLoadSites({ sites }) {
      renderSites({ siteData: Object.values(sites) });
    },
    onSaveSites,
  });
})();

function reportTopLevelError(msg, url, lineNo, columnNo, error) {
  handleError(error);
}

function onSaveSites({ sites }) {
  sites.forEach(convertJSONFieldsToObjects);
  // If we ever have date fields, convert them here.
  // sites.forEach(convertDateFieldsToDates);
  var sitesDict = arrangeSitesIntoDict(sites);
  renderDownloadLink({
    blob: new Blob([JSON.stringify(sitesDict, null, 2)], {
      type: 'application/json',
    }),
    parentSelector: '#save-section',
    downloadLinkText: 'Download the sites file',
    filename: 'target_sites.json',
  });
}

function arrangeSitesIntoDict(sites) {
  var dict = {};
  sites.forEach(addToDict);
  return dict;

  function addToDict(site) {
    dict[site.site] = site;
  }
}

function convertJSONFieldsToObjects(site) {
  fieldsThatShouldRenderAsJSON.forEach(convertJSONFieldToObject);

  function convertJSONFieldToObject({ field, type }) {
    var value = site[field];
    if (value && typeof value === 'string') {
      let fallbackVal = [];
      if (type === 'object') {
        fallbackVal = {};
      }
      site[field] = noThrowJSONParse(value, fallbackVal);
    } else {
      // Defaulting to array instead of object.
      site[field] = [];
    }
  }
}

// function convertDateFieldsToDates(site) {
// dateFields.forEach(convertDateFieldToDate);
// function convertDateFieldToDate(field) {
//   var value = site[field];
//   if (value && typeof value === 'string') {
//     site[field] = new Date(value);
//   }
// }
// }
