#!/usr/bin/env node
/* global __dirname */

var fs = require('fs');

const targetSitesPath = __dirname + '/../../data/target_sites.json';

var targetSitesObject = JSON.parse(
  fs.readFileSync(targetSitesPath, { encoding: 'utf8' })
);

var duplicatesFound = 0;
var msnSitesFound = 0;
var seenURLs = [];

for (let key in targetSitesObject) {
  let siteObj = targetSitesObject[key];
  if (siteObj.feeder_pages?.[0] === 'https://') {
    continue;
  }
  for (let url of siteObj.feeder_pages) {
    if (seenURLs.includes(url)) {
      console.log('Found duplicate:', siteObj);
      duplicatesFound += 1;
      delete targetSitesObject[key];
      continue;
    }
    if (key.endsWith('_on_msn_com')) {
      console.log('Found "on MSN.com site', siteObj);
      msnSitesFound += 1;
      delete targetSitesObject[key];
    }
    seenURLs = seenURLs.concat(siteObj.feeder_pages);
  }
}

fs.writeFileSync(targetSitesPath, JSON.stringify(targetSitesObject, null, 2), {
  encoding: 'utf8',
});

console.log(
  'Found',
  duplicatesFound,
  'duplicates and',
  msnSitesFound,
  '"on MSN.com sites.'
);
