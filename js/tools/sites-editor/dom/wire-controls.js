var d3 = require('d3-selection');
var of = require('object-form');

var listenersInit = false;
var objectFromDOM = of.ObjectFromDOM({});

function wireControls({ onLoadSites, onSaveSites }) {
  if (listenersInit) {
    return;
  }
  listenersInit = true;

  d3.select('#save-button').on('click', onSave);
  d3.select('#sites-file').on('change', onSitesFileChange);

  var file = getFile();
  if (file) {
    loadFile(file);
  }

  function onSitesFileChange() {
    var file = this.files[0];
    loadFile(file);
  }

  function loadFile(file) {
    if (file && file.type.startsWith('application/json')) {
      let reader = new FileReader();
      reader.onload = passContentsToFlow;
      reader.readAsText(file);
    }
  }

  function passContentsToFlow(e) {
    var sites;
    try {
      sites = JSON.parse(e.target.result);
    } catch (error) {
      console.error(error);
      throw new Error('Could not read site file.');
    }
    if (sites) {
      onLoadSites({ sites });
    }
  }

  function onSave() {
    var sites = [];
    var siteItems = document.querySelectorAll('#site-root .site');
    for (var i = 0; i < siteItems.length; ++i) {
      sites.push(objectFromDOM(siteItems[i]));
    }
    onSaveSites({ sites });
  }
}

function getFile() {
  var files = document.getElementById('sites-file').files;

  var file;
  if (files.length > 0) {
    file = files[0];
  }
  return file;
}

module.exports = wireControls;
