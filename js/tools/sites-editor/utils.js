var of = require('object-form');
var objectFromDOM = of.ObjectFromDOM({});

function getSitesFromDOM() {
  var sites = [];
  var siteItems = document.querySelectorAll('#site-root .site');
  for (var i = 0; i < siteItems.length; ++i) {
    sites.push(objectFromDOM(siteItems[i]));
  }
  return sites;
}

module.exports = { getSitesFromDOM };
