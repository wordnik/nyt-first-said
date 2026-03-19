var d3 = require('d3-selection');
var listenersInit = false;

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
    onSaveSites();
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
